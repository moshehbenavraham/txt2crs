import {
  infiniteQueryOptions,
  useInfiniteQuery,
  useQueryClient,
} from "@tanstack/react-query"
import { useEffect } from "react"

import { type JobLibraryPublic, JobsService } from "@/client"
import {
  getTransientRetryDelay,
  isTransientJobReadError,
} from "@/components/CourseProgress/queries"

const LIBRARY_PAGE_SIZE = 12
const VISIBLE_LIBRARY_POLLING_INTERVAL_MILLISECONDS = 5_000
const MAXIMUM_AUTOMATIC_TRANSIENT_RETRIES = 5

export const libraryQueryKey = ["course-library"] as const

function isActiveLibraryStatus(
  status: JobLibraryPublic["data"][number]["status"],
): boolean {
  switch (status) {
    case "accepted":
    case "researching":
    case "drafting":
    case "validating":
    case "rendering":
    case "delivering":
      return true
    case "completed":
    case "failed":
    case "cancelled":
      return false
    default: {
      const exhaustiveStatus: never = status
      return exhaustiveStatus
    }
  }
}

interface LibraryPollingIntervalInput {
  pages: JobLibraryPublic[]
  isDocumentVisible: boolean
}

/** Poll only when visible loaded rows contain work that can still advance. */
export function getLibraryPollingInterval({
  pages,
  isDocumentVisible,
}: LibraryPollingIntervalInput): number | false {
  if (!isDocumentVisible) {
    return false
  }
  const hasActiveJob = pages.some((page) =>
    page.data.some((job) => isActiveLibraryStatus(job.status)),
  )
  return hasActiveJob ? VISIBLE_LIBRARY_POLLING_INTERVAL_MILLISECONDS : false
}

function isCurrentDocumentVisible(): boolean {
  return (
    typeof document === "undefined" || document.visibilityState === "visible"
  )
}

export function getLibraryQueryOptions() {
  return infiniteQueryOptions({
    queryKey: libraryQueryKey,
    initialPageParam: null as string | null,
    queryFn: ({ pageParam }) =>
      JobsService.listJobs({
        query: {
          limit: LIBRARY_PAGE_SIZE,
          ...(pageParam ? { cursor: pageParam } : {}),
        },
      }),
    getNextPageParam: (lastPage) => lastPage.next_cursor,
    staleTime: 0,
    refetchOnMount: "always",
    refetchOnReconnect: "always",
    refetchOnWindowFocus: "always",
    refetchIntervalInBackground: false,
    retry: (failureCount, error) =>
      failureCount < MAXIMUM_AUTOMATIC_TRANSIENT_RETRIES &&
      isTransientJobReadError(error),
    retryDelay: (attemptIndex) => getTransientRetryDelay(attemptIndex + 1),
    refetchInterval: (query) =>
      getLibraryPollingInterval({
        pages: query.state.data?.pages ?? [],
        isDocumentVisible: isCurrentDocumentVisible(),
      }),
  })
}

/** Owner-scoped cursor query with immediate visible-tab revalidation. */
export function useCourseLibraryQuery() {
  const queryClient = useQueryClient()

  useEffect(() => {
    if (typeof document === "undefined") {
      return
    }
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        void queryClient.refetchQueries({
          queryKey: libraryQueryKey,
          exact: true,
          type: "active",
        })
      }
    }
    document.addEventListener("visibilitychange", handleVisibilityChange)
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange)
    }
  }, [queryClient])

  return useInfiniteQuery(getLibraryQueryOptions())
}
