import { describe, expect, it, vi } from "vitest"

import { type JobLibraryPublic, JobsService } from "@/client"
import { ApiError } from "@/lib/api-error"
import {
  getLibraryPollingInterval,
  getLibraryQueryOptions,
  libraryQueryKey,
} from "./queries"

const libraryPage = (status: JobLibraryPublic["data"][number]["status"]) =>
  ({
    data: [{ job_id: "job-library", status }],
    next_cursor: null,
  }) as JobLibraryPublic

describe("course library query policy", () => {
  it("uses the generated owner collection and passes opaque cursors", async () => {
    const listSpy = vi
      .spyOn(JobsService, "listJobs")
      .mockResolvedValue(libraryPage("completed"))
    const options = getLibraryQueryOptions()

    expect(libraryQueryKey).toEqual(["course-library"])
    await options.queryFn?.({ pageParam: "opaque-next-page" } as never)
    expect(listSpy).toHaveBeenCalledWith({
      query: { cursor: "opaque-next-page", limit: 12 },
    })
  })

  it("polls only while the document is visible and a loaded job is active", () => {
    expect(
      getLibraryPollingInterval({
        pages: [libraryPage("researching")],
        isDocumentVisible: true,
      }),
    ).toBe(5000)
    expect(
      getLibraryPollingInterval({
        pages: [libraryPage("researching")],
        isDocumentVisible: false,
      }),
    ).toBe(false)
    expect(
      getLibraryPollingInterval({
        pages: [libraryPage("completed"), libraryPage("failed")],
        isDocumentVisible: true,
      }),
    ).toBe(false)
  })

  it("retries transient collection reads but stops on permanent errors", () => {
    const retry = getLibraryQueryOptions().retry
    expect(typeof retry).toBe("function")
    if (typeof retry !== "function") {
      throw new Error("The library retry policy must remain callable.")
    }

    const transientError = new ApiError({
      body: {},
      status: 503,
      url: "/api/v1/jobs",
    })
    const permanentError = new ApiError({
      body: {},
      status: 422,
      url: "/api/v1/jobs",
    })
    expect(retry(0, transientError)).toBe(true)
    expect(retry(0, permanentError)).toBe(false)
    expect(retry(5, transientError)).toBe(false)
  })
})
