import { renderToStaticMarkup } from "react-dom/server"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { JobStatusPublic } from "@/client"
import type { JobId } from "@/lib/types"

const { artifactQueryMock } = vi.hoisted(() => ({
  artifactQueryMock: vi.fn(),
}))

vi.mock("./queries", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./queries")>()),
  useArtifactManifestQuery: artifactQueryMock,
}))

vi.mock("./useArtifactTransfer", () => ({
  useArtifactTransfer: () => ({
    loadArtifact: vi.fn(),
    isArtifactLoading: () => false,
    errorMessage: null,
    clearError: vi.fn(),
  }),
}))

import { CourseResultsWorkspace } from "./CourseResultsWorkspace"

const inconsistentCompletedSnapshot = {
  job_id: "job-results",
  status: "completed",
  artifacts: {
    available: true,
    count: 16,
    manifest_url: null,
  },
} as JobStatusPublic

describe("completed results workspace states", () => {
  beforeEach(() => {
    artifactQueryMock.mockReturnValue({
      data: undefined,
      isPending: true,
      isFetching: false,
      refetch: vi.fn(),
    })
  })

  it("fails an inconsistent artifact advertisement without an infinite spinner", () => {
    const markup = renderToStaticMarkup(
      <CourseResultsWorkspace
        jobId={"job-results" as JobId}
        snapshot={inconsistentCompletedSnapshot}
      />,
    )

    expect(markup).toContain("Publication files are not available")
    expect(markup).not.toContain("Preparing the private publication index")
  })
})
