# SPDX-License-Identifier: MIT-0

"""Real and deterministic composition roots behind one public protocol."""

from collections.abc import Iterator
from contextlib import AbstractContextManager, ExitStack, contextmanager
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import RLock
from typing import Protocol, runtime_checkable

import httpx

from txt2crs.ai.codex_runtime import (
    OfficialCodexSdkAdapter,
    ResearchMcpConnection,
)
from txt2crs.ai.fake_runtime import FakeRuntime, ScriptedTurn
from txt2crs.ai.job_runtime import (
    JobRuntimeResources,
    JobRuntimeResourcesFactory,
    ManagedProviderSessionFactory,
)
from txt2crs.ai.model_policy import Gpt56ModelPolicy
from txt2crs.ai.retry import RetryController, RetrySettings
from txt2crs.ai.runtime import CancellationToken
from txt2crs.ai.runtime_status import (
    CredentialStatus,
    RuntimeReadiness,
    RuntimeReadinessStatus,
)
from txt2crs.ai.system_authentication import (
    DedicatedSystemAuthenticator,
    SystemAuthenticationSnapshot,
    SystemAuthenticationState,
)
from txt2crs.ai.tool_guardrails import (
    ToolCallGuardrailConfig,
    ToolCallGuardrailController,
)
from txt2crs.ai.usage import RuntimeUsage, SubscriptionQuotaState
from txt2crs.application.config import (
    DeterministicApplicationConfig,
    DeterministicGenerationScenario,
    RealApplicationConfig,
)
from txt2crs.application.facade import ApplicationExecutor, Txt2CrsApplication
from txt2crs.application.owner_lifecycle import OwnerPurgeCoordinator
from txt2crs.generation.pipeline import CourseGenerationPipeline
from txt2crs.ingestion.documents import DocxAdapter, PptxAdapter
from txt2crs.ingestion.media import (
    FasterWhisperTranscriber,
    ImageOcrAdapter,
    PytesseractOcrEngine,
    TimestampedSegment,
    TranscriptionAdapter,
)
from txt2crs.ingestion.models import IngestionLimits
from txt2crs.ingestion.pdf import PdfAdapter
from txt2crs.ingestion.routing_url import RoutingUrlAdapter
from txt2crs.ingestion.service import IngestionService, InputAdapter
from txt2crs.ingestion.url import UrlAdapter
from txt2crs.ingestion.youtube import (
    DefaultYouTubeTranscriptFetcher,
    YouTubeTranscriptAdapter,
)
from txt2crs.jobs.artifact_store import FilesystemPrivateArtifactStore
from txt2crs.jobs.executor import DurablePipelineFactory, GenerationJobExecutor
from txt2crs.jobs.notifications import DeliveryNotificationPolicy
from txt2crs.jobs.preparation import GenerationPreparationService
from txt2crs.jobs.quota import AdmissionLimits
from txt2crs.jobs.requests import ExecutionProfile, GenerationRequest
from txt2crs.jobs.service import JobService
from txt2crs.jobs.store import SqliteJobStore
from txt2crs.rendering.artifacts import ArtifactRenderer
from txt2crs.research.coordinator import ResearchCoordinatorService
from txt2crs.research.evidence import FrozenEvidenceSet
from txt2crs.research.managed_mcp import ManagedResearchMcpServer
from txt2crs.research.mcp_server import ResearchMcpApplication
from txt2crs.research.service import ResearchToolService
from txt2crs.research.source_policy import (
    ProviderReviewStatus,
    ResearchSourcePolicy,
    SourcePolicyRegistry,
)
from txt2crs.research.tavily import TAVILY_ORIGIN, TavilyClient, TavilySettings
from txt2crs.security.policy import ContentPolicy
from txt2crs.security.url_safety import _default_resolver, normalize_public_url


@runtime_checkable
class ApplicationFactory(Protocol):
    """Common shell-injectable factory contract."""

    def create(self) -> Txt2CrsApplication:
        """Return one fully composed application facade."""


class _DeterministicAuthenticator:
    """Credential-free browser-safe authentication boundary for local tests."""

    def __init__(self) -> None:
        self._closed = False

    @staticmethod
    def _snapshot() -> SystemAuthenticationSnapshot:
        """Return an explicit non-credentialed deterministic state."""

        return SystemAuthenticationSnapshot(
            state=SystemAuthenticationState.signed_out,
            verification_url=None,
            user_code=None,
            message="Deterministic application does not use provider credentials.",
        )

    def start_device_code_login(self) -> SystemAuthenticationSnapshot:
        """Keep deterministic mode credential-free."""

        return self._snapshot()

    def current_status(self, *, refresh: bool = False) -> SystemAuthenticationSnapshot:
        """Return the same safe state without performing external work."""

        del refresh
        return self._snapshot()

    def logout(self) -> SystemAuthenticationSnapshot:
        """Return the already-signed-out state."""

        return self._snapshot()

    def close(self) -> None:
        """Make repeated deterministic cleanup harmless."""

        self._closed = True


class _DeterministicReadinessInspector:
    """Return a truthful ready state for the complete local fake graph."""

    def inspect_readiness(self) -> RuntimeReadiness:
        """Report local readiness without claiming subscription telemetry."""

        return RuntimeReadiness.create(
            status=RuntimeReadinessStatus.ready,
            credential_status=CredentialStatus.valid,
            model_entitled=True,
            subscription_quota_state=SubscriptionQuotaState.unknown,
            warnings=["Deterministic provider mode is active."],
            recovery_actions=[],
        )


class _DeterministicResearchCoordinator:
    """Return a fresh immutable evidence copy without network access."""

    def __init__(self, evidence_set: FrozenEvidenceSet) -> None:
        self._evidence_set_json = evidence_set.model_dump_json()

    def collect(
        self,
        _research_plan: object,
        cancellation: CancellationToken,
        *,
        high_risk_course: bool,
    ) -> FrozenEvidenceSet:
        """Check local policy and return a separately parsed evidence set."""

        if high_risk_course:
            raise PermissionError("Deterministic P0 research forbids high-risk work.")
        # Structural typing keeps this fake independent from SDK objects while
        # still exercising the production cancellation token supplied by the
        # pipeline.
        cancellation.raise_if_cancelled()
        return FrozenEvidenceSet.model_validate_json(self._evidence_set_json)


class _BoundPipelineFactory(DurablePipelineFactory):
    """Yield one already-composed pipeline for one exact request identity."""

    def __init__(
        self,
        *,
        request_hash: str,
        pipeline: CourseGenerationPipeline,
    ) -> None:
        self._request_hash = request_hash
        self._pipeline = pipeline

    @contextmanager
    def open(
        self,
        generation_request: GenerationRequest,
    ) -> Iterator[CourseGenerationPipeline]:
        """Reject retargeting and keep the pipeline alive for result extraction."""

        if generation_request.request_hash != self._request_hash:
            raise ValueError("The executor pipeline belongs to another request.")
        yield self._pipeline


class _DeterministicExecutorFactory:
    """Create fresh local model, evidence, budget, and cancellation per job."""

    def __init__(
        self,
        *,
        job_service: JobService,
        artifact_renderer: ArtifactRenderer,
        scenario: DeterministicGenerationScenario,
    ) -> None:
        self._job_service = job_service
        self._artifact_renderer = artifact_renderer
        self._scenario = scenario

    def create_executor(
        self,
        *,
        job_id: str,
        user_id: str,
        generation_request: GenerationRequest,
    ) -> ApplicationExecutor:
        """Build one complete isolated deterministic graph."""

        if generation_request.execution_profile.model_id != self._scenario.model_id:
            raise ValueError("The stored request requires another model.")
        resources = JobRuntimeResourcesFactory().create(
            generation_request.execution_profile
        )
        fake_runtime = FakeRuntime(
            readiness_status=RuntimeReadinessStatus.ready,
            credential_status=CredentialStatus.valid,
            models=(self._scenario.model_id,),
            scripted_turns=tuple(
                ScriptedTurn(
                    output=turn.load_output(),
                    usage=RuntimeUsage.for_chatgpt_subscription(
                        model_id=self._scenario.model_id,
                        input_tokens=1,
                        output_tokens=1,
                        latency_ms=0,
                    ),
                    thread_id=f"deterministic-{turn.stage}",
                    turn_id=f"deterministic-{turn.stage}",
                )
                for turn in self._scenario.turns
            ),
        )
        pipeline = CourseGenerationPipeline(
            runtime=fake_runtime,
            research_coordinator=_DeterministicResearchCoordinator(
                self._scenario.load_evidence_set()
            ),
            renderer=self._artifact_renderer,
            model_id=self._scenario.model_id,
            budget=resources.budget,
            retry_settings=_retry_settings(generation_request.execution_profile),
        )
        executor = GenerationJobExecutor(
            job_service=self._job_service,
            preparation_service=_preparation_service(
                execution_profile=generation_request.execution_profile,
                adapters={},
            ),
            pipeline_factory=_BoundPipelineFactory(
                request_hash=generation_request.request_hash,
                pipeline=pipeline,
            ),
            renderer=self._artifact_renderer,
        )
        return ApplicationExecutor(
            executor=executor,
            job_id=job_id,
            user_id=user_id,
            cancellation=resources.cancellation,
        )


@dataclass(frozen=True, slots=True)
class _RealResearchSession:
    """Managed listener URL plus direct coordinator for the local pipeline."""

    url: str
    coordinator: ResearchCoordinatorService


class _RealDurablePipelineFactory(DurablePipelineFactory):
    """Open all real provider resources lazily for one stored request."""

    def __init__(
        self,
        *,
        config: RealApplicationConfig,
        resources: JobRuntimeResources,
        request_hash: str,
        artifact_renderer: ArtifactRenderer,
    ) -> None:
        self._config = config
        self._resources = resources
        self._request_hash = request_hash
        self._artifact_renderer = artifact_renderer

    @contextmanager
    def open(
        self,
        generation_request: GenerationRequest,
    ) -> Iterator[CourseGenerationPipeline]:
        """Compose and own Tavily, MCP, Codex, coordinator, and pipeline."""

        if generation_request.request_hash != self._request_hash:
            raise ValueError("The executor pipeline belongs to another request.")
        if (
            generation_request.execution_profile.model_id
            != self._config.default_execution_profile.model_id
        ):
            raise ValueError("The stored request requires another configured model.")

        provider_factory = _managed_real_provider_factory(
            config=self._config,
            execution_profile=generation_request.execution_profile,
        )
        with provider_factory.open(self._resources) as provider_session:
            research_session = provider_session.research_mcp
            if not isinstance(research_session, _RealResearchSession):
                raise TypeError("The managed research session is unavailable.")
            yield CourseGenerationPipeline(
                runtime=provider_session.runtime,
                research_coordinator=research_session.coordinator,
                renderer=self._artifact_renderer,
                model_id=generation_request.execution_profile.model_id,
                budget=self._resources.budget,
                retry_settings=_retry_settings(generation_request.execution_profile),
            )


class _RealExecutorFactory:
    """Build fresh real provider state from the exact durable request."""

    def __init__(
        self,
        *,
        config: RealApplicationConfig,
        job_service: JobService,
        artifact_renderer: ArtifactRenderer,
        ingestion_adapters: dict[str, InputAdapter],
    ) -> None:
        self._config = config
        self._job_service = job_service
        self._artifact_renderer = artifact_renderer
        self._ingestion_adapters = ingestion_adapters

    def create_executor(
        self,
        *,
        job_id: str,
        user_id: str,
        generation_request: GenerationRequest,
    ) -> ApplicationExecutor:
        """Create one fresh mutable graph without opening provider resources."""

        resources = JobRuntimeResourcesFactory().create(
            generation_request.execution_profile
        )
        executor = GenerationJobExecutor(
            job_service=self._job_service,
            preparation_service=_preparation_service(
                execution_profile=generation_request.execution_profile,
                adapters=self._ingestion_adapters,
            ),
            pipeline_factory=_RealDurablePipelineFactory(
                config=self._config,
                resources=resources,
                request_hash=generation_request.request_hash,
                artifact_renderer=self._artifact_renderer,
            ),
            renderer=self._artifact_renderer,
        )
        return ApplicationExecutor(
            executor=executor,
            job_id=job_id,
            user_id=user_id,
            cancellation=resources.cancellation,
        )


class _RealReadinessInspector:
    """Probe the same finite managed provider graph used by real jobs."""

    def __init__(self, config: RealApplicationConfig) -> None:
        self._config = config

    def inspect_readiness(self) -> RuntimeReadiness:
        """Open, inspect, and close one real graph or return safe unavailable."""

        resources = JobRuntimeResourcesFactory().create(
            self._config.default_execution_profile
        )
        provider_factory = _managed_real_provider_factory(
            config=self._config,
            execution_profile=self._config.default_execution_profile,
        )
        readiness: RuntimeReadiness | None = None
        try:
            with provider_factory.open(resources) as provider_session:
                readiness = provider_session.runtime.inspect_readiness()
        except Exception:
            # Managed open already cleans each partial dependency. Readiness
            # deliberately omits which private component failed.
            pass
        if readiness is not None:
            return readiness
        return RuntimeReadiness.create(
            status=RuntimeReadinessStatus.unavailable,
            credential_status=CredentialStatus.unknown,
            model_entitled=False,
            subscription_quota_state=SubscriptionQuotaState.unknown,
            warnings=["The configured provider runtime is unavailable."],
            recovery_actions=["Review system authentication and retry readiness."],
        )


class _LazyFasterWhisperTranscriber:
    """Delay optional model loading until an audio/video input is selected."""

    def __init__(self) -> None:
        self._transcriber: FasterWhisperTranscriber | None = None
        self._lock = RLock()

    def transcribe(
        self,
        media_bytes: bytes,
        media_type: str,
    ) -> list[TimestampedSegment]:
        """Construct the optional transcriber once, only on actual use."""

        with self._lock:
            if self._transcriber is None:
                self._transcriber = FasterWhisperTranscriber()
            transcriber = self._transcriber
        return transcriber.transcribe(media_bytes, media_type)


class DeterministicApplicationFactory:
    """Compose a complete credential-free application over production stores."""

    def __init__(self, config: DeterministicApplicationConfig) -> None:
        self._config = config

    def create(self) -> Txt2CrsApplication:
        """Create one local application with fresh scenario state per executor."""

        (
            store,
            artifact_store,
            job_service,
            artifact_renderer,
        ) = _persistent_services(
            state_directory=self._config.storage.state_directory,
            job_database_path=self._config.storage.job_database_path,
            artifact_directory=self._config.storage.artifact_directory,
            maximum_artifact_job_bytes=(
                self._config.storage.maximum_artifact_job_bytes
            ),
            artifact_retention_days=self._config.storage.artifact_retention_days,
            admission_limits=self._config.admission.to_domain(),
        )
        # Until the facade is successfully returned, this stack owns every
        # long-lived resource and unwinds them in reverse construction order.
        with ExitStack() as construction_cleanup:
            construction_cleanup.callback(store.close)
            authenticator = _DeterministicAuthenticator()
            construction_cleanup.callback(authenticator.close)
            application = Txt2CrsApplication(
                job_service=job_service,
                readiness_inspector=_DeterministicReadinessInspector(),
                authenticator=authenticator,
                executor_factory=_DeterministicExecutorFactory(
                    job_service=job_service,
                    artifact_renderer=artifact_renderer,
                    scenario=self._config.scenario,
                ),
                owner_lifecycle=OwnerPurgeCoordinator(
                    artifact_store=artifact_store,
                    owner_store=store,
                ),
                close_callbacks=(store.close,),
            )
            # Ownership has moved into Txt2CrsApplication.close().
            construction_cleanup.pop_all()
            return application


class RealApplicationFactory:
    """Compose production package implementations without starting a job graph."""

    def __init__(self, config: RealApplicationConfig) -> None:
        self._config = config

    def create(self) -> Txt2CrsApplication:
        """Create long-lived local stores/ingestion/auth and lazy executors."""

        (
            store,
            artifact_store,
            job_service,
            artifact_renderer,
        ) = _persistent_services(
            state_directory=self._config.storage.state_directory,
            job_database_path=self._config.storage.job_database_path,
            artifact_directory=self._config.storage.artifact_directory,
            maximum_artifact_job_bytes=(
                self._config.storage.maximum_artifact_job_bytes
            ),
            artifact_retention_days=self._config.storage.artifact_retention_days,
            admission_limits=self._config.admission.to_domain(),
        )
        with ExitStack() as construction_cleanup:
            construction_cleanup.callback(store.close)
            ingestion_http_client = httpx.Client(
                follow_redirects=False,
                timeout=self._config.http_timeout_seconds,
            )
            construction_cleanup.callback(ingestion_http_client.close)
            ingestion_adapters = _real_ingestion_adapters(
                config=self._config,
                http_client=ingestion_http_client,
            )
            # System authentication also launches Codex app-server, so its cwd
            # belongs under the configured ephemeral worker root. Keeping this
            # directory out of durable state prevents it from entering backups
            # alongside SQLite, artifacts, and credentials.
            authentication_worker_directory = (
                self._config.worker_directory / "authentication"
            )
            authenticator = DedicatedSystemAuthenticator.create(
                worker_directory=authentication_worker_directory,
                codex_home=self._config.codex_home,
            )
            construction_cleanup.callback(authenticator.close)
            application = Txt2CrsApplication(
                job_service=job_service,
                readiness_inspector=_RealReadinessInspector(self._config),
                authenticator=authenticator,
                executor_factory=_RealExecutorFactory(
                    config=self._config,
                    job_service=job_service,
                    artifact_renderer=artifact_renderer,
                    ingestion_adapters=ingestion_adapters,
                ),
                owner_lifecycle=OwnerPurgeCoordinator(
                    artifact_store=artifact_store,
                    owner_store=store,
                ),
                close_callbacks=(ingestion_http_client.close, store.close),
            )
            construction_cleanup.pop_all()
            return application


def _persistent_services(
    *,
    state_directory: Path,
    job_database_path: Path | None,
    artifact_directory: Path | None,
    maximum_artifact_job_bytes: int,
    artifact_retention_days: int,
    admission_limits: AdmissionLimits,
) -> tuple[
    SqliteJobStore,
    FilesystemPrivateArtifactStore,
    JobService,
    ArtifactRenderer,
]:
    """Create and permission the shared durable foundation."""

    if state_directory.is_symlink():
        raise ValueError("Application state directory cannot be a symlink.")
    state_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    state_directory.chmod(0o700)
    if job_database_path is None or artifact_directory is None:
        # Public config validation always resolves these compatibility fields.
        # Keeping a defensive guard here prevents an invalid manually-created
        # object from falling back to an unintended working-directory path.
        raise ValueError("Application storage paths must be resolved.")

    resolved_job_database_path = job_database_path.resolve(strict=False)
    resolved_artifact_directory = artifact_directory.resolve(strict=False)
    resolved_job_database_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    resolved_job_database_path.parent.chmod(0o700)
    store = SqliteJobStore(
        resolved_job_database_path,
        admission_limits=admission_limits,
    )
    try:
        artifact_store = FilesystemPrivateArtifactStore(
            root_directory=resolved_artifact_directory,
            maximum_job_bytes=maximum_artifact_job_bytes,
            retention_days=artifact_retention_days,
        )
        artifact_renderer = ArtifactRenderer()
        job_service = JobService(
            store=store,
            artifact_store=artifact_store,
            notification_policy=DeliveryNotificationPolicy.disabled(),
        )
    except BaseException:
        # No facade exists yet to own the SQLite connection. Closing here also
        # handles interruption during construction, not only normal exceptions.
        store.close()
        raise
    return store, artifact_store, job_service, artifact_renderer


def _preparation_service(
    *,
    execution_profile: ExecutionProfile,
    adapters: dict[str, InputAdapter],
) -> GenerationPreparationService:
    """Use exact stored input limits and policy version for each job."""

    return GenerationPreparationService(
        ingestion_service=IngestionService(
            limits=IngestionLimits(
                maximum_input_bytes=(
                    execution_profile.input_limits.maximum_input_bytes
                ),
                maximum_normalized_characters=(
                    execution_profile.input_limits.maximum_normalized_characters
                ),
            ),
            adapters=adapters,
        ),
        content_policy=ContentPolicy(policy_version=execution_profile.policy_version),
    )


def _retry_settings(execution_profile: ExecutionProfile) -> RetrySettings:
    """Translate the exact stored retry policy without applying new defaults."""

    retry_policy = execution_profile.retry_policy
    return RetrySettings(
        maximum_attempts=retry_policy.maximum_attempts,
        base_seconds=retry_policy.base_seconds,
        maximum_seconds=retry_policy.maximum_seconds,
        jitter_ratio=retry_policy.jitter_ratio,
    )


def _real_ingestion_adapters(
    *,
    config: RealApplicationConfig,
    http_client: httpx.Client,
) -> dict[str, InputAdapter]:
    """Construct every enabled concrete ingestion adapter inside the package."""

    tavily_client = TavilyClient(
        settings=TavilySettings(
            api_key=config.tavily_api_key,
            timeout_seconds=config.http_timeout_seconds,
            maximum_document_bytes=config.maximum_research_document_bytes,
        ),
        http_client=http_client,
        url_resolver=_default_resolver,
    )
    youtube_adapter = YouTubeTranscriptAdapter(
        transcript_fetcher=DefaultYouTubeTranscriptFetcher(),
        preferred_languages=list(config.preferred_youtube_languages) or None,
    )
    url_adapter = RoutingUrlAdapter(
        normalize_public_url=lambda url: normalize_public_url(
            url,
            resolver=_default_resolver,
        ),
        youtube_adapter=youtube_adapter,
        general_url_adapter=UrlAdapter(extractor=tavily_client),
    )
    adapters: dict[str, InputAdapter] = {
        "url": url_adapter,
        "pdf": PdfAdapter(
            maximum_pages=(
                config.default_execution_profile.input_limits.maximum_pdf_pages
            )
        ),
        "document": DocxAdapter(),
        "slides": PptxAdapter(),
        "image": ImageOcrAdapter(ocr_engine=PytesseractOcrEngine()),
    }
    if config.enable_local_transcription:
        transcription_adapter = TranscriptionAdapter(
            transcriber=_LazyFasterWhisperTranscriber()
        )
        adapters["audio"] = transcription_adapter
        adapters["video"] = transcription_adapter
    return adapters


def _managed_real_provider_factory(
    *,
    config: RealApplicationConfig,
    execution_profile: ExecutionProfile,
) -> ManagedProviderSessionFactory:
    """Build closures that create every provider resource only on context entry."""

    workers_directory = config.worker_directory
    workers_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    workers_directory.chmod(0o700)

    @contextmanager
    def temporary_worker() -> Iterator[Path]:
        """Yield one isolated directory and remove it after provider cleanup."""

        with TemporaryDirectory(
            prefix="txt2crs-job-",
            dir=workers_directory,
        ) as temporary_path:
            worker_directory = Path(temporary_path)
            worker_directory.chmod(0o700)
            yield worker_directory

    def http_client_context() -> AbstractContextManager[httpx.Client]:
        """Return one job-scoped Tavily HTTP client."""

        return httpx.Client(
            follow_redirects=False,
            timeout=config.http_timeout_seconds,
        )

    @contextmanager
    def research_mcp_context(
        resources: JobRuntimeResources,
        http_client: httpx.Client,
    ) -> Iterator[_RealResearchSession]:
        """Compose reviewed Tavily tools, coordinator, and managed MCP."""

        retry_controller = RetryController(
            settings=_retry_settings(execution_profile),
            budget=resources.budget,
            cancellation=resources.cancellation,
        )
        source_policy = ResearchSourcePolicy(
            schema_version="1.0",
            policy_version="tavily-policy-v1",
            provider_id="tavily",
            review_status=ProviderReviewStatus.reviewed,
            enabled=True,
            reviewed_by="txt2crs package policy",
            reviewed_on=date(2026, 7, 19),
            allowed_origin=TAVILY_ORIGIN,
            model_controlled_fields=["query", "maximum_results"],
            maximum_items_per_request=100,
            maximum_items_per_job=execution_profile.run_limits.maximum_sources,
            maximum_bytes_per_job=(
                execution_profile.run_limits.maximum_extracted_bytes
            ),
            maximum_seconds_per_request=config.http_timeout_seconds,
            allowed_course_domains=list(config.primary_research_domains),
            high_risk_allowed=False,
        )
        research_service = ResearchToolService(
            provider_id="tavily",
            provider=TavilyClient(
                settings=TavilySettings(
                    api_key=config.tavily_api_key,
                    timeout_seconds=config.http_timeout_seconds,
                    maximum_document_bytes=(config.maximum_research_document_bytes),
                ),
                http_client=http_client,
                url_resolver=_default_resolver,
            ),
            source_policy_registry=SourcePolicyRegistry([source_policy]),
            budget=resources.budget,
            guardrail=ToolCallGuardrailController(ToolCallGuardrailConfig()),
            cancellation=resources.cancellation,
            retry_controller=retry_controller,
        )
        coordinator = ResearchCoordinatorService(
            tools=research_service,
            clock=lambda: datetime.now(UTC),
            primary_domains=set(config.primary_research_domains),
        )
        managed_server = ManagedResearchMcpServer(
            ResearchMcpApplication(
                research_service,
                host=config.managed_mcp_host,
                port=config.managed_mcp_port,
            ),
            host=config.managed_mcp_host,
            port=config.managed_mcp_port,
            startup_timeout_seconds=(config.managed_mcp_startup_timeout_seconds),
            shutdown_timeout_seconds=(config.managed_mcp_shutdown_timeout_seconds),
        )
        with managed_server:
            yield _RealResearchSession(
                url=managed_server.url,
                coordinator=coordinator,
            )

    def codex_adapter(
        worker_directory: Path,
        research_session: _RealResearchSession,
    ) -> OfficialCodexSdkAdapter:
        """Create the exact subscription adapter with reviewed MCP only."""

        return OfficialCodexSdkAdapter.create(
            worker_directory=worker_directory,
            codex_home=config.codex_home,
            research_mcp=ResearchMcpConnection(url=research_session.url),
        )

    return ManagedProviderSessionFactory(
        temporary_worker_context_factory=temporary_worker,
        http_client_context_factory=http_client_context,
        research_mcp_context_factory=research_mcp_context,
        codex_adapter_factory=codex_adapter,
        model_policy=Gpt56ModelPolicy(configured_model_id=execution_profile.model_id),
    )
