import { QueryErrorResetBoundary } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Suspense } from "react"
import { ErrorBoundary } from "react-error-boundary"

import { LibraryIndex } from "@/components/Dashboard/LibraryIndex"
import { WorkspaceHeader } from "@/components/Dashboard/WorkspaceHeader"
import PendingDashboard from "@/components/Pending/PendingDashboard"
import { Button } from "@/components/ui/button"
import useAuth from "@/hooks/useAuth"
import { buildPageTitle } from "@/lib/branding"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: buildPageTitle("Dashboard"),
      },
    ],
  }),
})

/**
 * Inline problem surface: page identity, navigation, Settings, and Log out
 * stay available. Non-auth data errors never redirect to Login.
 */
function DashboardError({ onRetry }: { onRetry: () => void }) {
  return (
    <section
      aria-labelledby="dashboard-error-title"
      className="rounded-xl border border-border bg-surface-1 p-6 md:p-8"
    >
      <div className="flex max-w-md flex-col gap-2">
        <h2 id="dashboard-error-title" className="text-heading font-semibold">
          We could not load your library
        </h2>
        <p className="text-body-sm text-muted-foreground">
          Something went wrong while fetching your items. Your account and
          settings remain available.
        </p>
        <div className="mt-2">
          <Button variant="outline" onClick={onRetry}>
            Try again
          </Button>
        </div>
      </div>
    </section>
  )
}

function Dashboard() {
  const { user: currentUser } = useAuth()

  return (
    <div className="flex flex-col gap-(--space-section)">
      <WorkspaceHeader user={currentUser} />
      <QueryErrorResetBoundary>
        {({ reset }) => (
          <ErrorBoundary
            onReset={reset}
            fallbackRender={({ resetErrorBoundary }) => (
              <DashboardError onRetry={resetErrorBoundary} />
            )}
          >
            <Suspense fallback={<PendingDashboard />}>
              <LibraryIndex />
            </Suspense>
          </ErrorBoundary>
        )}
      </QueryErrorResetBoundary>
    </div>
  )
}
