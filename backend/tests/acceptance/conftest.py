"""Reusable credential-free durable application fixtures for Phase 03."""

from dataclasses import dataclass
from pathlib import Path

import pytest
from txt2crs.application import (
    ApplicationAdmissionConfig,
    ApplicationStorageConfig,
    DeterministicApplicationConfig,
    DeterministicApplicationFactory,
    DeterministicGenerationScenario,
    DeterministicTurn,
    Txt2CrsApplication,
)
from txt2crs.jobs import (
    CurriculumShapeLimits,
    ExecutionProfile,
    GenerationRequest,
    InputExecutionLimits,
    InputPayload,
    LearnerAgeGroup,
    LearningPreferenceDefaults,
    LearningPreferenceIntent,
    RequestRetryPolicy,
    RunExecutionLimits,
)


@dataclass(frozen=True, slots=True)
class DurableSubmissionHarness:
    """Open production SQLite composition with a deterministic provider graph."""

    state_directory: Path
    execution_profile: ExecutionProfile
    scenario: DeterministicGenerationScenario

    def open(
        self,
        *,
        maximum_jobs_per_user: int = 10,
        maximum_jobs_global: int = 100,
    ) -> Txt2CrsApplication:
        """Open or reopen the same exact durable state directory."""

        return DeterministicApplicationFactory(
            DeterministicApplicationConfig(
                storage=ApplicationStorageConfig(
                    state_directory=self.state_directory,
                    maximum_artifact_job_bytes=20_000_000,
                    artifact_retention_days=30,
                ),
                admission=ApplicationAdmissionConfig(
                    window_seconds=3_600,
                    maximum_jobs_per_user=maximum_jobs_per_user,
                    maximum_jobs_global=maximum_jobs_global,
                    maximum_reserved_tokens_per_user=7_500_000,
                    maximum_reserved_tokens_global=75_000_000,
                    maximum_research_cost_microusd_per_user=10_000_000,
                    maximum_research_cost_microusd_global=100_000_000,
                ),
                default_execution_profile=self.execution_profile,
                scenario=self.scenario,
            )
        ).create()

    def request(
        self,
        *,
        value: str = "Teach relational database indexes.",
        provider_consent: bool = True,
        learner_age_group: LearnerAgeGroup = LearnerAgeGroup.adult,
    ) -> GenerationRequest:
        """Build one exact canonical request aligned with the factory profile."""

        return GenerationRequest.create(
            schema_version="1.0",
            request_version="generation-request-v1",
            input_payload=InputPayload(
                input_type="prompt",
                value=value,
                media_type="text/plain",
                file_name=None,
                metadata={"input_mode": "prompt"},
            ),
            preferences=LearningPreferenceIntent(
                audience=None,
                prior_knowledge=None,
                learning_goals=("Explain index lookup.",),
                level="auto",
                language="auto",
            ),
            provider_consent=provider_consent,
            learner_age_group=learner_age_group,
            policy_flags=(),
            execution_profile=self.execution_profile,
        )


def _execution_profile() -> ExecutionProfile:
    """Return the finite P0-like profile frozen into every acceptance request."""

    return ExecutionProfile(
        schema_version="1.0",
        engine_version="txt2crs-0.6.0",
        prompt_version="course-pipeline-v1",
        policy_version="content-policy-v1",
        model_id="gpt-5.6",
        reasoning_effort="high",
        retry_policy=RequestRetryPolicy(
            maximum_attempts=3,
            base_seconds=1.0,
            maximum_seconds=15.0,
            jitter_ratio=0.2,
        ),
        input_limits=InputExecutionLimits(
            maximum_input_bytes=20_971_520,
            maximum_metadata_bytes=262_144,
            maximum_normalized_characters=200_000,
            maximum_pdf_pages=200,
        ),
        run_limits=RunExecutionLimits(
            maximum_turns=20,
            maximum_research_calls=12,
            maximum_search_calls=6,
            maximum_extract_calls=6,
            maximum_sources=12,
            maximum_extracted_bytes=2_000_000,
            maximum_input_tokens=600_000,
            maximum_output_tokens=150_000,
            maximum_retries=3,
            maximum_repairs=3,
            maximum_elapsed_seconds=2_700,
        ),
        preference_defaults=LearningPreferenceDefaults(),
        curriculum_shape_limits=CurriculumShapeLimits(),
    )


def _scenario() -> DeterministicGenerationScenario:
    """Return a strict scenario that is never consumed by submission tests."""

    return DeterministicGenerationScenario.create(
        model_id="gpt-5.6",
        turns=(
            DeterministicTurn.create(
                stage="plan_research",
                output={"schema_version": "1.0"},
            ),
        ),
        evidence_set={
            "schema_version": "1.0",
            "evidence_version": "sha256:" + ("0" * 64),
            "sources": [],
            "excerpts": [],
            "selection_scores": [],
        },
    )


@pytest.fixture()
def durable_submission_harness(tmp_path: Path) -> DurableSubmissionHarness:
    """Provide isolated durable state for one acceptance test."""

    return DurableSubmissionHarness(
        state_directory=(tmp_path / "state").resolve(),
        execution_profile=_execution_profile(),
        scenario=_scenario(),
    )
