# SPDX-License-Identifier: MIT-0

"""Fixed evaluation cases covering content, safety, and runtime failure modes."""

from dataclasses import dataclass
from hashlib import sha256
from importlib.resources import files
from typing import Literal

from txt2crs.evals.models import EvaluationCase

EvaluationCategory = Literal[
    "short_prompt",
    "long_transcript",
    "malformed_input",
    "noisy_extraction",
    "conflicting_evidence",
    "prompt_injection",
    "inaccessible_source",
    "multilingual_rtl",
    "specialist_high_risk",
    "quota_exhaustion",
    "cancellation",
    "invalid_schema",
    "citation_failure",
]


@dataclass(frozen=True, slots=True)
class _CaseDefinition:
    """Human-reviewed metadata for one packaged private fixture."""

    case_id: str
    category: EvaluationCategory
    fixture_name: str
    expected_invariants: tuple[str, ...]


_CASE_DEFINITIONS = (
    _CaseDefinition(
        case_id="eval-short-prompt",
        category="short_prompt",
        fixture_name="short_prompt.txt",
        expected_invariants=("complete_bundle", "grounded_claims"),
    ),
    _CaseDefinition(
        case_id="eval-long-transcript",
        category="long_transcript",
        fixture_name="long_transcript.txt",
        expected_invariants=("bounded_input", "complete_bundle"),
    ),
    _CaseDefinition(
        case_id="eval-malformed-input",
        category="malformed_input",
        fixture_name="malformed_input.txt",
        expected_invariants=("explicit_rejection",),
    ),
    _CaseDefinition(
        case_id="eval-noisy-extraction",
        category="noisy_extraction",
        fixture_name="noisy_extraction.txt",
        expected_invariants=(
            "extraction_warning_visible",
            "no_silent_truncation",
        ),
    ),
    _CaseDefinition(
        case_id="eval-conflicting-evidence",
        category="conflicting_evidence",
        fixture_name="conflicting_evidence.txt",
        expected_invariants=("conflict_disclosed", "citations_resolve"),
    ),
    _CaseDefinition(
        case_id="eval-prompt-injection",
        category="prompt_injection",
        fixture_name="prompt_injection.txt",
        expected_invariants=("instructions_isolated", "no_secret_disclosure"),
    ),
    _CaseDefinition(
        case_id="eval-inaccessible-source",
        category="inaccessible_source",
        fixture_name="inaccessible_source.txt",
        expected_invariants=("ssrf_blocked", "partial_failure_visible"),
    ),
    _CaseDefinition(
        case_id="eval-multilingual-rtl",
        category="multilingual_rtl",
        fixture_name="multilingual_rtl.txt",
        expected_invariants=("requested_locale", "rtl_accessibility"),
    ),
    _CaseDefinition(
        case_id="eval-specialist-high-risk",
        category="specialist_high_risk",
        fixture_name="specialist_high_risk.txt",
        expected_invariants=("high_risk_gate", "authoritative_sources"),
    ),
    _CaseDefinition(
        case_id="eval-quota-exhaustion",
        category="quota_exhaustion",
        fixture_name="quota_exhaustion.txt",
        expected_invariants=("quota_state_truthful", "no_partial_delivery"),
    ),
    _CaseDefinition(
        case_id="eval-cancellation",
        category="cancellation",
        fixture_name="cancellation.txt",
        expected_invariants=("terminal_cancelled", "active_turn_interrupted"),
    ),
    _CaseDefinition(
        case_id="eval-invalid-schema",
        category="invalid_schema",
        fixture_name="invalid_schema.txt",
        expected_invariants=("local_validation_rejects", "no_checkpoint"),
    ),
    _CaseDefinition(
        case_id="eval-citation-failure",
        category="citation_failure",
        fixture_name="citation_failure.txt",
        expected_invariants=("unsupported_claim_rejected", "no_partial_delivery"),
    ),
)


def built_in_evaluation_cases() -> tuple[EvaluationCase, ...]:
    """Load the stable case catalog and hash the exact packaged fixture bytes."""

    fixture_root = files("txt2crs.evals").joinpath("fixtures")
    evaluation_cases: list[EvaluationCase] = []
    for definition in _CASE_DEFINITIONS:
        fixture_bytes = fixture_root.joinpath(definition.fixture_name).read_bytes()
        evaluation_cases.append(
            EvaluationCase(
                schema_version="1.0",
                case_id=definition.case_id,
                case_version="eval-v1",
                category=definition.category,
                input_hash=f"sha256:{sha256(fixture_bytes).hexdigest()}",
                expected_invariants=list(definition.expected_invariants),
                private_input_reference=(
                    f"package://txt2crs.evals/fixtures/{definition.fixture_name}"
                ),
            )
        )
    return tuple(evaluation_cases)
