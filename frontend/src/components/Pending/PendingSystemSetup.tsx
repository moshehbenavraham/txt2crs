import { Skeleton } from "@/components/ui/skeleton"

/**
 * The skeleton mirrors the final verdict, action/recovery columns, and check
 * index so the page does not jump when both cache requests settle.
 */
const PendingSystemSetup = () => (
  <div className="flex flex-col gap-6">
    <p className="sr-only" role="status">
      Loading system setup
    </p>
    <div
      aria-hidden="true"
      className="flex flex-col gap-5 rounded-2xl border border-border bg-surface-1 p-6"
    >
      <Skeleton className="h-3 w-28" />
      <Skeleton className="h-7 w-64 max-w-full" />
      <Skeleton className="h-4 w-full max-w-2xl" />
      <div className="grid gap-4 sm:grid-cols-3">
        <Skeleton className="h-12" />
        <Skeleton className="h-12" />
        <Skeleton className="h-12" />
      </div>
    </div>
    <div className="grid gap-6 lg:grid-cols-2">
      <Skeleton className="h-80 rounded-2xl" />
      <Skeleton className="h-80 rounded-2xl" />
    </div>
    <Skeleton className="h-96 rounded-2xl" />
  </div>
)

export default PendingSystemSetup
