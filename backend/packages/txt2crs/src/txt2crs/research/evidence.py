# SPDX-License-Identifier: MIT-0

"""Immutable evidence sets and deterministic citation acceptance."""

import json
import re
from hashlib import sha256
from html import escape

from pydantic import Field, model_validator

from txt2crs.domain.models import (
    ClaimCitation,
    EvidenceExcerpt,
    HashValue,
    SchemaVersion,
    SourceRecord,
    StrictContract,
)
from txt2crs.research.quality import ScoredEvidence

_GROUNDING_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "was",
        "were",
        "with",
    }
)


def hash_text(value: str) -> str:
    """Return the package's labeled SHA-256 spelling for UTF-8 text."""

    return f"sha256:{sha256(value.encode('utf-8')).hexdigest()}"


class CitationValidationError(ValueError):
    """Raised when evidence integrity or citation acceptance fails."""


class FrozenEvidenceSet(StrictContract):
    """Versioned, deterministically ordered evidence for one course version."""

    schema_version: SchemaVersion
    evidence_version: HashValue
    sources: list[SourceRecord] = Field(max_length=100)
    excerpts: list[EvidenceExcerpt] = Field(max_length=2_000)
    selection_scores: list[ScoredEvidence] = Field(
        default_factory=list,
        max_length=2_000,
    )

    @model_validator(mode="after")
    def validate_structure(self) -> "FrozenEvidenceSet":
        """Require unique IDs and resolvable source references."""

        source_ids = [source.source_id for source in self.sources]
        evidence_ids = [excerpt.evidence_id for excerpt in self.excerpts]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("duplicate source ID in evidence set")
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("duplicate evidence ID in evidence set")
        known_source_ids = set(source_ids)
        for excerpt in self.excerpts:
            if excerpt.source_id not in known_source_ids:
                raise ValueError(
                    f"evidence {excerpt.evidence_id} references an unknown source"
                )
        return self

    def verify_integrity(self) -> None:
        """Recompute hashes and the version before accepting any citation."""

        for excerpt in self.excerpts:
            if hash_text(excerpt.excerpt) != excerpt.content_hash:
                raise CitationValidationError(
                    f"Evidence {excerpt.evidence_id} failed its content hash check."
                )
        expected_version = _derive_evidence_version(
            self.sources,
            self.excerpts,
            self.selection_scores,
        )
        if expected_version != self.evidence_version:
            raise CitationValidationError(
                "The frozen evidence-set version does not match its contents."
            )

    def as_untrusted_prompt_data(self) -> str:
        """Render explicit data segments without granting instruction priority."""

        prompt_segments = []
        for excerpt in self.excerpts:
            warning = str(excerpt.prompt_injection_warning).casefold()
            prompt_segments.append(
                f'<untrusted_evidence evidence_id="{escape(excerpt.evidence_id)}" '
                f'source_id="{escape(excerpt.source_id)}" '
                f'prompt_injection_warning="{warning}">'
                f"{escape(excerpt.excerpt)}"
                "</untrusted_evidence>"
            )
        return "\n".join(prompt_segments)


class EvidenceLedger:
    """Collect validated source records and freeze them exactly once."""

    def __init__(self) -> None:
        self._sources: dict[str, SourceRecord] = {}
        self._excerpts: dict[str, EvidenceExcerpt] = {}
        self._frozen_set: FrozenEvidenceSet | None = None

    def _require_mutable(self) -> None:
        """Stop any write after an evidence version has been published."""

        if self._frozen_set is not None:
            raise RuntimeError("The evidence ledger is frozen.")

    def add_source(self, source: SourceRecord) -> None:
        """Add one immutable source record with a unique stable ID."""

        self._require_mutable()
        if source.source_id in self._sources:
            raise ValueError(f"duplicate source ID: {source.source_id}")
        self._sources[source.source_id] = source

    def add_excerpt(self, excerpt: EvidenceExcerpt) -> None:
        """Add exact evidence only after its source and hash are valid."""

        self._require_mutable()
        if excerpt.source_id not in self._sources:
            raise ValueError(f"unknown source ID: {excerpt.source_id}")
        if excerpt.evidence_id in self._excerpts:
            raise ValueError(f"duplicate evidence ID: {excerpt.evidence_id}")
        if hash_text(excerpt.excerpt) != excerpt.content_hash:
            raise ValueError(f"evidence hash mismatch: {excerpt.evidence_id}")
        self._excerpts[excerpt.evidence_id] = excerpt

    def freeze(
        self,
        *,
        selection_scores: list[ScoredEvidence] | None = None,
    ) -> FrozenEvidenceSet:
        """Return the same deterministic evidence version on every later call."""

        if self._frozen_set is None:
            sources = sorted(self._sources.values(), key=lambda item: item.source_id)
            excerpts = sorted(
                self._excerpts.values(),
                key=lambda item: item.evidence_id,
            )
            retained_scores = list(selection_scores or [])
            self._frozen_set = FrozenEvidenceSet(
                schema_version="1.0",
                evidence_version=_derive_evidence_version(
                    sources,
                    excerpts,
                    retained_scores,
                ),
                sources=sources,
                excerpts=excerpts,
                selection_scores=retained_scores,
            )
        return self._frozen_set


def validate_claim_citations(
    *,
    citations: list[ClaimCitation],
    evidence_set: FrozenEvidenceSet,
    unresolved_claims: list[str],
    high_risk_course: bool,
) -> None:
    """Apply deterministic existence, hash, disclosure, and authority gates."""

    evidence_set.verify_integrity()
    source_by_id = {source.source_id: source for source in evidence_set.sources}
    excerpt_by_id = {excerpt.evidence_id: excerpt for excerpt in evidence_set.excerpts}
    disclosed_claims = {
        " ".join(unresolved_claim.casefold().split())
        for unresolved_claim in unresolved_claims
    }
    citation_ids = [citation.citation_id for citation in citations]
    if len(citation_ids) != len(set(citation_ids)):
        raise CitationValidationError("Citation IDs must be unique.")

    for citation in citations:
        if hash_text(citation.claim_text) != citation.claim_hash:
            raise CitationValidationError(
                f"Citation {citation.citation_id} failed its claim hash check."
            )
        missing_evidence_ids = [
            evidence_id
            for evidence_id in citation.evidence_ids
            if evidence_id not in excerpt_by_id
        ]
        if missing_evidence_ids:
            raise CitationValidationError(
                f"Citation {citation.citation_id} references missing evidence "
                f"{missing_evidence_ids[0]}."
            )
        if citation.support_verdict in {"unsupported", "partial"}:
            raise CitationValidationError(
                f"Citation {citation.citation_id} is unsupported."
            )
        supporting_excerpt_text = " ".join(
            excerpt_by_id[evidence_id].excerpt for evidence_id in citation.evidence_ids
        )
        if not has_minimum_text_support(
            claim_text=citation.claim_text,
            evidence_text=supporting_excerpt_text,
            high_risk_course=high_risk_course,
        ):
            raise CitationValidationError(
                f"Citation {citation.citation_id} lacks independent text support."
            )
        if citation.support_verdict == "conflicting":
            normalized_claim = " ".join(citation.claim_text.casefold().split())
            if normalized_claim not in disclosed_claims:
                raise CitationValidationError(
                    f"Conflicting citation {citation.citation_id} is not disclosed."
                )
        if high_risk_course:
            supporting_sources = [
                source_by_id[excerpt_by_id[evidence_id].source_id]
                for evidence_id in citation.evidence_ids
            ]
            if not any(
                source.authority_tier in {"primary", "authoritative"}
                for source in supporting_sources
            ):
                raise CitationValidationError(
                    f"Citation {citation.citation_id} lacks authoritative evidence."
                )


def has_minimum_text_support(
    *,
    claim_text: str,
    evidence_text: str,
    high_risk_course: bool,
) -> bool:
    """Reject unrelated evidence before trusting a semantic verdict.

    This deliberately conservative check is not presented as full natural
    language entailment. It proves that a claimed support verdict is at least
    grounded in overlapping substantive evidence terms. Higher-risk courses
    use a stricter overlap threshold in addition to their authority gate.
    """

    claim_terms = _significant_terms(claim_text)
    evidence_terms = _significant_terms(evidence_text)
    if not claim_terms:
        return False
    overlap_count = len(claim_terms & evidence_terms)
    minimum_overlap_count = 1 if len(claim_terms) == 1 else 2
    minimum_ratio = 0.7 if high_risk_course else 0.5
    return (
        overlap_count >= minimum_overlap_count
        and overlap_count / len(claim_terms) >= minimum_ratio
    )


def _significant_terms(text: str) -> set[str]:
    """Return simple Unicode-aware content terms with light suffix folding."""

    raw_terms = re.findall(r"[^\W_]+", text.casefold(), flags=re.UNICODE)
    return {
        _fold_suffix(term)
        for term in raw_terms
        if len(term) >= 2 and term not in _GROUNDING_STOP_WORDS
    }


def _fold_suffix(term: str) -> str:
    """Fold common English inflections without an NLP runtime dependency."""

    if len(term) > 4 and term.endswith("ies"):
        return f"{term[:-3]}y"
    for suffix in ("ing", "ed"):
        if len(term) > len(suffix) + 3 and term.endswith(suffix):
            return term[: -len(suffix)]
    if len(term) > 3 and term.endswith("s"):
        return term[:-1]
    return term


def _derive_evidence_version(
    sources: list[SourceRecord],
    excerpts: list[EvidenceExcerpt],
    selection_scores: list[ScoredEvidence],
) -> str:
    """Hash canonical JSON so ordering never changes evidence identity."""

    canonical_payload = {
        "sources": [
            source.model_dump(mode="json")
            for source in sorted(sources, key=lambda item: item.source_id)
        ],
        "excerpts": [
            excerpt.model_dump(mode="json")
            for excerpt in sorted(excerpts, key=lambda item: item.evidence_id)
        ],
        "selection_scores": [
            scored_evidence.model_dump(mode="json")
            for scored_evidence in selection_scores
        ],
    }
    canonical_json = json.dumps(
        canonical_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hash_text(canonical_json)
