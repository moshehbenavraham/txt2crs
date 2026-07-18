import { useSuspenseQuery } from "@tanstack/react-query"
import { Link } from "@tanstack/react-router"
import { ArrowRight } from "lucide-react"
import type { ReactNode } from "react"

import { DashboardEmpty } from "@/components/Dashboard/DashboardEmpty"
import { LibraryPreview } from "@/components/Dashboard/LibraryPreview"
import {
  getDashboardItemsQueryOptions,
  getDashboardUsersQueryOptions,
} from "@/components/Dashboard/queries"
import { Button } from "@/components/ui/button"
import useAuth from "@/hooks/useAuth"
import { usePrefersReducedMotion } from "@/hooks/usePrefersReducedMotion"
import { cn } from "@/lib/utils"

interface IndexSectionProps {
  index: number
  title: string
  action?: ReactNode
  className?: string
  children: ReactNode
}

/**
 * One numbered entry on the workspace index rail. The number encodes reading
 * order; the rail is structure, not decoration.
 */
function IndexSection({
  index,
  title,
  action,
  className,
  children,
}: IndexSectionProps) {
  const headingId = `dashboard-section-${index}`

  return (
    <section
      aria-labelledby={headingId}
      className={cn(
        "grid grid-cols-[2rem_minmax(0,1fr)] gap-x-3 sm:grid-cols-[3rem_minmax(0,1fr)] sm:gap-x-5",
        className,
      )}
    >
      <div className="flex flex-col items-start gap-3 pt-0.5">
        <span
          aria-hidden="true"
          className="font-mono text-body-sm text-muted-foreground"
        >
          {String(index).padStart(2, "0")}
        </span>
        <span
          aria-hidden="true"
          className="ml-1 hidden w-px flex-1 bg-border sm:block"
        />
      </div>
      <div className="flex min-w-0 flex-col gap-4">
        <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <h2
            id={headingId}
            className="text-caption font-body font-semibold text-muted-foreground"
          >
            {title}
          </h2>
          {action}
        </div>
        {children}
      </div>
    </section>
  )
}

function LibraryStatus({ count }: { count: number }) {
  return (
    <div className="flex flex-col gap-2">
      <p className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="border-b-2 border-accent/70 font-mono text-3xl font-medium tabular-nums text-foreground md:text-4xl">
          {count}
        </span>{" "}
        <span className="text-body text-muted-foreground">
          {count === 1 ? "item" : "items"} in your library
        </span>
      </p>
      <p className="max-w-prose text-body-sm text-muted-foreground">
        This is the exact total. The preview below shows a small subset.
      </p>
    </div>
  )
}

function ActionLink({
  to,
  children,
}: {
  to: "/items" | "/settings" | "/admin"
  children: ReactNode
}) {
  return (
    <Button
      variant="outline"
      className="h-11 w-full justify-between sm:h-9 sm:w-auto sm:justify-start"
      asChild
    >
      <Link to={to}>
        {children}
        <ArrowRight aria-hidden="true" className="size-4" />
      </Link>
    </Button>
  )
}

function WorkspaceActionsSection() {
  return (
    <IndexSection
      index={3}
      title="Workspace actions"
      className="reveal-group reveal-delay-3"
    >
      <div className="flex flex-col items-stretch gap-2 sm:flex-row sm:gap-3">
        <ActionLink to="/items">Open library</ActionLink>
        <ActionLink to="/settings">Account settings</ActionLink>
      </div>
    </IndexSection>
  )
}

function AdministrationSection() {
  const { data: users } = useSuspenseQuery(getDashboardUsersQueryOptions())

  return (
    <IndexSection
      index={3}
      title="Administration"
      className="reveal-group reveal-delay-3"
    >
      <div className="flex flex-col gap-3">
        <p className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
          <span className="font-mono text-xl font-medium tabular-nums text-foreground">
            {users.count}
          </span>{" "}
          <span className="text-body text-muted-foreground">
            registered {users.count === 1 ? "account" : "accounts"}
          </span>
        </p>
        <div className="flex flex-col items-stretch gap-2 sm:flex-row sm:gap-3">
          <ActionLink to="/admin">Manage users</ActionLink>
          <ActionLink to="/settings">Account settings</ActionLink>
        </div>
      </div>
    </IndexSection>
  )
}

export function LibraryIndex() {
  const { user: currentUser } = useAuth()
  const prefersReducedMotion = usePrefersReducedMotion()
  const { data: items } = useSuspenseQuery(getDashboardItemsQueryOptions())

  if (items.count === 0) {
    return <DashboardEmpty isSuperuser={!!currentUser?.is_superuser} />
  }

  return (
    <div className="flex flex-col gap-(--space-section)">
      <IndexSection
        index={1}
        title="Library status"
        className="reveal-group reveal-delay-2"
      >
        <LibraryStatus count={items.count} />
      </IndexSection>

      <IndexSection
        index={2}
        title="Library preview"
        action={
          <Link
            to="/items"
            viewTransition={!prefersReducedMotion}
            className="inline-flex min-h-8 items-center gap-1 text-body-sm text-primary underline-offset-4 hover:underline"
          >
            Open all items
            <ArrowRight aria-hidden="true" className="size-3.5" />
          </Link>
        }
        className="reveal-group reveal-delay-3"
      >
        <div className="[view-transition-name:library-surface]">
          <LibraryPreview items={items.data} total={items.count} />
        </div>
      </IndexSection>

      {currentUser?.is_superuser ? (
        <AdministrationSection />
      ) : (
        <WorkspaceActionsSection />
      )}
    </div>
  )
}
