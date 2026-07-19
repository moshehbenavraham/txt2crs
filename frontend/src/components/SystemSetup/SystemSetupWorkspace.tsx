import {
  useMutation,
  useQueryClient,
  useSuspenseQueries,
} from "@tanstack/react-query"
import { useEffect, useState } from "react"

import { SystemService } from "@/client"
import { getApiErrorMessage } from "@/lib/api-error"
import { AuthenticationPanel } from "./AuthenticationPanel"
import { getAuthenticationDisplay, getReadinessDisplay } from "./presentation"
import {
  getSystemAuthenticationQueryOptions,
  getSystemReadinessQueryOptions,
  SYSTEM_AUTHENTICATION_QUERY_KEY,
  SYSTEM_READINESS_QUERY_KEY,
} from "./queries"
import { ReadinessOverview } from "./ReadinessOverview"
import { RecoveryPanel } from "./RecoveryPanel"
import { SystemChecklist } from "./SystemChecklist"

export function SystemSetupWorkspace() {
  const queryClient = useQueryClient()
  const [copyAnnouncement, setCopyAnnouncement] = useState("")
  const [readinessQuery, authenticationQuery] = useSuspenseQueries({
    // These cache reads are independent. Starting them together prevents a
    // request waterfall and mirrors the backend's detached state boundary.
    queries: [
      getSystemReadinessQueryOptions(),
      getSystemAuthenticationQueryOptions(),
    ],
  })
  const readiness = readinessQuery.data
  const authentication = authenticationQuery.data
  const readinessDisplay = getReadinessDisplay(readiness)
  const authenticationDisplay = getAuthenticationDisplay(authentication.state)

  const startAuthentication = useMutation({
    mutationFn: () => SystemService.startSystemAuthentication(),
    onMutate: () => {
      setCopyAnnouncement("")
    },
    onSuccess: (startedAuthentication) => {
      // The response is server state. Write it into the existing query cache
      // instead of duplicating it in component state; waiting data enables the
      // query's finite status polling.
      queryClient.setQueryData(
        SYSTEM_AUTHENTICATION_QUERY_KEY,
        startedAuthentication,
      )
    },
  })

  useEffect(() => {
    if (authentication.state === "authenticated") {
      // A completed ceremony may change aggregate readiness. Refresh only the
      // detached readiness endpoint; never infer readiness from auth alone.
      queryClient.invalidateQueries({
        queryKey: SYSTEM_READINESS_QUERY_KEY,
      })
    }
  }, [authentication.state, queryClient])

  return (
    <section aria-label="System status" className="flex min-w-0 flex-col gap-6">
      <p
        className="sr-only"
        role="status"
        aria-live="polite"
        aria-atomic="true"
      >
        {readinessDisplay.title}. {authenticationDisplay.title}.
        {copyAnnouncement ? ` ${copyAnnouncement}.` : ""}
      </p>

      <ReadinessOverview readiness={readiness} />

      <div className="grid min-w-0 items-stretch gap-6 *:min-w-0 lg:grid-cols-[minmax(0,1.12fr)_minmax(20rem,0.88fr)]">
        <AuthenticationPanel
          authentication={authentication}
          isStarting={startAuthentication.isPending}
          startErrorMessage={
            startAuthentication.error
              ? getApiErrorMessage(startAuthentication.error)
              : undefined
          }
          onStart={() => startAuthentication.mutate()}
          onCopyAnnouncement={setCopyAnnouncement}
        />
        <RecoveryPanel readiness={readiness} />
      </div>

      <SystemChecklist checks={readiness.checks} />
    </section>
  )
}
