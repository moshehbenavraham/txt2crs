import { afterEach, describe, expect, it, vi } from "vitest"

import {
  type ArtifactManifestPublic,
  type JobStatusPublic,
  JobsService,
} from "@/client"
import { ApiError } from "@/lib/api-error"
import {
  ArtifactManifestIntegrityError,
  artifactManifestQueryKey,
  getArtifactManifestQueryOptions,
  isTransientArtifactReadError,
  shouldLoadArtifactManifest,
} from "./queries"

const completedJob = {
  job_id: "job-results",
  status: "completed",
  artifacts: { available: true, count: 16, manifest_url: "/artifacts" },
} as JobStatusPublic

afterEach(() => {
  vi.restoreAllMocks()
})

describe("artifact manifest query policy", () => {
  it("enables only a completed job that advertises private artifacts", () => {
    expect(shouldLoadArtifactManifest(completedJob)).toBe(true)
    expect(
      shouldLoadArtifactManifest({
        ...completedJob,
        status: "delivering",
      }),
    ).toBe(false)
    expect(
      shouldLoadArtifactManifest({
        ...completedJob,
        artifacts: { available: false, count: 0, manifest_url: null },
      }),
    ).toBe(false)
    expect(
      shouldLoadArtifactManifest({
        ...completedJob,
        artifacts: { available: true, count: 16, manifest_url: null },
      }),
    ).toBe(false)
  })

  it("uses an owner-job key and the generated manifest operation", async () => {
    const manifest = {
      schema_version: "1.0",
      job_id: "job-results",
      deliverables: [],
    } as unknown as ArtifactManifestPublic
    const readSpy = vi
      .spyOn(JobsService, "readJobArtifacts")
      .mockResolvedValue(manifest)
    const options = getArtifactManifestQueryOptions("job-results", true)
    const requestController = new AbortController()

    expect(artifactManifestQueryKey("job-results")).toEqual([
      "course-jobs",
      "job-results",
      "artifacts",
    ])
    await options.queryFn?.({ signal: requestController.signal } as never)
    expect(readSpy).toHaveBeenCalledWith({
      path: { job_id: "job-results" },
      signal: requestController.signal,
    })
    expect(options.refetchInterval).toBe(false)
    expect(options.refetchOnMount).toBe("always")
  })

  it("fails a cross-job manifest once without retrying it as connectivity", async () => {
    vi.spyOn(JobsService, "readJobArtifacts").mockResolvedValue({
      schema_version: "1.0",
      job_id: "another-job",
      deliverables: [],
    } as unknown as ArtifactManifestPublic)
    const options = getArtifactManifestQueryOptions("job-results", true)
    const request = options.queryFn?.({
      signal: new AbortController().signal,
    } as never)

    await expect(request).rejects.toBeInstanceOf(ArtifactManifestIntegrityError)
    expect(
      isTransientArtifactReadError(new ArtifactManifestIntegrityError()),
    ).toBe(false)
  })

  it("retries only bounded transient failures", () => {
    const options = getArtifactManifestQueryOptions("job-results", true)
    const retry = options.retry
    if (typeof retry !== "function") {
      throw new Error("Artifact manifest retry must stay conditional.")
    }
    const unavailable = new ApiError({
      body: {},
      status: 503,
      url: "/api/v1/jobs/job-results/artifacts",
    })
    const denied = new ApiError({
      body: {},
      status: 404,
      url: "/api/v1/jobs/job-results/artifacts",
    })

    expect(isTransientArtifactReadError(unavailable)).toBe(true)
    expect(retry(0, unavailable)).toBe(true)
    expect(retry(2, unavailable)).toBe(false)
    expect(retry(0, denied)).toBe(false)
  })
})
