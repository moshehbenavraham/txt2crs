import { queryOptions, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useMemo } from "react"

import { type JobStatusPublic, JobsService } from "@/client"
import { ApiError } from "@/lib/api-error"
import type { JobId } from "@/lib/types"

const VISIBLE_POLLING_INTERVAL_MILLISECONDS = 1_500
const HIDDEN_POLLING_INTERVAL_MILLISECONDS = 10_000
const MAXIMUM_TRANSIENT_RETRY_DELAY_MILLISECONDS = 30_000
const MAXIMUM_AUTOMATIC_TRANSIENT_RETRIES = 5

export const jobQueryKey = (jobId: string) => ["course-jobs", jobId] as const

function isTerminalJobStatus(status: JobStatusPublic["status"]): boolean {
  switch (status) {
    case "completed":
    case "failed":
    case "cancelled":
      return true
    case "accepted":
    case "researching":
    case "drafting":
    case "validating":
    case "rendering":
    case "delivering":
      return false
    default: {
      // A generated status addition must receive an explicit polling decision.
      const exhaustiveStatus: never = status
      return exhaustiveStatus
    }
  }
}

/** Exponential transient delay where failure number one waits one base tick. */
export function getTransientRetryDelay(failureCount: number): number {
  const boundedFailureCount = Math.max(1, Math.floor(failureCount))
  return Math.min(
    VISIBLE_POLLING_INTERVAL_MILLISECONDS * 2 ** (boundedFailureCount - 1),
    MAXIMUM_TRANSIENT_RETRY_DELAY_MILLISECONDS,
  )
}

interface JobPollingIntervalInput {
  snapshot: JobStatusPublic | undefined
  isDocumentVisible: boolean
  transientFailureCount: number
}

/**
 * Resolve one finite polling interval from server status and browser state.
 *
 * A last safe terminal snapshot always wins. During reconnecting, the larger
 * of visibility cadence and transient backoff prevents a hidden tab from
 * becoming more aggressive than a visible one.
 */
export function getJobPollingInterval({
  snapshot,
  isDocumentVisible,
  transientFailureCount,
}: JobPollingIntervalInput): number | false {
  if (snapshot && isTerminalJobStatus(snapshot.status)) {
    return false
  }

  const visibilityInterval = isDocumentVisible
    ? VISIBLE_POLLING_INTERVAL_MILLISECONDS
    : HIDDEN_POLLING_INTERVAL_MILLISECONDS
  if (transientFailureCount <= 0) {
    return visibilityInterval
  }
  return Math.max(
    visibilityInterval,
    getTransientRetryDelay(transientFailureCount),
  )
}

/** Keep an already-rendered snapshot from moving backward or across jobs. */
export function chooseLatestJobSnapshot(
  previousSnapshot: JobStatusPublic | undefined,
  incomingSnapshot: JobStatusPublic,
): JobStatusPublic {
  if (!previousSnapshot) {
    return incomingSnapshot
  }
  if (
    incomingSnapshot.job_id !== previousSnapshot.job_id ||
    incomingSnapshot.revision <= previousSnapshot.revision
  ) {
    return previousSnapshot
  }
  return incomingSnapshot
}

/** Retry connectivity/server failures, never ownership or validation failures. */
export function isTransientJobReadError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return (
      error.status === 0 ||
      error.status === 408 ||
      error.status === 429 ||
      error.status >= 500
    )
  }
  return error instanceof Error
}

function isCurrentDocumentVisible(): boolean {
  return (
    typeof document === "undefined" || document.visibilityState === "visible"
  )
}

export function getJobQueryOptions(jobId: string) {
  return queryOptions<
    JobStatusPublic,
    Error,
    JobStatusPublic,
    ReturnType<typeof jobQueryKey>
  >({
    queryKey: jobQueryKey(jobId),
    queryFn: () => JobsService.readJob({ path: { job_id: jobId } }),
    staleTime: 0,
    refetchOnMount: "always",
    refetchOnReconnect: "always",
    refetchOnWindowFocus: "always",
    refetchIntervalInBackground: true,
    retry: (failureCount, error) =>
      failureCount < MAXIMUM_AUTOMATIC_TRANSIENT_RETRIES &&
      isTransientJobReadError(error),
    // TanStack passes a zero-based attempt index; the product policy is easier
    // to review as a one-based failure count.
    retryDelay: (attemptIndex) => getTransientRetryDelay(attemptIndex + 1),
    refetchInterval: (query) =>
      getJobPollingInterval({
        snapshot: query.state.data,
        isDocumentVisible: isCurrentDocumentVisible(),
        transientFailureCount: query.state.fetchFailureCount,
      }),
    // TanStack intentionally exposes structural-sharing values as unknown.
    // This query's generated queryFn fixes both values to JobStatusPublic.
    structuralSharing: (previousData, incomingData) =>
      chooseLatestJobSnapshot(
        previousData as JobStatusPublic | undefined,
        incomingData as JobStatusPublic,
      ),
  })
}

interface JobVisibilitySubscription {
  target: Pick<EventTarget, "addEventListener" | "removeEventListener">
  getVisibilityState: () => DocumentVisibilityState
  onVisible: () => void
}

/**
 * Subscribe to visible re-entry and return the exact listener cleanup.
 *
 * Keeping this adapter separate makes lifecycle behavior testable without a
 * browser DOM. TanStack owns and disposes the query's interval timer.
 */
export function subscribeToJobVisibility({
  target,
  getVisibilityState,
  onVisible,
}: JobVisibilitySubscription): () => void {
  const handleVisibilityChange = () => {
    if (getVisibilityState() === "visible") {
      onVisible()
    }
  }
  target.addEventListener("visibilitychange", handleVisibilityChange)
  return () => {
    target.removeEventListener("visibilitychange", handleVisibilityChange)
  }
}

/** Owner-scoped progress query with explicit visible revalidation cleanup. */
export function useJobProgressQuery(jobId: JobId) {
  const queryClient = useQueryClient()
  const queryKey = useMemo(() => jobQueryKey(jobId), [jobId])

  useEffect(() => {
    if (typeof document === "undefined") {
      return
    }
    return subscribeToJobVisibility({
      target: document,
      getVisibilityState: () => document.visibilityState,
      onVisible: () => {
        void queryClient.refetchQueries({
          queryKey,
          exact: true,
          type: "active",
        })
      },
    })
  }, [queryClient, queryKey])

  return useQuery(getJobQueryOptions(jobId))
}
