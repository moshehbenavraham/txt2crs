# SPDX-License-Identifier: MIT-0

"""Tests for explainable and deterministic evidence ranking."""

import pytest

from txt2crs.research.quality import (
    EVIDENCE_RUBRIC_VERSION,
    EvidenceCandidate,
    EvidenceSelectionError,
    rank_and_select_evidence,
    score_evidence,
)


def candidate(
    *,
    evidence_id: str,
    source_id: str,
    authority_tier: str,
    primary_source: bool,
    relevance: float = 0.9,
    freshness: float = 0.8,
    corroboration: float = 0.7,
    extraction_completeness: float = 1.0,
    conflict: bool = False,
) -> EvidenceCandidate:
    """Create one scored candidate while making test differences obvious."""

    return EvidenceCandidate.model_validate(
        {
            "evidence_id": evidence_id,
            "source_id": source_id,
            "authority_tier": authority_tier,
            "primary_source": primary_source,
            "relevance": relevance,
            "freshness": freshness,
            "corroboration": corroboration,
            "extraction_completeness": extraction_completeness,
            "conflict": conflict,
        }
    )


def test_score_records_a_versioned_explainable_breakdown() -> None:
    """Selection decisions retain their individual deterministic components."""

    score = score_evidence(
        candidate(
            evidence_id="ev-primary",
            source_id="src-primary",
            authority_tier="primary",
            primary_source=True,
        )
    )

    assert score.rubric_version == EVIDENCE_RUBRIC_VERSION
    assert score.total_score == pytest.approx(
        sum(score.components.model_dump().values())
    )
    assert score.components.authority > 0
    assert score.components.directness > 0


def test_authoritative_primary_evidence_ranks_before_community_content() -> None:
    """High relevance alone cannot make community content dominate."""

    primary = candidate(
        evidence_id="ev-primary",
        source_id="src-primary",
        authority_tier="primary",
        primary_source=True,
        relevance=0.8,
    )
    community = candidate(
        evidence_id="ev-community",
        source_id="src-community",
        authority_tier="community",
        primary_source=False,
        relevance=1.0,
    )

    selected = rank_and_select_evidence(
        [community, primary],
        maximum_evidence=2,
        maximum_community_evidence=1,
        maximum_per_source=2,
        high_risk_claim=False,
    )

    assert [item.candidate.evidence_id for item in selected] == [
        "ev-primary",
        "ev-community",
    ]


def test_stable_tie_breakers_do_not_depend_on_input_order() -> None:
    """Equal candidates sort by source ID and evidence ID deterministically."""

    first = candidate(
        evidence_id="ev-b",
        source_id="src-b",
        authority_tier="authoritative",
        primary_source=False,
    )
    second = candidate(
        evidence_id="ev-a",
        source_id="src-a",
        authority_tier="authoritative",
        primary_source=False,
    )

    forward = rank_and_select_evidence(
        [first, second],
        maximum_evidence=2,
        maximum_community_evidence=1,
        maximum_per_source=2,
        high_risk_claim=False,
    )
    backward = rank_and_select_evidence(
        [second, first],
        maximum_evidence=2,
        maximum_community_evidence=1,
        maximum_per_source=2,
        high_risk_claim=False,
    )

    assert [item.candidate.evidence_id for item in forward] == [
        item.candidate.evidence_id for item in backward
    ]
    assert forward[0].candidate.evidence_id == "ev-a"


def test_community_and_per_source_caps_preserve_diversity() -> None:
    """One weak or prolific source cannot fill the evidence window."""

    candidates = [
        candidate(
            evidence_id="ev-community-1",
            source_id="src-community",
            authority_tier="community",
            primary_source=False,
            relevance=1.0,
        ),
        candidate(
            evidence_id="ev-community-2",
            source_id="src-community-2",
            authority_tier="community",
            primary_source=False,
            relevance=0.99,
        ),
        candidate(
            evidence_id="ev-authority-1",
            source_id="src-authority",
            authority_tier="authoritative",
            primary_source=False,
            relevance=0.8,
        ),
        candidate(
            evidence_id="ev-authority-2",
            source_id="src-authority",
            authority_tier="authoritative",
            primary_source=False,
            relevance=0.79,
        ),
        candidate(
            evidence_id="ev-primary",
            source_id="src-primary",
            authority_tier="primary",
            primary_source=True,
            relevance=0.75,
        ),
    ]

    selected = rank_and_select_evidence(
        candidates,
        maximum_evidence=4,
        maximum_community_evidence=1,
        maximum_per_source=1,
        high_risk_claim=False,
    )

    assert sum(item.candidate.authority_tier == "community" for item in selected) == 1
    assert len({item.candidate.source_id for item in selected}) == len(selected)


def test_high_risk_selection_requires_authoritative_candidate() -> None:
    """A high-risk topic cannot proceed from community-only evidence."""

    with pytest.raises(EvidenceSelectionError, match="authoritative"):
        rank_and_select_evidence(
            [
                candidate(
                    evidence_id="ev-community",
                    source_id="src-community",
                    authority_tier="community",
                    primary_source=False,
                )
            ],
            maximum_evidence=2,
            maximum_community_evidence=1,
            maximum_per_source=1,
            high_risk_claim=True,
        )
