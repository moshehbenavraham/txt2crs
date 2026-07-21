# SPDX-License-Identifier: MIT-0

"""Coordinate research questions into one immutable evidence version."""

import re
from collections.abc import Callable
from datetime import datetime
from typing import Literal, Protocol
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from txt2crs.ai.runtime import CancellationToken
from txt2crs.domain.models import (
    EvidenceExcerpt,
    InputLocation,
    ResearchPlan,
    SourceRecord,
)
from txt2crs.research.evidence import EvidenceLedger, FrozenEvidenceSet, hash_text
from txt2crs.research.models import (
    ExtractRequest,
    ExtractResult,
    SearchRequest,
    SearchResult,
)
from txt2crs.research.quality import (
    EvidenceCandidate,
    EvidenceSelectionError,
    rank_and_select_evidence,
)

_PROMPT_INJECTION_PATTERN = re.compile(
    r"(?i)\b(?:ignore|disregard|override)\b.{0,80}"
    r"\b(?:instructions?|prompts?|rules?|system|developer)\b"
)
_CONFLICT_PATTERN = re.compile(
    # The final alternative is a deliberate stem for all supersede variants.
    # spellchecker:ignore-next-line
    r"(?i)\b(?:conflict|contradict|disagree|disputed|supersed)\w*\b"
)
_COMMUNITY_DOMAINS = frozenset(
    {
        "reddit.com",
        "stackexchange.com",
        "stackoverflow.com",
        "superuser.com",
        "youtube.com",
        "youtu.be",
    }
)
_STANDARDS_DOMAINS = frozenset({"ietf.org", "rfc-editor.org", "w3.org", "iso.org"})
_ACADEMIC_DOMAINS = frozenset({"arxiv.org"})
_EDUCATION_RESEARCH_PATTERN = re.compile(
    r"(?i)\b(?:assessment design|cognitive load|education research|"
    r"instructional design|learning objectives?|pedagog\w*|retrieval practice|"
    r"teaching methods?)\b"
)
_TRACKING_QUERY_KEYS = frozenset(
    {
        "fbclid",
        "gclid",
        "mc_cid",
        "mc_eid",
        "ref",
        "source",
    }
)


class ResearchTools(Protocol):
    """Search/extract surface supplied by the budgeted research service."""

    def search(self, request: SearchRequest) -> SearchResult:
        """Search reviewed public sources."""

    def extract(self, request: ExtractRequest) -> ExtractResult:
        """Extract reviewed public documents."""


class ResearchCoordinatorService:
    """Search, extract, classify, segment, hash, and freeze research."""

    def __init__(
        self,
        *,
        tools: ResearchTools,
        clock: Callable[[], datetime],
        primary_domains: set[str],
    ) -> None:
        self._tools = tools
        self._clock = clock
        self._primary_domains = {
            domain.casefold().rstrip(".") for domain in primary_domains
        }

    def collect(
        self,
        research_plan: ResearchPlan,
        cancellation: CancellationToken,
        *,
        high_risk_course: bool,
    ) -> FrozenEvidenceSet:
        """Collect at most the plan's maximum unique public sources."""

        ledger = EvidenceLedger()
        attempted_urls: set[str] = set()
        collected_urls: set[str] = set()
        collected_excerpt_texts: list[str] = []
        candidate_records: dict[
            str,
            tuple[SourceRecord, EvidenceExcerpt, EvidenceCandidate],
        ] = {}
        for question_index, question in enumerate(research_plan.questions):
            cancellation.raise_if_cancelled()
            # Only successfully extracted, unique candidates consume the
            # evidence allowance. Failed provider documents remain bounded by
            # the separate search/extract call budget and cannot starve later
            # research questions of their source opportunity.
            remaining_sources = research_plan.maximum_sources - len(candidate_records)
            if remaining_sources <= 0:
                break
            remaining_questions = len(research_plan.questions) - question_index
            per_question_source_limit = max(
                1,
                (remaining_sources + remaining_questions - 1) // remaining_questions,
            )
            search_result = self._tools.search(
                SearchRequest(
                    query=_build_search_query(
                        question=question.question,
                        preferred_source_types=question.preferred_source_types,
                        primary_domains=self._primary_domains,
                    ),
                    maximum_results=min(
                        10,
                        remaining_sources,
                        per_question_source_limit,
                    ),
                )
            )
            candidate_hits = []
            candidate_urls: set[str] = set()
            for search_hit in search_result.hits:
                canonical_url = _canonicalize_url(search_hit.url)
                if canonical_url in attempted_urls or canonical_url in candidate_urls:
                    continue
                candidate_hits.append(search_hit)
                candidate_urls.add(canonical_url)
                if len(candidate_hits) >= remaining_sources:
                    break
            if not candidate_hits:
                continue
            attempted_urls.update(candidate_urls)

            extraction_result = self._tools.extract(
                ExtractRequest(urls=[hit.url for hit in candidate_hits])
            )
            hit_by_url = {hit.url: hit for hit in candidate_hits}
            for document in extraction_result.documents:
                cancellation.raise_if_cancelled()
                canonical_url = _canonicalize_url(document.url)
                if canonical_url in collected_urls:
                    continue
                # The EvidenceExcerpt model trims outer whitespace. Normalize
                # before deriving both its stable ID and hash so a 20,000
                # character cutoff that lands on a space cannot make the
                # validated model differ from the bytes we hashed.
                excerpt_text = document.content[:20_000].strip()
                if _is_semantic_duplicate(
                    excerpt_text=excerpt_text,
                    collected_excerpt_texts=collected_excerpt_texts,
                ):
                    collected_urls.add(canonical_url)
                    continue
                source_id = _stable_identifier("src", canonical_url)
                evidence_id = _stable_identifier(
                    "ev",
                    f"{source_id}\n{excerpt_text}",
                )
                hostname = (urlsplit(document.url).hostname or "").casefold()
                source_type, authority_tier = _classify_source(
                    hostname=hostname,
                    primary_domains=self._primary_domains,
                )
                is_primary = authority_tier == "primary"
                source = SourceRecord(
                    schema_version="1.0",
                    source_id=source_id,
                    canonical_url=canonical_url,
                    title=(
                        hit_by_url[document.url].title
                        if document.url in hit_by_url
                        else document.title
                    ),
                    publisher_or_author=hostname or "Unknown publisher",
                    publication_date=None,
                    retrieved_at=self._clock(),
                    content_hash=hash_text(document.content),
                    source_type=source_type,
                    authority_tier=authority_tier,
                    language="en",
                )
                excerpt = EvidenceExcerpt(
                    schema_version="1.0",
                    evidence_id=evidence_id,
                    source_id=source_id,
                    excerpt=excerpt_text,
                    location=InputLocation(label=document.url),
                    content_hash=hash_text(excerpt_text),
                    retrieval_method="web_extract",
                    prompt_injection_warning=(
                        _PROMPT_INJECTION_PATTERN.search(excerpt_text) is not None
                    ),
                )
                matched_search_hit = hit_by_url.get(document.url)
                quality_candidate = EvidenceCandidate(
                    evidence_id=evidence_id,
                    source_id=source_id,
                    authority_tier=source.authority_tier,
                    primary_source=is_primary,
                    relevance=(
                        matched_search_hit.relevance_score
                        if matched_search_hit is not None
                        else 0.0
                    ),
                    # Publication dates are not supplied by the current
                    # provider contract. A neutral value remains explicit in
                    # the retained component breakdown instead of inventing
                    # freshness.
                    freshness=0.5,
                    corroboration=0.0,
                    extraction_completeness=min(
                        1.0,
                        len(excerpt_text) / max(1, len(document.content)),
                    ),
                    conflict=_CONFLICT_PATTERN.search(excerpt_text) is not None,
                )
                candidate_records[evidence_id] = (
                    source,
                    excerpt,
                    quality_candidate,
                )
                collected_urls.add(canonical_url)
                collected_excerpt_texts.append(excerpt_text)
                if len(candidate_records) >= research_plan.maximum_sources:
                    break

        selected_scores = rank_and_select_evidence(
            [
                quality_candidate
                for _source, _excerpt, quality_candidate in candidate_records.values()
            ],
            maximum_evidence=research_plan.maximum_sources,
            maximum_community_evidence=min(1, research_plan.maximum_sources),
            maximum_per_source=1,
            high_risk_claim=high_risk_course,
        )
        validate_evidence_requirements(
            research_plan=research_plan,
            selected_candidates=[score.candidate for score in selected_scores],
            education_evidence_ids={
                evidence_id
                for evidence_id, (
                    source,
                    excerpt,
                    _candidate,
                ) in candidate_records.items()
                if _is_education_research(
                    source_title=source.title,
                    excerpt_text=excerpt.excerpt,
                )
            },
        )
        for scored_evidence in selected_scores:
            source, excerpt, _quality_candidate = candidate_records[
                scored_evidence.candidate.evidence_id
            ]
            ledger.add_source(source)
            ledger.add_excerpt(excerpt)
        return ledger.freeze(selection_scores=selected_scores)


def validate_evidence_requirements(
    *,
    research_plan: ResearchPlan,
    selected_candidates: list[EvidenceCandidate],
    education_evidence_ids: set[str],
) -> None:
    """Prove a frozen selection meets the plan, not merely its numeric cap."""

    authoritative_count = sum(
        candidate.authority_tier in {"primary", "authoritative"}
        for candidate in selected_candidates
    )
    if authoritative_count < research_plan.minimum_authoritative_sources:
        raise EvidenceSelectionError(
            "Research plan requires more authoritative evidence."
        )
    education_count = sum(
        candidate.evidence_id in education_evidence_ids
        for candidate in selected_candidates
    )
    if education_count < research_plan.minimum_education_sources:
        raise EvidenceSelectionError(
            "Research plan requires more education or assessment evidence."
        )


def validate_frozen_evidence_requirements(
    *,
    research_plan: ResearchPlan,
    evidence_set: FrozenEvidenceSet,
) -> None:
    """Recheck durable evidence when a pipeline resumes from a checkpoint."""

    authoritative_count = sum(
        source.authority_tier in {"primary", "authoritative"}
        for source in evidence_set.sources
    )
    if authoritative_count < research_plan.minimum_authoritative_sources:
        raise EvidenceSelectionError(
            "Research plan requires more authoritative evidence."
        )
    source_by_id = {source.source_id: source for source in evidence_set.sources}
    education_count = sum(
        _is_education_research(
            source_title=source_by_id[excerpt.source_id].title,
            excerpt_text=excerpt.excerpt,
        )
        for excerpt in evidence_set.excerpts
    )
    if education_count < research_plan.minimum_education_sources:
        raise EvidenceSelectionError(
            "Research plan requires more education or assessment evidence."
        )


def _build_search_query(
    *,
    question: str,
    preferred_source_types: list[str],
    primary_domains: set[str],
) -> str:
    """Keep plan authority preferences visible to the search provider."""

    source_types = ", ".join(preferred_source_types)
    normalized_research_request = " ".join(
        [question, *preferred_source_types]
    ).casefold()
    relevant_domains = [
        domain
        for domain in sorted(primary_domains)
        if any(
            domain_term in normalized_research_request
            for domain_term in re.findall(r"[a-z0-9]+", domain.casefold())
            if domain_term not in {"com", "docs", "edu", "gov", "net", "org"}
            and len(domain_term) >= 4
        )
    ]
    authority_hint = (
        f" Reviewed authoritative domains: {', '.join(relevant_domains)}."
        if relevant_domains
        else ""
    )
    return f"{question} Preferred source types: {source_types}.{authority_hint}"


def _canonicalize_url(url: str) -> str:
    """Remove fragments and tracking noise before URL identity checks."""

    parsed_url = urlsplit(url)
    hostname = (parsed_url.hostname or "").casefold()
    if hostname.startswith("www."):
        hostname = hostname[4:]
    port = parsed_url.port
    netloc = hostname
    if port is not None and not (
        (parsed_url.scheme.casefold() == "http" and port == 80)
        or (parsed_url.scheme.casefold() == "https" and port == 443)
    ):
        netloc = f"{hostname}:{port}"
    retained_query = [
        (key, value)
        for key, value in parse_qsl(parsed_url.query, keep_blank_values=True)
        if key.casefold() not in _TRACKING_QUERY_KEYS
        and not key.casefold().startswith("utm_")
    ]
    normalized_path = parsed_url.path.rstrip("/") or "/"
    return urlunsplit(
        (
            parsed_url.scheme.casefold(),
            netloc,
            normalized_path,
            urlencode(sorted(retained_query)),
            "",
        )
    )


def _is_semantic_duplicate(
    *,
    excerpt_text: str,
    collected_excerpt_texts: list[str],
) -> bool:
    """Reject exact and near-mirror article text across different URLs."""

    candidate_terms = set(re.findall(r"[a-z0-9]+", excerpt_text.casefold()))
    for collected_text in collected_excerpt_texts:
        if excerpt_text == collected_text:
            return True
        collected_terms = set(re.findall(r"[a-z0-9]+", collected_text.casefold()))
        union = candidate_terms | collected_terms
        if union and len(candidate_terms & collected_terms) / len(union) >= 0.92:
            return True
    return False


def _is_education_research(*, source_title: str, excerpt_text: str) -> bool:
    """Classify pedagogy evidence without changing persisted score contracts."""

    return (
        _EDUCATION_RESEARCH_PATTERN.search(f"{source_title}\n{excerpt_text}")
        is not None
    )


def _classify_source(
    *,
    hostname: str,
    primary_domains: set[str],
) -> tuple[
    Literal[
        "official_documentation",
        "government",
        "academic",
        "standards_body",
        "reputable_secondary",
        "community",
        "user_input",
    ],
    Literal["primary", "authoritative", "secondary", "community"],
]:
    """Map reviewed domain evidence to honest source and authority labels."""

    normalized_hostname = hostname.removeprefix("www.").rstrip(".")
    if _domain_matches(normalized_hostname, _COMMUNITY_DOMAINS):
        return "community", "community"
    if _domain_matches(normalized_hostname, primary_domains):
        return "official_documentation", "primary"
    if normalized_hostname.endswith(".gov"):
        return "government", "authoritative"
    if _domain_matches(normalized_hostname, _STANDARDS_DOMAINS):
        return "standards_body", "authoritative"
    if normalized_hostname.endswith(".edu") or _domain_matches(
        normalized_hostname,
        _ACADEMIC_DOMAINS,
    ):
        return "academic", "authoritative"
    return "reputable_secondary", "secondary"


def _domain_matches(hostname: str, domains: set[str] | frozenset[str]) -> bool:
    """Accept a reviewed domain and its subdomains without suffix confusion."""

    return any(
        hostname == domain or hostname.endswith(f".{domain}") for domain in domains
    )


def _stable_identifier(prefix: str, value: str) -> str:
    """Derive compact stable IDs from canonical source material."""

    return f"{prefix}-{hash_text(value).removeprefix('sha256:')[:24]}"
