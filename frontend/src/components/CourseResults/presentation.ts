import type {
  ArtifactDeliverable,
  ArtifactFormat,
  ArtifactManifestPublic,
  ArtifactMetadataPublic,
} from "@/client"

const DELIVERABLE_ORDER: readonly ArtifactDeliverable[] = [
  "course",
  "review_pack",
  "assessment",
  "answer_key",
]

const FORMAT_ORDER: readonly ArtifactFormat[] = [
  "html",
  "markdown",
  "pdf",
  "docx",
]

const EXPECTED_MEDIA_TYPE_BASES: Record<ArtifactFormat, string> = {
  html: "text/html",
  markdown: "text/markdown",
  pdf: "application/pdf",
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

const PUBLICATION_DEFINITIONS: Record<
  ArtifactDeliverable,
  {
    title: string
    shortTitle: string
    eyebrow: string
    description: string
    folio: string
  }
> = {
  course: {
    title: "Course",
    shortTitle: "Course",
    eyebrow: "Teach",
    description:
      "The complete learning sequence, organized into modules and objectives.",
    folio: "01",
  },
  review_pack: {
    title: "Review pack",
    shortTitle: "Review pack",
    eyebrow: "Revisit",
    description:
      "A compact companion for recall, practice, and independent review.",
    folio: "02",
  },
  assessment: {
    title: "Assessment",
    shortTitle: "Assessment",
    eyebrow: "Check",
    description:
      "A learner-facing test aligned with the course's stated objectives.",
    folio: "03",
  },
  answer_key: {
    title: "Instructor answer key",
    shortTitle: "Answer key",
    eyebrow: "Guide",
    description:
      "Private-purpose marking guidance for the person leading the learning.",
    folio: "04",
  },
}

export const ARTIFACT_FORMAT_LABELS: Record<ArtifactFormat, string> = {
  html: "HTML",
  markdown: "Markdown",
  pdf: "PDF",
  docx: "DOCX",
}

export class ManifestPresentationError extends Error {
  constructor(message = "The publication files could not be verified.") {
    super(message)
    this.name = "ManifestPresentationError"
  }
}

function hasControlCharacters(value: string): boolean {
  return [...value].some((character) => {
    const characterCode = character.charCodeAt(0)
    return characterCode < 32 || (characterCode >= 127 && characterCode <= 159)
  })
}

export interface ArtifactPresentation extends ArtifactMetadataPublic {
  formatLabel: string
  sizeLabel: string
}

export interface PublicationPresentation {
  deliverable: ArtifactDeliverable
  title: string
  shortTitle: string
  eyebrow: string
  description: string
  folio: string
  artifacts: ArtifactPresentation[]
  htmlPreview: ArtifactPresentation | null
  htmlPreviewUnavailableReason: string | null
  isInstructorOnly: boolean
}

/**
 * Check path- and header-adjacent manifest fields again in the browser.
 *
 * The backend already validates the generated contract. This small runtime
 * guard exists because cached data, extensions, or a future client regression
 * must not turn malformed metadata into a download or preview action.
 */
function isValidArtifactMetadata(
  value: ArtifactMetadataPublic,
): value is ArtifactMetadataPublic {
  const expectedMediaType = EXPECTED_MEDIA_TYPE_BASES[value.format]
  const mediaTypeBase =
    typeof value.media_type === "string"
      ? value.media_type.toLowerCase().split(";", 1)[0]?.trim()
      : undefined
  return (
    typeof value.artifact_id === "string" &&
    value.artifact_id.length > 0 &&
    value.artifact_id.length <= 255 &&
    /^[A-Za-z0-9._:-]+$/.test(value.artifact_id) &&
    typeof value.file_name === "string" &&
    value.file_name.length > 0 &&
    value.file_name.length <= 255 &&
    !/[\\/]/.test(value.file_name) &&
    !hasControlCharacters(value.file_name) &&
    typeof value.size_bytes === "number" &&
    Number.isSafeInteger(value.size_bytes) &&
    value.size_bytes >= 0 &&
    typeof expectedMediaType === "string" &&
    mediaTypeBase === expectedMediaType &&
    typeof value.download_url === "string" &&
    value.download_url.length > 0
  )
}

function validateManifestTopology(manifest: ArtifactManifestPublic): void {
  if (
    !Array.isArray(manifest.deliverables) ||
    manifest.deliverables.length !== DELIVERABLE_ORDER.length
  ) {
    throw new ManifestPresentationError(
      "The results manifest must contain four publications.",
    )
  }
  if (
    manifest.schema_version !== "1.0" ||
    typeof manifest.job_id !== "string" ||
    manifest.job_id.length === 0 ||
    !Array.isArray(manifest.deliverables)
  ) {
    throw new ManifestPresentationError()
  }

  const observedDeliverables = manifest.deliverables.map(
    ({ deliverable }) => deliverable,
  )
  if (
    observedDeliverables.some(
      (deliverable, index) => deliverable !== DELIVERABLE_ORDER[index],
    )
  ) {
    throw new ManifestPresentationError()
  }

  const observedArtifactIds = new Set<string>()
  for (const group of manifest.deliverables) {
    if (
      !Array.isArray(group.artifacts) ||
      group.artifacts.length < 1 ||
      group.artifacts.length > FORMAT_ORDER.length
    ) {
      throw new ManifestPresentationError()
    }
    const groupFormats = new Set<ArtifactFormat>()
    for (const artifact of group.artifacts) {
      if (
        !isValidArtifactMetadata(artifact) ||
        groupFormats.has(artifact.format) ||
        observedArtifactIds.has(artifact.artifact_id)
      ) {
        throw new ManifestPresentationError(
          "The results manifest contains invalid artifact metadata.",
        )
      }
      groupFormats.add(artifact.format)
      observedArtifactIds.add(artifact.artifact_id)
    }
  }
}

/**
 * Map an integrity-checked manifest into a deterministic learner presentation.
 */
export function buildPublicationPresentations(
  manifest: ArtifactManifestPublic,
  htmlPreviewMaximumBytes: number,
): PublicationPresentation[] {
  validateManifestTopology(manifest)
  if (
    !Number.isSafeInteger(htmlPreviewMaximumBytes) ||
    htmlPreviewMaximumBytes <= 0
  ) {
    throw new ManifestPresentationError()
  }

  return manifest.deliverables.map((group) => {
    const definition = PUBLICATION_DEFINITIONS[group.deliverable]
    const artifacts = group.artifacts
      .map<ArtifactPresentation>((artifact) => ({
        ...artifact,
        formatLabel: ARTIFACT_FORMAT_LABELS[artifact.format],
        sizeLabel: formatArtifactByteSize(artifact.size_bytes),
      }))
      .sort(
        (firstArtifact, secondArtifact) =>
          FORMAT_ORDER.indexOf(firstArtifact.format) -
          FORMAT_ORDER.indexOf(secondArtifact.format),
      )
    const htmlArtifact =
      artifacts.find(({ format }) => format === "html") ?? null
    const isHtmlWithinPreviewLimit =
      htmlArtifact !== null &&
      htmlArtifact.size_bytes <= htmlPreviewMaximumBytes

    return {
      deliverable: group.deliverable,
      ...definition,
      artifacts,
      htmlPreview: isHtmlWithinPreviewLimit ? htmlArtifact : null,
      htmlPreviewUnavailableReason:
        htmlArtifact !== null && !isHtmlWithinPreviewLimit
          ? `HTML files above ${formatArtifactByteSize(
              htmlPreviewMaximumBytes,
            ).replace(
              " MB",
              " MiB",
            )} remain available for download but cannot be previewed here.`
          : null,
      isInstructorOnly: group.deliverable === "answer_key",
    }
  })
}

/** Present base-two file sizes with at most one meaningful decimal place. */
export function formatArtifactByteSize(sizeBytes: number): string {
  if (!Number.isFinite(sizeBytes) || sizeBytes <= 0) {
    return "0 B"
  }
  const units = ["B", "KB", "MB", "GB"] as const
  const unitIndex = Math.min(
    Math.floor(Math.log(sizeBytes) / Math.log(1024)),
    units.length - 1,
  )
  const scaledValue = sizeBytes / 1024 ** unitIndex
  const roundedValue =
    unitIndex === 0
      ? Math.round(scaledValue)
      : Math.round(scaledValue * 10) / 10
  return `${roundedValue.toLocaleString("en-US")} ${units[unitIndex]}`
}

/** Return a navigable source only for explicit web protocols. */
export function getSafeExternalSourceUrl(rawUrl: string | null): string | null {
  if (rawUrl === null) {
    return null
  }
  try {
    const parsedUrl = new URL(rawUrl)
    return parsedUrl.protocol === "https:" || parsedUrl.protocol === "http:"
      ? parsedUrl.href
      : null
  } catch {
    return null
  }
}
