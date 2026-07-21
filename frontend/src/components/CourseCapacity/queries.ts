import { queryOptions, useQuery } from "@tanstack/react-query"

import { JobsService } from "@/client"
import {
  getTransientRetryDelay,
  isTransientJobReadError,
} from "@/components/CourseProgress/queries"

export const admissionCapacityQueryKey = ["jobs", "admission-capacity"] as const

/** Owner capacity changes only after admission or rolling reservation expiry. */
export function getAdmissionCapacityQueryOptions() {
  return queryOptions({
    queryKey: admissionCapacityQueryKey,
    queryFn: () => JobsService.readAdmissionCapacity(),
    staleTime: 30_000,
    refetchOnMount: "always",
    refetchOnReconnect: "always",
    refetchOnWindowFocus: "always",
    retry: (failureCount, error) =>
      failureCount < 3 && isTransientJobReadError(error),
    retryDelay: (attemptIndex) => getTransientRetryDelay(attemptIndex + 1),
  })
}

export function useAdmissionCapacityQuery() {
  return useQuery(getAdmissionCapacityQueryOptions())
}
