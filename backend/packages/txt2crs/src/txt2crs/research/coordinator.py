# SPDX-License-Identifier: MIT-0

"""Coordinate research questions into one immutable evidence version."""

import re
from collections.abc import Callable
from datetime import datetime
from typing import Protocol
from urllib.parse import urlsplit

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
        candidate_records: dict[
            str,
            tuple[SourceRecord, EvidenceExcerpt, EvidenceCandidate],
        ] = {}
        for question in research_plan.questions:
            cancellation.raise_if_cancelled()
            # Search candidates consume the source allowance before provider
            # extraction. Tracking attempted URLs prevents a partial extract
            # from spending the same finite allowance again on later questions.
            remaining_sources = research_plan.maximum_sources - len(attempted_urls)
            if remaining_sources <= 0:
                break
            search_result = self._tools.search(
                SearchRequest(
                    query=question.question,
                    maximum_results=min(10, remaining_sources),
                )
            )
            candidate_hits = []
            candidate_urls: set[str] = set()
            for search_hit in search_result.hits:
                if search_hit.url in attempted_urls or search_hit.url in candidate_urls:
                    continue
                candidate_hits.append(search_hit)
                candidate_urls.add(search_hit.url)
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
                if document.url in collected_urls:
                    continue
                source_id = _stable_identifier("src", document.url)
                # The EvidenceExcerpt model trims outer whitespace. Normalize
                # before deriving both its stable ID and hash so a 20,000
                # character cutoff that lands on a space cannot make the
                # validated model differ from the bytes we hashed.
                excerpt_text = document.content[:20_000].strip()
                evidence_id = _stable_identifier(
                    "ev",
                    f"{source_id}\n{excerpt_text}",
                )
                hostname = (urlsplit(document.url).hostname or "").casefold()
                is_primary = hostname in self._primary_domains
                source = SourceRecord(
                    schema_version="1.0",
                    source_id=source_id,
                    canonical_url=document.url,
                    title=(
                        hit_by_url[document.url].title
                        if document.url in hit_by_url
                        else document.title
                    ),
                    publisher_or_author=hostname or "Unknown publisher",
                    publication_date=None,
                    retrieved_at=self._clock(),
                    content_hash=hash_text(document.content),
                    source_type=(
                        "official_documentation"
                        if is_primary
                        else "reputable_secondary"
                    ),
                    authority_tier="primary" if is_primary else "secondary",
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
                collected_urls.add(document.url)
                if len(candidate_records) >= research_plan.maximum_sources:
                    break

        selected_scores = rank_and_select_evidence(
            [
                quality_candidate
                for _source, _excerpt, quality_candidate in candidate_records.values()
            ],
            maximum_evidence=research_plan.maximum_sources,
            maximum_community_evidence=0,
            maximum_per_source=1,
            high_risk_claim=high_risk_course,
        )
        for scored_evidence in selected_scores:
            source, excerpt, _quality_candidate = candidate_records[
                scored_evidence.candidate.evidence_id
            ]
            ledger.add_source(source)
            ledger.add_excerpt(excerpt)
        return ledger.freeze(selection_scores=selected_scores)


def _stable_identifier(prefix: str, value: str) -> str:
    """Derive compact stable IDs from canonical source material."""

    return f"{prefix}-{hash_text(value).removeprefix('sha256:')[:24]}"
