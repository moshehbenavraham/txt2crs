# SPDX-License-Identifier: MIT-0

"""Explicit live proofs for the ChatGPT subscription and complete application."""

import os
import re
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
from time import monotonic, sleep
from typing import Literal

import pytest
from pydantic import SecretStr

from txt2crs import __version__
from txt2crs.ai.codex_runtime import (
    CodexSubscriptionRuntime,
    OfficialCodexSdkAdapter,
    ResearchMcpConnection,
)
from txt2crs.ai.events import RuntimeEvent, RuntimeEventType
from txt2crs.ai.model_policy import DEFAULT_GPT56_MODEL_ID, Gpt56ModelPolicy
from txt2crs.ai.runtime import CancellationToken, TurnRequest
from txt2crs.ai.usage import BillingSource
from txt2crs.application import (
    ApplicationAdmissionConfig,
    ApplicationReadinessCheckState,
    ApplicationReadinessStatus,
    ApplicationStorageConfig,
    RealApplicationConfig,
    RealApplicationFactory,
)
from txt2crs.domain.models import StrictContract
from txt2crs.generation.pipeline import PipelineCheckpoint
from txt2crs.jobs import (
    CurriculumShapeLimits,
    ExecutionProfile,
    GenerationRequest,
    InputExecutionLimits,
    InputPayload,
    JobStatus,
    LearnerAgeGroup,
    LearningPreferenceDefaults,
    LearningPreferenceIntent,
    RequestRetryPolicy,
    RunExecutionLimits,
)
from txt2crs.research.managed_mcp import ManagedResearchMcpServer
from txt2crs.research.mcp_server import create_research_mcp_application
from txt2crs.research.models import (
    ExtractedDocument,
    ExtractRequest,
    ExtractResult,
    SearchHit,
    SearchRequest,
    SearchResult,
)

pytestmark = pytest.mark.live

_LIVE_COURSE_MODEL_ID = "gpt-5.6-sol"
_LIVE_COURSE_OWNER_ID = "live-proof-owner"
_LIVE_COURSE_IDEMPOTENCY_KEY = "release-candidate-live-course-v1"
_LIVE_COURSE_TIMEOUT_SECONDS = 2_700


class LiveProbeResult(StrictContract):
    """Small schema proving the model consumed the allowlisted tool result."""

    schema_version: Literal["1.0"]
    tool_used: Literal["research_search"]
    source_title: str


class DeterministicResearchService:
    """Serve public-shaped evidence without spending a research API quota."""

    def search(self, request: SearchRequest) -> SearchResult:
        """Return one unmistakable title for the live model to report."""

        return SearchResult(
            query=request.query,
            hits=[
                SearchHit(
                    title="TXT2CRS LIVE MCP PROBE SOURCE",
                    url="https://example.com/txt2crs-live-probe",
                    snippet="A deterministic subscription acceptance source.",
                    relevance_score=1.0,
                )
            ],
        )

    def extract(self, request: ExtractRequest) -> ExtractResult:
        """Support extraction if the model chooses the second allowed tool."""

        return ExtractResult(
            documents=[
                ExtractedDocument(
                    url=request.urls[0],
                    title="TXT2CRS LIVE MCP PROBE SOURCE",
                    content="This is deterministic acceptance evidence.",
                    content_bytes=42,
                )
            ],
            failed_urls=[],
        )


@pytest.mark.skipif(
    os.getenv("TXT2CRS_RUN_LIVE_CODEX") != "1",
    reason="Set TXT2CRS_RUN_LIVE_CODEX=1 for subscription acceptance.",
)
def test_live_chatgpt_turn_calls_allowlisted_research_tool(
    tmp_path: Path,
) -> None:
    """Verify the donor-independent subscription path against the real SDK."""

    model_policy = Gpt56ModelPolicy(
        configured_model_id=os.getenv(
            "TXT2CRS_MODEL_ID",
            DEFAULT_GPT56_MODEL_ID,
        )
    )
    research_application = create_research_mcp_application(
        DeterministicResearchService(),
        port=0,
    )
    emitted_events: list[RuntimeEvent] = []
    parent_environment = dict(os.environ)
    configured_codex_home = os.getenv("TXT2CRS_LIVE_CODEX_HOME")
    isolated_codex_home = (
        Path(configured_codex_home) if configured_codex_home else Path.home() / ".codex"
    )
    managed_research_mcp = ManagedResearchMcpServer(
        research_application,
        host="127.0.0.1",
        port=0,
    )
    with managed_research_mcp as ready_research_mcp:
        adapter = OfficialCodexSdkAdapter.create(
            worker_directory=tmp_path / "codex-worker",
            codex_home=isolated_codex_home,
            parent_environment=parent_environment,
            research_mcp=ResearchMcpConnection(
                url=ready_research_mcp.url,
            ),
            event_sink=emitted_events.append,
        )
        try:
            runtime = CodexSubscriptionRuntime(
                adapter=adapter,
                model_policy=model_policy,
            )
            assert runtime.inspect_readiness().model_entitled is True
            result = runtime.run_validated_turn(
                request=TurnRequest(
                    request_id="live-subscription-probe",
                    stage="live_research_probe",
                    model_id=model_policy.configured_model_id,
                    prompt_version="live-probe-v1",
                    trusted_instructions=(
                        "Call research_search exactly once with query "
                        "'txt2crs live probe'. Then return the required schema "
                        "with tool_used='research_search' and the exact source "
                        "title."
                    ),
                    untrusted_data='{"purpose":"subscription acceptance"}',
                    timeout_seconds=120,
                ),
                artifact_model=LiveProbeResult,
                cancellation=CancellationToken(),
            )
        finally:
            adapter.close()

    assert result.artifact.tool_used == "research_search"
    assert result.artifact.source_title == "TXT2CRS LIVE MCP PROBE SOURCE"
    assert result.usage.model_id == model_policy.configured_model_id
    assert result.usage.billing_source == "chatgpt_subscription"
    completed_tool_events = [
        event
        for event in emitted_events
        if event.event_type is RuntimeEventType.tool_completed
    ]
    assert len(completed_tool_events) == 1
    assert "research_search" in completed_tool_events[0].safe_message


def _live_course_execution_profile() -> ExecutionProfile:
    """Return one compact but complete profile for the release-candidate proof."""

    return ExecutionProfile(
        schema_version="1.0",
        engine_version=f"txt2crs-{__version__.replace('+', '.')}",
        prompt_version="course-pipeline-v1",
        policy_version="content-policy-v1",
        model_id=_LIVE_COURSE_MODEL_ID,
        reasoning_effort="high",
        retry_policy=RequestRetryPolicy(
            maximum_attempts=3,
            base_seconds=1,
            maximum_seconds=15,
            jitter_ratio=0.2,
        ),
        input_limits=InputExecutionLimits(
            maximum_input_bytes=20_971_520,
            maximum_metadata_bytes=262_144,
            maximum_normalized_characters=200_000,
            maximum_pdf_pages=200,
        ),
        run_limits=RunExecutionLimits(
            maximum_turns=16,
            maximum_research_calls=6,
            maximum_search_calls=3,
            maximum_extract_calls=3,
            maximum_sources=6,
            maximum_extracted_bytes=1_000_000,
            # Six schema-rich Sol turns cumulatively consume more than the
            # earlier 200k proof cap even for this compact course. Keep the
            # test finite while leaving enough headroom for the final
            # assessment turn after course/review context is supplied.
            maximum_input_tokens=300_000,
            maximum_output_tokens=60_000,
            maximum_retries=2,
            maximum_repairs=8,
            maximum_elapsed_seconds=_LIVE_COURSE_TIMEOUT_SECONDS,
        ),
        preference_defaults=LearningPreferenceDefaults(
            desired_depth="Compact, foundational-to-applied",
            # The live release proof deliberately requests a short lesson. Its
            # purpose is to exercise every real boundary without pretending a
            # compact one-module artifact represents an hour of instruction.
            duration_minutes=15,
            tone="Clear, rigorous, and encouraging",
            accessibility_requirements=(
                "Semantic headings",
                "Plain-language definitions",
                "Textual explanations of visual concepts",
            ),
            assessment_item_count=4,
            passing_percentage=70,
        ),
        curriculum_shape_limits=CurriculumShapeLimits(
            minimum_objectives=2,
            maximum_objectives=3,
            minimum_modules=1,
            maximum_modules=1,
            minimum_sections_per_module=2,
            maximum_sections_per_module=3,
            minimum_content_blocks_per_section=2,
            maximum_content_blocks_per_section=5,
        ),
    )


def _live_course_generation_request() -> GenerationRequest:
    """Build one synthetic topic with no personal or confidential information."""

    return GenerationRequest.create(
        schema_version="1.0",
        request_version="generation-request-v1",
        input_payload=InputPayload(
            input_type="prompt",
            value=(
                "Create a beginner course explaining how DNS resolution works "
                "during ordinary web browsing. Cover recursive resolvers, root "
                "and authoritative name servers, caching and TTLs, and safe "
                "practical troubleshooting. Use current public technical sources."
            ),
            media_type="text/plain",
            file_name=None,
            metadata={"source": "synthetic-release-proof"},
        ),
        preferences=LearningPreferenceIntent(
            audience="Adult learners with basic web-browsing experience",
            prior_knowledge="No networking administration experience required",
            learning_goals=(
                "Trace one domain-name lookup from browser to authoritative answer.",
                "Explain caching, TTLs, and a safe basic DNS troubleshooting process.",
            ),
            level="beginner",
            language="en",
        ),
        provider_consent=True,
        learner_age_group=LearnerAgeGroup.adult,
        policy_flags=("allow_external_research",),
        execution_profile=_live_course_execution_profile(),
    )


def _required_private_path(environment_name: str) -> Path:
    """Return one explicit absolute private path without printing its value."""

    configured_value = os.getenv(environment_name)
    if configured_value is None or not configured_value.strip():
        pytest.fail(f"{environment_name} is required for the full-course live proof.")
    configured_path = Path(configured_value).expanduser()
    if not configured_path.is_absolute():
        pytest.fail(f"{environment_name} must be an absolute path.")
    return configured_path.resolve()


@pytest.mark.skipif(
    os.getenv("TXT2CRS_RUN_LIVE_COURSE") != "1",
    reason="Set TXT2CRS_RUN_LIVE_COURSE=1 for the full-course live proof.",
)
def test_live_application_delivers_one_researched_course(
    tmp_path: Path,
) -> None:
    """Run one durable Sol/Tavily job and verify all public delivery contracts."""

    configured_tavily_api_key = os.getenv("TAVILY_API_KEY")
    if configured_tavily_api_key is None or not configured_tavily_api_key.strip():
        pytest.fail("TAVILY_API_KEY is required for the full-course live proof.")

    state_directory = _required_private_path("TXT2CRS_LIVE_STATE_ROOT")
    codex_home = _required_private_path("TXT2CRS_LIVE_CODEX_HOME")
    execution_profile = _live_course_execution_profile()
    application = RealApplicationFactory(
        RealApplicationConfig(
            storage=ApplicationStorageConfig(
                state_directory=state_directory,
                maximum_artifact_job_bytes=100_000_000,
                artifact_retention_days=30,
            ),
            admission=ApplicationAdmissionConfig(
                window_seconds=86_400,
                maximum_jobs_per_user=1,
                maximum_jobs_global=1,
                maximum_reserved_tokens_per_user=1_000_000,
                maximum_reserved_tokens_global=1_000_000,
                maximum_research_cost_microusd_per_user=2_000_000,
                maximum_research_cost_microusd_global=2_000_000,
            ),
            default_execution_profile=execution_profile,
            codex_home=codex_home,
            worker_directory=(tmp_path / "live-course-worker").resolve(),
            tavily_api_key=SecretStr(configured_tavily_api_key),
            managed_mcp_port=0,
            primary_research_domains=(
                "datatracker.ietf.org",
                "www.icann.org",
                "developers.cloudflare.com",
            ),
        )
    ).create()
    observed_checkpoints: list[tuple[int, str]] = []
    started_at = monotonic()

    try:
        readiness = application.inspect_application_readiness()
        assert readiness.status is ApplicationReadinessStatus.ready
        assert readiness.configured_model_id == _LIVE_COURSE_MODEL_ID
        assert all(
            check_state is ApplicationReadinessCheckState.ready
            for check_state in readiness.checks.model_dump(mode="python").values()
        )

        submitted_job = application.submit(
            user_id=_LIVE_COURSE_OWNER_ID,
            idempotency_key=_LIVE_COURSE_IDEMPOTENCY_KEY,
            generation_request=_live_course_generation_request(),
            admission_reservation=application.default_admission_reservation(),
        )
        with application.create_executor(
            job_id=submitted_job.job_id,
            user_id=_LIVE_COURSE_OWNER_ID,
        ) as course_executor:
            # Execution remains on one worker thread while the test observes
            # owner-authorized durable recovery snapshots through the facade.
            with ThreadPoolExecutor(max_workers=1) as execution_pool:
                execution_future = execution_pool.submit(course_executor.execute)
                while not execution_future.done():
                    recovery_state = application.recover(
                        job_id=submitted_job.job_id,
                        user_id=_LIVE_COURSE_OWNER_ID,
                    )
                    durable_checkpoint = recovery_state.checkpoint
                    if durable_checkpoint is not None and (
                        not observed_checkpoints
                        or durable_checkpoint.sequence != observed_checkpoints[-1][0]
                    ):
                        observed_checkpoints.append(
                            (
                                durable_checkpoint.sequence,
                                durable_checkpoint.stage,
                            )
                        )
                    sleep(0.1)
                completed_job = execution_future.result()

        final_recovery_state = application.recover(
            job_id=submitted_job.job_id,
            user_id=_LIVE_COURSE_OWNER_ID,
        )
        final_durable_checkpoint = final_recovery_state.checkpoint
        assert final_durable_checkpoint is not None
        if (
            not observed_checkpoints
            or observed_checkpoints[-1][0] != final_durable_checkpoint.sequence
        ):
            observed_checkpoints.append(
                (
                    final_durable_checkpoint.sequence,
                    final_durable_checkpoint.stage,
                )
            )

        checkpoint_sequences = [
            checkpoint_sequence for checkpoint_sequence, _stage in observed_checkpoints
        ]
        assert checkpoint_sequences == sorted(set(checkpoint_sequences))
        observed_stage_names = [
            checkpoint_stage for _sequence, checkpoint_stage in observed_checkpoints
        ]
        assert observed_stage_names.index("collect_evidence") < next(
            stage_index
            for stage_index, checkpoint_stage in enumerate(observed_stage_names)
            if checkpoint_stage == "design_course"
            or checkpoint_stage.startswith("write_module:")
        )

        final_checkpoint = PipelineCheckpoint.model_validate(
            final_durable_checkpoint.artifact
        )
        assert final_checkpoint.stage == "cross_validate_artifacts"
        assert final_checkpoint.evidence_set is not None
        assert final_checkpoint.evidence_set.sources
        assert final_checkpoint.evidence_set.excerpts
        assert final_checkpoint.answer_key is not None
        assert final_checkpoint.usage_records
        assert {
            usage_record.model_id for usage_record in final_checkpoint.usage_records
        } == {_LIVE_COURSE_MODEL_ID}
        assert all(
            usage_record.billing_source is BillingSource.chatgpt_subscription
            for usage_record in final_checkpoint.usage_records
        )

        public_job = application.get_public_job(
            job_id=submitted_job.job_id,
            user_id=_LIVE_COURSE_OWNER_ID,
        )
        artifact_manifest = application.get_artifact_manifest(
            job_id=submitted_job.job_id,
            user_id=_LIVE_COURSE_OWNER_ID,
        )
        assert completed_job.status is JobStatus.completed
        assert public_job.status is JobStatus.completed
        assert public_job.artifacts.available is True
        assert public_job.artifacts.count == 16
        assert len(artifact_manifest.artifacts) == 16

        downloaded_artifacts: dict[str, bytes] = {}
        for artifact_metadata in artifact_manifest.artifacts:
            with application.open_artifact(
                job_id=submitted_job.job_id,
                user_id=_LIVE_COURSE_OWNER_ID,
                artifact_id=artifact_metadata.artifact_id,
            ) as artifact_chunks:
                artifact_bytes = b"".join(artifact_chunks)
            downloaded_artifacts[artifact_metadata.artifact_id] = artifact_bytes
            assert len(artifact_bytes) == artifact_metadata.size_bytes
            assert (
                f"sha256:{sha256(artifact_bytes).hexdigest()}"
                == artifact_metadata.content_hash
            )

        # These bounded content checks cover the exact live publication while
        # avoiding logs or tracked copies of any artifact body. Detailed
        # format behavior remains credential-free in unit tests.
        review_markdown = downloaded_artifacts["review_pack_markdown"].decode("utf-8")
        assert (
            re.search(
                r"\b(?:section|objective|exercise|flashcard|source)_id\b",
                review_markdown,
                re.IGNORECASE,
            )
            is None
        )
        assert (
            re.search(
                r"\b(?:lo|obj|sec|pe|we|fc)[-_:]?\d[A-Za-z0-9._:-]*\b",
                review_markdown,
                re.IGNORECASE,
            )
            is None
        )
        assert (
            re.search(
                r"\b(?:section|objective|practice|exercise|worked|flashcard)"
                r"[-_:](?=[A-Za-z0-9._:-]*\d)[A-Za-z0-9._:-]+\b",
                review_markdown,
                re.IGNORECASE,
            )
            is None
        )
        assert (
            re.search(
                r"\bobjective\s+Objective\b",
                review_markdown,
                re.IGNORECASE,
            )
            is None
        )
        assessment_markdown = downloaded_artifacts["assessment_markdown"].decode(
            "utf-8"
        )
        answer_key_markdown = downloaded_artifacts["answer_key_markdown"].decode(
            "utf-8"
        )
        assert "Evidence sources" not in assessment_markdown
        assert "Grading criteria" not in assessment_markdown
        assert answer_key_markdown.count("**Evidence sources**") == len(
            final_checkpoint.answer_key.answers
        )

        elapsed_seconds = int(monotonic() - started_at)
        print(
            "live_course_safe_summary "
            f"model_family=gpt-5.6 artifact_count=16 "
            f"duration_seconds={elapsed_seconds} "
            f"checkpoint_count={len(observed_checkpoints)}"
        )
    finally:
        application.close()
