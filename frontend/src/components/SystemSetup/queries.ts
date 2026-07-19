import { queryOptions } from "@tanstack/react-query"

import { type SystemAuthenticationState, SystemService } from "@/client"

export const SYSTEM_READINESS_QUERY_KEY = ["system", "readiness"] as const
export const SYSTEM_AUTHENTICATION_QUERY_KEY = [
  "system",
  "authentication",
] as const

const AUTHENTICATION_POLL_INTERVAL_MS = 1000

/**
 * Poll only while the package has an active device ceremony. Returning false
 * for every other state makes terminal stop behavior explicit and prevents a
 * signed-out setup page from producing background traffic forever.
 */
export function getSystemAuthenticationPollingInterval(
  state: SystemAuthenticationState | undefined,
): number | false {
  return state === "waiting_for_user" ? AUTHENTICATION_POLL_INTERVAL_MS : false
}

export function getSystemReadinessQueryOptions() {
  return queryOptions({
    queryKey: SYSTEM_READINESS_QUERY_KEY,
    queryFn: () => SystemService.readSystemReadiness(),
    staleTime: 5000,
    refetchOnWindowFocus: false,
  })
}

export function getSystemAuthenticationQueryOptions() {
  return queryOptions({
    queryKey: SYSTEM_AUTHENTICATION_QUERY_KEY,
    queryFn: () => SystemService.readSystemAuthenticationStatus(),
    refetchInterval: (query) =>
      getSystemAuthenticationPollingInterval(query.state.data?.state),
    refetchIntervalInBackground: false,
    refetchOnWindowFocus: false,
  })
}
