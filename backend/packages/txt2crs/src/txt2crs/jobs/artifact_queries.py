# SPDX-License-Identifier: MIT-0

"""Path-free public contracts for private rendered artifacts."""

import re
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import Annotated

from pydantic import ConfigDict, Field, model_validator

from txt2crs.domain.models import HashValue, Identifier, SchemaVersion, StrictContract
from txt2crs.rendering.artifacts import RenderedArtifact

_ARTIFACT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA256_HEX_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_MANIFEST_FILE_NAME = "manifest.json"
_MAXIMUM_MANIFEST_BYTES = 128 * 1024
ARTIFACT_STREAM_CHUNK_BYTES = 64 * 1024


def _has_control_characters(value: str) -> bool:
    """Return whether text contains C0, DEL, or C1 control characters."""

    return any(
        ord(character) < 32 or 127 <= ord(character) <= 159 for character in value
    )


class ArtifactIntegrityError(ValueError):
    """Stored metadata, topology, or bytes failed private integrity checks."""


class ArtifactDeliverable(StrEnum):
    """Canonical educational products generated for one accepted course."""

    course = "course"
    review_pack = "review_pack"
    assessment = "assessment"
    answer_key = "answer_key"


class ArtifactFormat(StrEnum):
    """Portable output formats emitted by the deterministic renderer."""

    html = "html"
    markdown = "markdown"
    pdf = "pdf"
    docx = "docx"


# Renderer dictionary keys are already stable across storage and recovery.
# Keeping an exact map here prevents a private/debug file from becoming a
# downloadable public artifact merely because its name happens to contain an
# underscore or a familiar extension.
_CANONICAL_ARTIFACT_KINDS: dict[
    str,
    tuple[ArtifactDeliverable, ArtifactFormat],
] = {
    f"{deliverable.value}_{artifact_format.value}": (
        deliverable,
        artifact_format,
    )
    for deliverable in ArtifactDeliverable
    for artifact_format in ArtifactFormat
}


class _PublicArtifactContract(StrictContract):
    """Shared immutable configuration for path-free artifact query results."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )


class ArtifactMetadata(_PublicArtifactContract):
    """Allowlisted metadata for one canonical private artifact."""

    artifact_id: Identifier
    deliverable: ArtifactDeliverable
    format: ArtifactFormat
    safe_file_name: Annotated[str, Field(min_length=1, max_length=255)]
    media_type: Annotated[str, Field(min_length=3, max_length=255)]
    size_bytes: int = Field(ge=0, le=1_000_000_000)
    content_hash: HashValue

    @model_validator(mode="after")
    def validate_public_metadata(self) -> "ArtifactMetadata":
        """Reject path-like names, header injection, and ID/type drift."""

        file_name = self.safe_file_name
        if (
            Path(file_name).name != file_name
            or file_name in {".", "..", _MANIFEST_FILE_NAME}
            or "/" in file_name
            or "\\" in file_name
            or _has_control_characters(file_name)
        ):
            raise ValueError("Artifact file name is unsafe.")
        if "/" not in self.media_type or _has_control_characters(self.media_type):
            raise ValueError("Artifact media type is unsafe.")
        expected_kind = _canonical_artifact_kind(self.artifact_id)
        if expected_kind != (self.deliverable, self.format):
            raise ValueError("Artifact identifier and public kind do not match.")
        return self


class ArtifactManifest(_PublicArtifactContract):
    """Verified path-free metadata for one owner-authorized artifact set."""

    schema_version: SchemaVersion
    job_id: Identifier
    created_at: datetime
    artifacts: tuple[ArtifactMetadata, ...] = Field(min_length=1, max_length=16)

    @model_validator(mode="after")
    def validate_manifest_identity(self) -> "ArtifactManifest":
        """Require deterministic ordering and unique IDs/file names."""

        artifact_ids = [artifact.artifact_id for artifact in self.artifacts]
        file_names = [artifact.safe_file_name for artifact in self.artifacts]
        if artifact_ids != sorted(artifact_ids):
            raise ValueError("Artifact manifest must use stable ID order.")
        if len(artifact_ids) != len(set(artifact_ids)):
            raise ValueError("Artifact manifest IDs must be unique.")
        if len(file_names) != len(set(file_names)):
            raise ValueError("Artifact manifest file names must be unique.")
        return self


def _canonical_artifact_kind(
    artifact_id: str,
) -> tuple[ArtifactDeliverable, ArtifactFormat] | None:
    """Return the reviewed deliverable/format pair for one stable ID."""

    return _CANONICAL_ARTIFACT_KINDS.get(artifact_id)


def _build_artifact_manifest_from_rendered(
    *,
    job_id: str,
    created_at: datetime,
    artifacts: dict[str, RenderedArtifact],
) -> ArtifactManifest:
    """Build path-free canonical metadata for the deterministic memory store."""

    public_manifest: ArtifactManifest | None = None
    try:
        _validate_private_rendered_artifact_metadata(artifacts)
        public_metadata: list[ArtifactMetadata] = []
        for artifact_id, rendered_artifact in sorted(artifacts.items()):
            public_kind = _canonical_artifact_kind(artifact_id)
            if public_kind is None:
                raise ArtifactIntegrityError(
                    "Artifact storage failed integrity verification."
                )
            deliverable, artifact_format = public_kind
            public_metadata.append(
                ArtifactMetadata(
                    artifact_id=artifact_id,
                    deliverable=deliverable,
                    format=artifact_format,
                    safe_file_name=rendered_artifact.file_name,
                    media_type=rendered_artifact.media_type,
                    size_bytes=len(rendered_artifact.content),
                    content_hash=(
                        f"sha256:{sha256(rendered_artifact.content).hexdigest()}"
                    ),
                )
            )
        public_manifest = ArtifactManifest(
            schema_version="1.0",
            job_id=job_id,
            created_at=created_at,
            artifacts=tuple(public_metadata),
        )
    except (TypeError, ValueError):
        pass
    if public_manifest is None:
        raise ArtifactIntegrityError("Artifact storage failed integrity verification.")
    return public_manifest


def _validate_private_rendered_artifact_metadata(
    artifacts: dict[str, RenderedArtifact],
) -> None:
    """Validate generic private names before either store mutates state.

    Canonical public ID mapping is intentionally not part of this helper.
    Private whole-bundle recovery still supports reviewed legacy/debug
    artifacts, while public projection separately requires exact renderer IDs.
    """

    if not artifacts:
        raise ValueError("At least one rendered artifact is required.")

    file_names: set[str] = set()
    for artifact_name, artifact in artifacts.items():
        if (
            not isinstance(artifact_name, str)
            or _ARTIFACT_NAME_PATTERN.fullmatch(artifact_name) is None
        ):
            raise ValueError("Artifact name is not a safe identifier.")
        file_name = artifact.file_name
        if (
            not isinstance(file_name, str)
            or not file_name
            or len(file_name) > 255
            or file_name in {".", "..", _MANIFEST_FILE_NAME}
            or Path(file_name).name != file_name
            or "/" in file_name
            or "\\" in file_name
            or _has_control_characters(file_name)
        ):
            raise ValueError("Rendered artifact file name is unsafe.")
        if file_name in file_names:
            raise ValueError("Rendered artifact file names must be unique.")
        file_names.add(file_name)

        media_type = artifact.media_type
        if (
            not isinstance(media_type, str)
            or not 3 <= len(media_type) <= 255
            or "/" not in media_type
            or _has_control_characters(media_type)
        ):
            raise ValueError("Rendered artifact media type is unsafe.")
        if not isinstance(artifact.content, bytes):
            raise ValueError("Rendered artifact content must be bytes.")


__all__ = [
    "ARTIFACT_STREAM_CHUNK_BYTES",
    "ArtifactDeliverable",
    "ArtifactFormat",
    "ArtifactIntegrityError",
    "ArtifactManifest",
    "ArtifactMetadata",
]
