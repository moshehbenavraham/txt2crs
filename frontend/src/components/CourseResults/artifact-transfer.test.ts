import { describe, expect, it } from "vitest"

import type { ArtifactMetadataPublic } from "@/client"
import {
  ArtifactTransferError,
  createTemporaryArtifactUrl,
  normalizeArtifactResponse,
} from "./artifact-transfer"

function metadata(
  overrides: Partial<ArtifactMetadataPublic> = {},
): ArtifactMetadataPublic {
  return {
    artifact_id: "course_html",
    format: "html",
    file_name: "course.html",
    media_type: "text/html; charset=utf-8",
    size_bytes: 13,
    content_hash: `sha256:${"a".repeat(64)}`,
    download_url: "/api/v1/jobs/job-results/artifacts/course_html",
    ...overrides,
  }
}

describe("artifact transfer verification", () => {
  it("normalizes generated text with exact UTF-8 bytes and media type", async () => {
    const verified = await normalizeArtifactResponse(
      "Hello course!",
      metadata(),
    )

    expect(verified.fileName).toBe("course.html")
    expect(verified.blob.size).toBe(13)
    expect(verified.blob.type).toBe("text/html;charset=utf-8")
  })

  it("accepts a matching binary Blob or File", async () => {
    const pdfBytes = new Blob(["pdf"], { type: "application/pdf" })
    const pdf = await normalizeArtifactResponse(
      pdfBytes,
      metadata({
        artifact_id: "course_pdf",
        format: "pdf",
        file_name: "course.pdf",
        media_type: "application/pdf",
        size_bytes: 3,
      }),
    )
    expect(pdf.blob).toBe(pdfBytes)

    const docxFile = new File(["docx"], "ignored-client-name.docx", {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    })
    const docx = await normalizeArtifactResponse(
      docxFile,
      metadata({
        artifact_id: "course_docx",
        format: "docx",
        file_name: "verified-course.docx",
        media_type:
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        size_bytes: 4,
      }),
    )
    expect(docx.fileName).toBe("verified-course.docx")
  })

  it("rejects byte, media, and filename mismatches with one safe error", async () => {
    await expect(
      normalizeArtifactResponse("too short", metadata()),
    ).rejects.toBeInstanceOf(ArtifactTransferError)
    await expect(
      normalizeArtifactResponse(
        new Blob(["abc"], { type: "application/pdf" }),
        metadata({ size_bytes: 3 }),
      ),
    ).rejects.toThrow(/could not be verified/i)
    await expect(
      normalizeArtifactResponse(
        "Hello course!",
        metadata({ file_name: "../private.html" }),
      ),
    ).rejects.toThrow(/could not be verified/i)
  })

  it("revokes a temporary object URL exactly once", () => {
    const revokedUrls: string[] = []
    const temporaryUrl = createTemporaryArtifactUrl(new Blob(["course"]), {
      createObjectURL: () => "blob:course-preview",
      revokeObjectURL: (url) => revokedUrls.push(url),
    })

    expect(temporaryUrl.url).toBe("blob:course-preview")
    temporaryUrl.release()
    temporaryUrl.release()
    expect(revokedUrls).toEqual(["blob:course-preview"])
  })
})
