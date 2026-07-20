import { createFileRoute, Link } from "@tanstack/react-router"

import { Button } from "@/components/ui/button"
import { buildPageTitle } from "@/lib/branding"

export const Route = createFileRoute("/_layout/forbidden")({
  component: ForbiddenPage,
  head: () => ({
    meta: [
      {
        title: buildPageTitle("Not authorized"),
      },
    ],
  }),
})

function ForbiddenPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <h1 className="text-3xl font-bold tracking-tight">Not authorized</h1>
      <p className="max-w-lg text-muted-foreground">
        You do not have permission to access that page.
      </p>
      <Button asChild>
        <Link to="/create">Return to course creation</Link>
      </Button>
    </div>
  )
}
