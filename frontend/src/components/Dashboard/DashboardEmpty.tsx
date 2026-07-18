import { Link } from "@tanstack/react-router"

import AddItem from "@/components/Items/AddItem"

interface DashboardEmptyProps {
  isSuperuser: boolean
}

export function DashboardEmpty({ isSuperuser }: DashboardEmptyProps) {
  return (
    <section
      aria-labelledby="dashboard-empty-title"
      className="reveal-group reveal-delay-2 rounded-2xl border border-border bg-surface-1 px-6 py-10 md:px-10 md:py-14"
    >
      <div className="flex max-w-md flex-col gap-3">
        <h2
          id="dashboard-empty-title"
          className="font-display text-display-md text-foreground"
        >
          Start your workspace
        </h2>
        <p className="text-body text-muted-foreground">
          Create an item to begin organizing your notes, references, or saved
          content.
        </p>
        <div className="mt-2 flex flex-col items-stretch gap-2 sm:flex-row">
          <AddItem />
        </div>
        <p className="text-body-sm text-muted-foreground">
          You can also{" "}
          <Link
            to="/settings"
            className="underline underline-offset-2 hover:text-foreground"
          >
            manage your account
          </Link>
          {isSuperuser && (
            <>
              {" "}
              or{" "}
              <Link
                to="/admin"
                className="underline underline-offset-2 hover:text-foreground"
              >
                administer users
              </Link>
            </>
          )}
          .
        </p>
      </div>
    </section>
  )
}
