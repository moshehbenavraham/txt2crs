import type { ArtifactFormat, ArtifactMetadataPublic } from "@/client"

const EXPECTED_MEDIA_TYPE_BASE: Record<ArtifactFormat, string> = {
  html: "text/html",
  markdown: "text/markdown",
  pdf: "application/pdf",
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

export class ArtifactTransferError extends Error {
  constructor() {
    super("The requested file could not be verified.")
    this.name = "ArtifactTransferError"
  }
}

export interface VerifiedArtifactTransfer {
  blob: Blob
  fileName: string
  mediaType: string
  sizeBytes: number
}

interface ObjectUrlApi {
  createObjectURL: (blob: Blob) => string
  revokeObjectURL: (url: string) => void
}

export interface TemporaryArtifactUrl {
  url: string
  release: () => void
}

function normalizeMediaType(mediaType: string): string {
  return mediaType
    .toLowerCase()
    .split(";")
    .map((part) => part.trim())
    .join(";")
}

function hasControlCharacters(value: string): boolean {
  return [...value].some((character) => {
    const characterCode = character.charCodeAt(0)
    return characterCode < 32 || (characterCode >= 127 && characterCode <= 159)
  })
}

function isSafeManifestFileName(fileName: string): boolean {
  return (
    fileName.length > 0 &&
    fileName.length <= 255 &&
    !/[\\/]/.test(fileName) &&
    !hasControlCharacters(fileName)
  )
}

function verifyMetadataMediaType(metadata: ArtifactMetadataPublic): string {
  const normalizedMediaType = normalizeMediaType(metadata.media_type)
  const mediaTypeBase = normalizedMediaType.split(";", 1)[0]
  if (
    mediaTypeBase !== EXPECTED_MEDIA_TYPE_BASE[metadata.format] ||
    !isSafeManifestFileName(metadata.file_name) ||
    !Number.isSafeInteger(metadata.size_bytes) ||
    metadata.size_bytes < 0
  ) {
    throw new ArtifactTransferError()
  }
  return normalizedMediaType
}

/**
 * Normalize the generated client's text/binary union and verify it against
 * the owner-private manifest before any download or preview side effect.
 */
export async function normalizeArtifactResponse(
  responseBody: string | Blob | File,
  metadata: ArtifactMetadataPublic,
): Promise<VerifiedArtifactTransfer> {
  const normalizedManifestMediaType = verifyMetadataMediaType(metadata)
  let artifactBlob: Blob

  if (typeof responseBody === "string") {
    if (metadata.format !== "html" && metadata.format !== "markdown") {
      throw new ArtifactTransferError()
    }
    artifactBlob = new Blob([responseBody], {
      type: normalizedManifestMediaType,
    })
  } else if (responseBody instanceof Blob) {
    const normalizedResponseMediaType = normalizeMediaType(responseBody.type)
    if (
      normalizedResponseMediaType.length === 0 ||
      normalizedResponseMediaType !== normalizedManifestMediaType
    ) {
      throw new ArtifactTransferError()
    }
    artifactBlob = responseBody
  } else {
    throw new ArtifactTransferError()
  }

  if (artifactBlob.size !== metadata.size_bytes) {
    throw new ArtifactTransferError()
  }

  return {
    blob: artifactBlob,
    fileName: metadata.file_name,
    mediaType: normalizedManifestMediaType,
    sizeBytes: artifactBlob.size,
  }
}

/**
 * Own a revocable URL with idempotent cleanup.
 *
 * Callers may release from close, navigation, and unmount without coordinating
 * which lifecycle path wins the race.
 */
export function createTemporaryArtifactUrl(
  artifactBlob: Blob,
  objectUrlApi: ObjectUrlApi = URL,
): TemporaryArtifactUrl {
  const url = objectUrlApi.createObjectURL(artifactBlob)
  let hasReleased = false
  return {
    url,
    release: () => {
      if (hasReleased) {
        return
      }
      hasReleased = true
      objectUrlApi.revokeObjectURL(url)
    },
  }
}
