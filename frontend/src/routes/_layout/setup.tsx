import { QueryErrorResetBoundary, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { RefreshCw, TriangleAlert } from "lucide-react"
import { Suspense } from "react"
import { ErrorBoundary } from "react-error-boundary"

import { UsersService } from "@/client"
import { PageHeader } from "@/components/Common/PageHeader"
import PendingSystemSetup from "@/components/Pending/PendingSystemSetup"
import {
  SYSTEM_AUTHENTICATION_QUERY_KEY,
  SYSTEM_READINESS_QUERY_KEY,
} from "@/components/SystemSetup/queries"
import { SystemSetupWorkspace } from "@/components/SystemSetup/SystemSetupWorkspace"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { buildPageTitle } from "@/lib/branding"
import { CURRENT_USER_QUERY_KEY } from "@/lib/session"

export const Route = createFileRoute("/_layout/setup")({
  component: SystemSetupPage,
  beforeLoad: async ({ context }) => {
    // Guard at the route boundary so a normal authenticated user is redirected
    // before readiness or device-status requests can reveal operator state.
    const currentUser = await context.queryClient.ensureQueryData({
      queryKey: CURRENT_USER_QUERY_KEY,
      queryFn: () => UsersService.readUserMe(),
    })

    if (!currentUser.is_superuser) {
      throw redirect({ to: "/forbidden" })
    }
  },
  head: () => ({
    meta: [
      {
        title: buildPageTitle("System setup"),
      },
    ],
  }),
})

function SetupError({ onRetry }: { onRetry: () => void }) {
  return (
    <Alert variant="destructive">
      <TriangleAlert aria-hidden="true" />
      <AlertTitle>System setup could not load</AlertTitle>
      <AlertDescription>
        <p>
          The safe cached status is unavailable. Your account and navigation
          remain available.
        </p>
        <Button
          type="button"
          variant="outline"
          className="mt-3"
          onClick={onRetry}
        >
          Try again
        </Button>
      </AlertDescription>
    </Alert>
  )
}

function SystemSetupPage() {
  const queryClient = useQueryClient()

  const refreshSystemState = () =>
    Promise.all([
      queryClient.invalidateQueries({
        queryKey: SYSTEM_READINESS_QUERY_KEY,
      }),
      queryClient.invalidateQueries({
        queryKey: SYSTEM_AUTHENTICATION_QUERY_KEY,
      }),
    ])

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Operator workspace"
        title="System setup"
        description="Configure Codex authentication and verify every course-system dependency before learner work begins."
        actions={
          <Button
            type="button"
            variant="outline"
            className="h-11 sm:h-9"
            onClick={refreshSystemState}
          >
            <RefreshCw data-icon="inline-start" />
            Refresh status
          </Button>
        }
      />

      <QueryErrorResetBoundary>
        {({ reset }) => (
          <ErrorBoundary
            onReset={reset}
            fallbackRender={({ resetErrorBoundary }) => (
              <SetupError
                onRetry={() => {
                  queryClient.resetQueries({
                    queryKey: ["system"],
                  })
                  resetErrorBoundary()
                }}
              />
            )}
          >
            <Suspense fallback={<PendingSystemSetup />}>
              <SystemSetupWorkspace />
            </Suspense>
          </ErrorBoundary>
        )}
      </QueryErrorResetBoundary>
    </div>
  )
}
