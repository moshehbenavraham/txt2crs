import { describe, expect, it } from "vitest"

import type {
  ArtifactDeliverable,
  ArtifactFormat,
  ArtifactManifestPublic,
  ArtifactMetadataPublic,
} from "@/client"
import {
  buildPublicationPresentations,
  formatArtifactByteSize,
  getSafeExternalSourceUrl,
  ManifestPresentationError,
} from "./presentation"

const deliverables: ArtifactDeliverable[] = [
  "course",
  "review_pack",
  "assessment",
  "answer_key",
]
const formats: ArtifactFormat[] = ["html", "markdown", "pdf", "docx"]

function artifact(
  deliverable: ArtifactDeliverable,
  format: ArtifactFormat,
  sizeBytes = 1024,
): ArtifactMetadataPublic {
  const mediaTypes: Record<ArtifactFormat, string> = {
    html: "text/html; charset=utf-8",
    markdown: "text/markdown; charset=utf-8",
    pdf: "application/pdf",
    docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  }
  return {
    artifact_id: `${deliverable}_${format}`,
    format,
    file_name: `${deliverable}.${format === "markdown" ? "md" : format}`,
    media_type: mediaTypes[format],
    size_bytes: sizeBytes,
    content_hash: `sha256:${"a".repeat(64)}`,
    download_url: `/api/v1/jobs/job-results/artifacts/${deliverable}_${format}`,
  }
}

function completeManifest(): ArtifactManifestPublic {
  return {
    schema_version: "1.0",
    job_id: "job-results",
    created_at: "2026-07-20T00:00:00Z",
    deliverables: deliverables.map((deliverable) => ({
      deliverable,
      // The server orders artifact IDs, not presentation formats. The mapper
      // must establish a stable learner-facing order independently.
      artifacts: [...formats]
        .reverse()
        .map((format) => artifact(deliverable, format)),
    })),
  }
}

describe("results manifest presentation", () => {
  it("maps exactly four publications and sixteen formats in product order", () => {
    const publications = buildPublicationPresentations(
      completeManifest(),
      5_242_880,
    )

    expect(publications.map(({ deliverable }) => deliverable)).toEqual(
      deliverables,
    )
    expect(publications.flatMap(({ artifacts }) => artifacts)).toHaveLength(16)
    for (const publication of publications) {
      expect(publication.artifacts.map(({ format }) => format)).toEqual(formats)
      expect(publication.htmlPreview?.format).toBe("html")
    }
  })

  it("keeps an exact-cap HTML artifact previewable and rejects one byte over", () => {
    const manifest = completeManifest()
    manifest.deliverables[0]!.artifacts = [
      artifact("course", "html", 5_242_880),
    ]
    manifest.deliverables[1]!.artifacts = [
      artifact("review_pack", "html", 5_242_881),
    ]

    const publications = buildPublicationPresentations(manifest, 5_242_880)
    expect(publications[0]?.htmlPreview).not.toBeNull()
    expect(publications[1]?.htmlPreview).toBeNull()
    expect(publications[1]?.htmlPreviewUnavailableReason).toMatch(/5 MiB/i)
  })

  it("fails closed for duplicate, missing, or malformed publication data", () => {
    const duplicate = completeManifest()
    duplicate.deliverables[1] = duplicate.deliverables[0]!
    expect(() => buildPublicationPresentations(duplicate, 5_242_880)).toThrow(
      ManifestPresentationError,
    )

    const missing = completeManifest()
    missing.deliverables.pop()
    expect(() => buildPublicationPresentations(missing, 5_242_880)).toThrow(
      /four publications/i,
    )

    const invalidSize = completeManifest()
    invalidSize.deliverables[0]!.artifacts[0]!.size_bytes = -1
    expect(() => buildPublicationPresentations(invalidSize, 5_242_880)).toThrow(
      /artifact metadata/i,
    )

    const mediaTypePrefixOnly = completeManifest()
    const htmlArtifact = mediaTypePrefixOnly.deliverables[0]!.artifacts.find(
      ({ format }) => format === "html",
    )
    if (htmlArtifact === undefined) {
      throw new Error("The complete test manifest must include HTML.")
    }
    htmlArtifact.media_type = "text/html-malicious"
    expect(() =>
      buildPublicationPresentations(mediaTypePrefixOnly, 5_242_880),
    ).toThrow(/artifact metadata/i)
  })

  it("formats bytes without implying precision the manifest does not provide", () => {
    expect(formatArtifactByteSize(0)).toBe("0 B")
    expect(formatArtifactByteSize(1024)).toBe("1 KB")
    expect(formatArtifactByteSize(1_572_864)).toBe("1.5 MB")
  })

  it("allows only HTTP(S) source links", () => {
    expect(getSafeExternalSourceUrl("https://docs.python.org/3/")).toBe(
      "https://docs.python.org/3/",
    )
    expect(getSafeExternalSourceUrl("http://example.test/reference")).toBe(
      "http://example.test/reference",
    )
    expect(getSafeExternalSourceUrl("javascript:alert(1)")).toBeNull()
    expect(getSafeExternalSourceUrl("file:///private/source")).toBeNull()
    expect(getSafeExternalSourceUrl("not a URL")).toBeNull()
  })
})
