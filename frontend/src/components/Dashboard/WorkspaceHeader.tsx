import { Link } from "@tanstack/react-router"

import type { UserPublic } from "@/client"
import { PageHeader } from "@/components/Common/PageHeader"
import AddItem from "@/components/Items/AddItem"
import { Button } from "@/components/ui/button"
import { usePrefersReducedMotion } from "@/hooks/usePrefersReducedMotion"

interface WorkspaceHeaderProps {
  user: UserPublic | null | undefined
}

export function WorkspaceHeader({ user }: WorkspaceHeaderProps) {
  const prefersReducedMotion = usePrefersReducedMotion()
  const firstName = user?.full_name?.trim().split(/\s+/)[0] || user?.email

  return (
    <div className="reveal-group reveal-delay-1">
      <PageHeader
        eyebrow="Workspace"
        title="Workspace overview"
        description={
          firstName
            ? `Good to see you, ${firstName}. Here is the current state of your library.`
            : "Here is the current state of your library."
        }
        actions={
          <>
            <Button variant="outline" className="h-11 sm:h-9" asChild>
              <Link to="/items" viewTransition={!prefersReducedMotion}>
                Open library
              </Link>
            </Button>
            <AddItem />
          </>
        }
      />
    </div>
  )
}
