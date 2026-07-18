import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { UserTableData } from "./columns"
import { UserActionsMenu } from "./UserActionsMenu"

/**
 * Mobile record representation of a user. Identity, role, status, and actions
 * are all visible without horizontal scrolling; color never carries status
 * alone.
 */
export function UserRecordCard({ user }: { user: UserTableData }) {
  return (
    <article className="flex flex-col gap-2 rounded-xl border border-border bg-surface-1 p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="flex min-w-0 flex-col gap-0.5">
          <div className="flex flex-wrap items-center gap-2">
            <h3
              className={cn(
                "truncate font-medium text-foreground",
                !user.full_name && "text-muted-foreground",
              )}
            >
              {user.full_name || "N/A"}
            </h3>
            {user.isCurrentUser && (
              <Badge variant="outline" className="text-xs">
                You
              </Badge>
            )}
          </div>
          <p className="truncate text-body-sm text-muted-foreground">
            {user.email}
          </p>
        </div>
        <div className="-mr-2 -mt-2 shrink-0">
          <UserActionsMenu user={user} />
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-body-sm">
        <Badge variant={user.is_superuser ? "default" : "secondary"}>
          {user.is_superuser ? "Superuser" : "User"}
        </Badge>
        <span className="flex items-center gap-2">
          <span
            aria-hidden="true"
            className={cn(
              "size-2 rounded-full",
              user.is_active ? "bg-success" : "bg-muted-foreground",
            )}
          />
          <span className={user.is_active ? "" : "text-muted-foreground"}>
            {user.is_active ? "Active" : "Inactive"}
          </span>
        </span>
      </div>
    </article>
  )
}
