# SPDX-License-Identifier: MIT-0

"""Explainable, versioned evidence scoring and deterministic selection."""

from typing import Literal

from pydantic import Field

from txt2crs.domain.models import Identifier, StrictContract

EVIDENCE_RUBRIC_VERSION: Literal["education-evidence-v1"] = "education-evidence-v1"

AuthorityTier = Literal["primary", "authoritative", "secondary", "community"]


class EvidenceCandidate(StrictContract):
    """Deterministic quality inputs for one evidence excerpt."""

    evidence_id: Identifier
    source_id: Identifier
    authority_tier: AuthorityTier
    primary_source: bool
    relevance: float = Field(ge=0, le=1)
    freshness: float = Field(ge=0, le=1)
    corroboration: float = Field(ge=0, le=1)
    extraction_completeness: float = Field(ge=0, le=1)
    conflict: bool


class EvidenceScoreComponents(StrictContract):
    """Weighted contributions retained with a selection decision."""

    authority: float
    directness: float
    relevance: float
    freshness: float
    corroboration: float
    extraction_completeness: float
    conflict_penalty: float


class ScoredEvidence(StrictContract):
    """Candidate plus rubric version, components, and total."""

    rubric_version: Literal["education-evidence-v1"]
    candidate: EvidenceCandidate
    components: EvidenceScoreComponents
    total_score: float


class EvidenceSelectionError(ValueError):
    """Raised when policy cannot construct an acceptable evidence window."""


_AUTHORITY_WEIGHTS: dict[AuthorityTier, float] = {
    "primary": 0.30,
    "authoritative": 0.26,
    "secondary": 0.16,
    "community": 0.05,
}


def score_evidence(candidate: EvidenceCandidate) -> ScoredEvidence:
    """Calculate one transparent education-oriented quality score."""

    components = EvidenceScoreComponents(
        authority=_AUTHORITY_WEIGHTS[candidate.authority_tier],
        directness=0.15 if candidate.primary_source else 0.08,
        relevance=0.25 * candidate.relevance,
        freshness=0.10 * candidate.freshness,
        corroboration=0.10 * candidate.corroboration,
        extraction_completeness=0.10 * candidate.extraction_completeness,
        conflict_penalty=-0.25 if candidate.conflict else 0.0,
    )
    return ScoredEvidence(
        rubric_version=EVIDENCE_RUBRIC_VERSION,
        candidate=candidate,
        components=components,
        total_score=sum(components.model_dump().values()),
    )


def rank_and_select_evidence(
    candidates: list[EvidenceCandidate],
    *,
    maximum_evidence: int,
    maximum_community_evidence: int,
    maximum_per_source: int,
    high_risk_claim: bool,
) -> list[ScoredEvidence]:
    """Select stable, diverse evidence while enforcing authority caps."""

    if maximum_evidence < 1:
        raise ValueError("maximum_evidence must be positive")
    if maximum_community_evidence < 0:
        raise ValueError("maximum_community_evidence cannot be negative")
    if maximum_per_source < 1:
        raise ValueError("maximum_per_source must be positive")

    scored_candidates = [score_evidence(candidate) for candidate in candidates]
    scored_candidates.sort(
        key=lambda item: (
            -item.total_score,
            -item.candidate.relevance,
            -item.candidate.freshness,
            item.candidate.source_id,
            item.candidate.evidence_id,
        )
    )

    selected: list[ScoredEvidence] = []
    per_source_counts: dict[str, int] = {}
    community_count = 0
    for scored_candidate in scored_candidates:
        candidate = scored_candidate.candidate
        if (
            candidate.authority_tier == "community"
            and community_count >= maximum_community_evidence
        ):
            continue
        if per_source_counts.get(candidate.source_id, 0) >= maximum_per_source:
            continue

        selected.append(scored_candidate)
        per_source_counts[candidate.source_id] = (
            per_source_counts.get(candidate.source_id, 0) + 1
        )
        if candidate.authority_tier == "community":
            community_count += 1
        if len(selected) >= maximum_evidence:
            break

    if high_risk_claim and not any(
        item.candidate.authority_tier in {"primary", "authoritative"}
        for item in selected
    ):
        raise EvidenceSelectionError("High-risk claims require authoritative evidence.")
    return selected
