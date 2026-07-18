import { createFileRoute, Link } from "@tanstack/react-router"

import { Button } from "@/components/ui/button"

export const Route = createFileRoute("/_layout/forbidden")({
  component: ForbiddenPage,
  head: () => ({
    meta: [
      {
        title: "Not Authorized - AIwithApex.com",
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
      <Link to="/">
        <Button>Go to dashboard</Button>
      </Link>
    </div>
  )
}
