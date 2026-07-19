# SPDX-License-Identifier: MIT-0

"""Strict immutable configuration for real and deterministic applications."""

import json
from ipaddress import ip_address
from pathlib import Path
from typing import Any, Self

from pydantic import ConfigDict, Field, SecretStr, field_validator, model_validator

from txt2crs.ai.model_policy import Gpt56ModelPolicy
from txt2crs.domain.models import Identifier, StrictContract
from txt2crs.jobs.quota import AdmissionLimits
from txt2crs.jobs.requests import ExecutionProfile
from txt2crs.research.evidence import FrozenEvidenceSet


def _require_absolute_unambiguous_path(path: Path, *, field_name: str) -> Path:
    """Reject relative paths and every existing symlink in their ancestry."""

    if not path.is_absolute():
        raise ValueError(f"{field_name} must be absolute")
    # Checking each lexical component before resolving prevents an
    # application-owned credential/state root from silently following a
    # pre-existing parent symlink into another location.
    for path_component in (path, *path.parents):
        if path_component.is_symlink():
            raise ValueError(f"{field_name} cannot contain symlinks")
    return path


def _reject_nonfinite_json_constant(_constant: str) -> None:
    """Reject JSON spellings such as NaN and Infinity."""

    raise ValueError("JSON numbers must be finite")


class FrozenApplicationConfig(StrictContract):
    """Reject unknown fields and mutation at every public config layer."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )


class ApplicationStorageConfig(FrozenApplicationConfig):
    """Private SQLite/artifact state owned by one application process."""

    state_directory: Path
    job_database_path: Path | None = None
    artifact_directory: Path | None = None
    maximum_artifact_job_bytes: int = Field(gt=0, le=1_000_000_000)
    artifact_retention_days: int = Field(gt=0, le=36_500)

    @field_validator("state_directory")
    @classmethod
    def require_absolute_state_directory(cls, state_directory: Path) -> Path:
        """Reject working-directory dependence and symlinked private state."""

        return _require_absolute_unambiguous_path(
            state_directory,
            field_name="state_directory",
        )

    @model_validator(mode="after")
    def resolve_and_confine_storage_paths(self) -> Self:
        """
        Derive legacy defaults and confine explicit paths to one private root.

        Earlier package callers supplied only ``state_directory``. Keeping
        those derived locations preserves compatibility, while the application
        shell can pass the exact SQLite and artifact paths already validated
        for backup, recovery, and container ownership.
        """
        state_directory = self.state_directory.resolve(strict=False)
        configured_job_database_path = (
            self.job_database_path or state_directory / "jobs.sqlite3"
        )
        configured_artifact_directory = (
            self.artifact_directory or state_directory / "artifacts"
        )
        job_database_path = _require_absolute_unambiguous_path(
            configured_job_database_path,
            field_name="job_database_path",
        ).resolve(strict=False)
        artifact_directory = _require_absolute_unambiguous_path(
            configured_artifact_directory,
            field_name="artifact_directory",
        ).resolve(strict=False)

        for field_name, child_path in (
            ("job_database_path", job_database_path),
            ("artifact_directory", artifact_directory),
        ):
            if (
                child_path == state_directory
                or state_directory not in child_path.parents
            ):
                raise ValueError(
                    f"{field_name} must be a strict child of state_directory"
                )

        database_overlaps_artifacts = (
            job_database_path == artifact_directory
            or artifact_directory in job_database_path.parents
            or job_database_path in artifact_directory.parents
        )
        if database_overlaps_artifacts:
            raise ValueError("job_database_path and artifact_directory cannot overlap")

        # Frozen public models prevent caller mutation after validation.
        # object.__setattr__ is limited to this validator so the two optional
        # compatibility inputs become canonical, non-optional runtime values.
        object.__setattr__(self, "state_directory", state_directory)
        object.__setattr__(self, "job_database_path", job_database_path)
        object.__setattr__(self, "artifact_directory", artifact_directory)
        return self


class ApplicationAdmissionConfig(FrozenApplicationConfig):
    """Serializable finite admission limits translated inside the package."""

    window_seconds: int = Field(gt=0)
    maximum_jobs_per_user: int = Field(gt=0)
    maximum_jobs_global: int = Field(gt=0)
    maximum_reserved_tokens_per_user: int = Field(gt=0)
    maximum_reserved_tokens_global: int = Field(gt=0)
    maximum_research_cost_microusd_per_user: int = Field(ge=0)
    maximum_research_cost_microusd_global: int = Field(ge=0)

    def to_domain(self) -> AdmissionLimits:
        """Build the existing quota authority without duplicating its checks."""

        return AdmissionLimits(**self.model_dump(mode="python"))


class DeterministicTurn(FrozenApplicationConfig):
    """One immutable canonical JSON output consumed by a local fake runtime."""

    stage: Identifier
    output_json: str = Field(min_length=2, max_length=5_000_000)

    @field_validator("output_json")
    @classmethod
    def validate_and_canonicalize_output_json(cls, output_json: str) -> str:
        """Require one finite JSON object even for direct model construction."""

        try:
            parsed_output = json.loads(
                output_json,
                parse_constant=_reject_nonfinite_json_constant,
            )
        except (TypeError, ValueError):
            raise ValueError("deterministic turn output must be valid JSON") from None
        if not isinstance(parsed_output, dict):
            raise ValueError("deterministic turn output must be an object")
        return json.dumps(
            parsed_output,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    @classmethod
    def create(cls, *, stage: str, output: dict[str, Any]) -> Self:
        """Freeze one finite JSON object so nested caller mutation is harmless."""

        canonical_output = json.dumps(
            output,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return cls(stage=stage, output_json=canonical_output)

    def load_output(self) -> dict[str, Any]:
        """Return a fresh dictionary for one newly created fake runtime."""

        parsed_output = json.loads(self.output_json)
        if not isinstance(parsed_output, dict):
            raise ValueError("Deterministic turn output must be an object.")
        return parsed_output


class DeterministicGenerationScenario(FrozenApplicationConfig):
    """Immutable local model turns and evidence copied into every job graph."""

    model_id: Identifier
    turns: tuple[DeterministicTurn, ...] = Field(min_length=1, max_length=1_000)
    evidence_set_json: str = Field(min_length=2, max_length=20_000_000)

    @field_validator("evidence_set_json")
    @classmethod
    def validate_and_freeze_evidence_json(cls, evidence_set_json: str) -> str:
        """Validate direct JSON input and retain one canonical strict snapshot."""

        try:
            evidence_set = FrozenEvidenceSet.model_validate_json(evidence_set_json)
        except ValueError:
            raise ValueError(
                "deterministic evidence must match the frozen evidence contract"
            ) from None
        return evidence_set.model_dump_json()

    @classmethod
    def create(
        cls,
        *,
        model_id: str,
        turns: tuple[DeterministicTurn, ...],
        evidence_set: FrozenEvidenceSet | dict[str, Any],
    ) -> Self:
        """Validate and freeze evidence independently from caller containers."""

        validated_evidence_set = FrozenEvidenceSet.model_validate(evidence_set)
        return cls(
            model_id=model_id,
            turns=turns,
            evidence_set_json=validated_evidence_set.model_dump_json(),
        )

    def load_evidence_set(self) -> FrozenEvidenceSet:
        """Return a fresh validated evidence set for one executor graph."""

        return FrozenEvidenceSet.model_validate_json(self.evidence_set_json)


class _BaseApplicationConfig(FrozenApplicationConfig):
    """State shared by real and deterministic composition."""

    storage: ApplicationStorageConfig
    admission: ApplicationAdmissionConfig
    default_execution_profile: ExecutionProfile


class RealApplicationConfig(_BaseApplicationConfig):
    """Values required to compose the real subscription/research application."""

    codex_home: Path
    worker_directory: Path = Path("/tmp/txt2crs-worker")
    tavily_api_key: SecretStr
    managed_mcp_host: str = "127.0.0.1"
    managed_mcp_port: int = Field(default=0, ge=0, le=65_535)
    managed_mcp_startup_timeout_seconds: float = Field(default=10, gt=0, le=60)
    managed_mcp_shutdown_timeout_seconds: float = Field(default=10, gt=0, le=60)
    http_timeout_seconds: float = Field(default=20, gt=0, le=60)
    maximum_research_document_bytes: int = Field(
        default=1_000_000,
        gt=0,
        le=10_000_000,
    )
    preferred_youtube_languages: tuple[str, ...] = Field(
        default=("en",),
        max_length=20,
    )
    primary_research_domains: tuple[Identifier, ...] = Field(
        default=("docs.python.org",),
        min_length=1,
        max_length=100,
    )
    enable_local_transcription: bool = False

    @field_validator("managed_mcp_host")
    @classmethod
    def require_numeric_loopback_mcp_host(cls, managed_mcp_host: str) -> str:
        """Reject wildcard, DNS, and non-loopback listener configuration."""

        try:
            parsed_address = ip_address(managed_mcp_host)
        except ValueError:
            raise ValueError(
                "managed_mcp_host must be an explicit numeric loopback address"
            ) from None
        if not parsed_address.is_loopback:
            raise ValueError("managed_mcp_host must be loopback-only")
        return str(parsed_address)

    @model_validator(mode="after")
    def require_safe_real_configuration(self) -> Self:
        """Bind real paths, secret, and model to reviewed package policy."""

        codex_home = _require_absolute_unambiguous_path(
            self.codex_home,
            field_name="codex_home",
        )
        resolved_codex_home = codex_home.resolve(strict=False)
        worker_directory = _require_absolute_unambiguous_path(
            self.worker_directory,
            field_name="worker_directory",
        ).resolve(strict=False)
        resolved_state_directory = self.storage.state_directory.resolve(strict=False)
        job_database_path = self.storage.job_database_path
        artifact_directory = self.storage.artifact_directory
        # ApplicationStorageConfig canonicalizes both optional compatibility
        # inputs in its model validator before this outer validator runs.
        if job_database_path is None or artifact_directory is None:
            raise ValueError("storage paths were not resolved")

        # A Codex home may be a distinct child of the same owner-only volume or
        # a completely disjoint private root. It may not equal or contain the
        # engine state root because that would give credentials ownership of
        # unrelated durable data.
        if (
            resolved_codex_home == resolved_state_directory
            or resolved_codex_home in resolved_state_directory.parents
        ):
            raise ValueError("codex_home cannot equal or contain state_directory")

        codex_overlaps_artifacts = (
            resolved_codex_home == artifact_directory
            or artifact_directory in resolved_codex_home.parents
            or resolved_codex_home in artifact_directory.parents
        )
        codex_overlaps_database = (
            resolved_codex_home == job_database_path
            or job_database_path in resolved_codex_home.parents
            or resolved_codex_home in job_database_path.parents
        )
        if codex_overlaps_artifacts or codex_overlaps_database:
            raise ValueError("codex_home cannot overlap engine data paths")

        worker_overlaps_state = (
            worker_directory == resolved_state_directory
            or resolved_state_directory in worker_directory.parents
            or worker_directory in resolved_state_directory.parents
        )
        worker_overlaps_codex = (
            worker_directory == resolved_codex_home
            or resolved_codex_home in worker_directory.parents
            or worker_directory in resolved_codex_home.parents
        )
        if worker_overlaps_state or worker_overlaps_codex:
            raise ValueError(
                "worker_directory must remain outside persistent private state"
            )

        object.__setattr__(self, "codex_home", resolved_codex_home)
        object.__setattr__(self, "worker_directory", worker_directory)
        if not self.tavily_api_key.get_secret_value().strip():
            raise ValueError("tavily_api_key cannot be empty")
        Gpt56ModelPolicy(configured_model_id=self.default_execution_profile.model_id)
        return self


class DeterministicApplicationConfig(_BaseApplicationConfig):
    """Credential-free scenario and production persistence configuration."""

    scenario: DeterministicGenerationScenario

    @model_validator(mode="after")
    def require_matching_deterministic_model(self) -> Self:
        """Prevent a scenario from silently overriding stored request identity."""

        if self.scenario.model_id != self.default_execution_profile.model_id:
            raise ValueError("Deterministic scenario model must match the profile.")
        return self
