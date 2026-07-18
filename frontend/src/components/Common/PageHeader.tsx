import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

interface PageHeaderProps {
  eyebrow?: string
  title: string
  description?: string
  actions?: ReactNode
  className?: string
}

/**
 * Shared page identity composition: optional eyebrow, one h1, a concise
 * description, and a wrapping action group. Below `sm` the identity and
 * actions stack full-width; above `sm` they align at the bottom edge.
 */
export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
  className,
}: PageHeaderProps) {
  return (
    <header
      className={cn(
        "flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between",
        className,
      )}
    >
      <div className="flex min-w-0 flex-col gap-1.5">
        {eyebrow && (
          <p className="text-caption font-body text-muted-foreground">
            {eyebrow}
          </p>
        )}
        <h1 className="font-display text-display-lg text-foreground">
          {title}
        </h1>
        {description && (
          <p className="max-w-prose text-body text-muted-foreground">
            {description}
          </p>
        )}
      </div>
      {actions && (
        <div className="flex shrink-0 flex-col items-stretch gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:gap-3">
          {actions}
        </div>
      )}
    </header>
  )
}
