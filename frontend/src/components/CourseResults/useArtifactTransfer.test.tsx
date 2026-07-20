import { describe, expect, it, vi } from "vitest"

import type { ArtifactMetadataPublic } from "@/client"
import {
  createArtifactTransferCoordinator,
  getArtifactTransferErrorMessage,
} from "./useArtifactTransfer"

const htmlArtifact: ArtifactMetadataPublic = {
  artifact_id: "course_html",
  format: "html",
  file_name: "course.html",
  media_type: "text/html; charset=utf-8",
  size_bytes: 13,
  content_hash: `sha256:${"a".repeat(64)}`,
  download_url: "/api/v1/jobs/job-results/artifacts/course_html",
}

describe("artifact transfer coordinator", () => {
  it("shares one generated-client request for duplicate triggers", async () => {
    let resolveTransfer: (value: string) => void = () => undefined
    const pendingTransfer = new Promise<string>((resolve) => {
      resolveTransfer = resolve
    })
    const download = vi.fn().mockReturnValue(pendingTransfer)
    const coordinator = createArtifactTransferCoordinator({ download })

    const firstTransfer = coordinator.load("job-results", htmlArtifact)
    const duplicateTransfer = coordinator.load("job-results", htmlArtifact)

    expect(duplicateTransfer).toBe(firstTransfer)
    expect(coordinator.isLoading(htmlArtifact.artifact_id)).toBe(true)
    expect(download).toHaveBeenCalledTimes(1)
    expect(download).toHaveBeenCalledWith({
      path: {
        job_id: "job-results",
        artifact_id: "course_html",
      },
      signal: expect.any(AbortSignal),
    })

    resolveTransfer("Hello course!")
    await expect(firstTransfer).resolves.toMatchObject({
      fileName: "course.html",
    })
    expect(coordinator.isLoading(htmlArtifact.artifact_id)).toBe(false)
  })

  it("releases the single-flight lock after failure so retry can proceed", async () => {
    const download = vi
      .fn()
      .mockRejectedValueOnce(new Error("private transport fact"))
      .mockResolvedValueOnce("Hello course!")
    const coordinator = createArtifactTransferCoordinator({ download })

    await expect(
      coordinator.load("job-results", htmlArtifact),
    ).rejects.toThrow()
    await expect(
      coordinator.load("job-results", htmlArtifact),
    ).resolves.toMatchObject({ fileName: "course.html" })
    expect(download).toHaveBeenCalledTimes(2)
  })

  it("uses fixed learner-safe error copy", () => {
    expect(
      getArtifactTransferErrorMessage(new Error("/private/path failed")),
    ).toBe("This file could not be prepared. Try again.")
  })
})
