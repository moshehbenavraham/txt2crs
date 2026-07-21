import { describe, expect, it, vi } from "vitest"

import { type JobStatusPublic, JobsService } from "@/client"
import { ApiError } from "@/lib/api-error"
import {
  chooseLatestJobSnapshot,
  getJobPollingInterval,
  getJobQueryOptions,
  getTransientRetryDelay,
  isTransientJobReadError,
  jobQueryKey,
  subscribeToJobVisibility,
} from "./queries"

const jobSnapshot = (status: JobStatusPublic["status"]): JobStatusPublic =>
  ({
    job_id: "job-progress",
    status,
    revision: 2,
    runtime_activity_at: "2026-07-21T10:01:00Z",
  }) as JobStatusPublic

describe("course job query policy", () => {
  it("uses an owner-job-scoped cache key and generated query function", async () => {
    const readSpy = vi
      .spyOn(JobsService, "readJob")
      .mockResolvedValue(jobSnapshot("accepted"))
    const options = getJobQueryOptions("job-progress")

    expect(jobQueryKey("job-progress")).toEqual(["course-jobs", "job-progress"])
    await options.queryFn?.({} as never)
    expect(readSpy).toHaveBeenCalledWith({
      path: { job_id: "job-progress" },
    })
  })

  it.each([
    "accepted",
    "researching",
    "drafting",
    "validating",
    "rendering",
    "delivering",
  ] as const)(
    "polls visible non-terminal %s jobs every 5 seconds",
    (status) => {
      expect(
        getJobPollingInterval({
          snapshot: jobSnapshot(status),
          isDocumentVisible: true,
          transientFailureCount: 0,
        }),
      ).toBe(5000)
    },
  )

  it("slows hidden polling and caps transient backoff at 30 seconds", () => {
    expect(
      getJobPollingInterval({
        snapshot: jobSnapshot("drafting"),
        isDocumentVisible: false,
        transientFailureCount: 0,
      }),
    ).toBe(30_000)
    expect(getTransientRetryDelay(1)).toBe(5000)
    expect(getTransientRetryDelay(2)).toBe(10_000)
    expect(getTransientRetryDelay(20)).toBe(30_000)
  })

  it.each(["completed", "failed", "cancelled"] as const)(
    "stops immediately for terminal %s jobs",
    (status) => {
      expect(
        getJobPollingInterval({
          snapshot: jobSnapshot(status),
          isDocumentVisible: true,
          transientFailureCount: 8,
        }),
      ).toBe(false)
    },
  )

  it("uses the last safe snapshot while transiently reconnecting", () => {
    expect(
      getJobPollingInterval({
        snapshot: jobSnapshot("researching"),
        isDocumentVisible: true,
        transientFailureCount: 3,
      }),
    ).toBe(20_000)
    expect(
      getJobPollingInterval({
        snapshot: undefined,
        isDocumentVisible: true,
        transientFailureCount: 1,
      }),
    ).toBe(5000)
  })

  it("keeps the newest revision and rejects cross-job snapshots", () => {
    const revisionTwo = jobSnapshot("researching")
    const staleRevision = { ...revisionTwo, revision: 1 }
    const nextRevision: JobStatusPublic = {
      ...revisionTwo,
      revision: 3,
      status: "drafting",
    }

    expect(chooseLatestJobSnapshot(revisionTwo, staleRevision)).toBe(
      revisionTwo,
    )
    expect(chooseLatestJobSnapshot(revisionTwo, nextRevision)).toBe(
      nextRevision,
    )
    expect(
      chooseLatestJobSnapshot(revisionTwo, {
        ...nextRevision,
        job_id: "another-job",
      }),
    ).toBe(revisionTwo)
  })

  it("accepts a newer runtime heartbeat without inventing a checkpoint revision", () => {
    const previousSnapshot = jobSnapshot("drafting")
    const heartbeatSnapshot = {
      ...previousSnapshot,
      runtime_activity_at: "2026-07-21T10:01:05Z",
    }
    const staleHeartbeatSnapshot = {
      ...previousSnapshot,
      runtime_activity_at: "2026-07-21T10:00:55Z",
    }

    expect(chooseLatestJobSnapshot(previousSnapshot, heartbeatSnapshot)).toBe(
      heartbeatSnapshot,
    )
    expect(
      chooseLatestJobSnapshot(previousSnapshot, staleHeartbeatSnapshot),
    ).toBe(previousSnapshot)
  })

  it("retries only transient reads and revalidates on direct re-entry", () => {
    const options = getJobQueryOptions("job-progress")

    expect(
      isTransientJobReadError(
        new ApiError({
          body: {},
          status: 500,
          url: "/api/v1/jobs/job-progress",
        }),
      ),
    ).toBe(true)
    expect(
      isTransientJobReadError(
        new ApiError({
          body: {},
          status: 404,
          url: "/api/v1/jobs/job-progress",
        }),
      ),
    ).toBe(false)
    expect(options.refetchOnMount).toBe("always")
    expect(options.refetchOnReconnect).toBe("always")
  })

  it("removes its visibility listener on cleanup", () => {
    const visibilityTarget = new EventTarget()
    let visibilityState: DocumentVisibilityState = "hidden"
    const onVisible = vi.fn()
    const unsubscribe = subscribeToJobVisibility({
      target: visibilityTarget,
      getVisibilityState: () => visibilityState,
      onVisible,
    })

    visibilityTarget.dispatchEvent(new Event("visibilitychange"))
    expect(onVisible).not.toHaveBeenCalled()
    visibilityState = "visible"
    visibilityTarget.dispatchEvent(new Event("visibilitychange"))
    expect(onVisible).toHaveBeenCalledTimes(1)

    unsubscribe()
    visibilityTarget.dispatchEvent(new Event("visibilitychange"))
    expect(onVisible).toHaveBeenCalledTimes(1)
  })
})
