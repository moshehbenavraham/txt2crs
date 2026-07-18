/**
 * Static surface placeholders matched to the index-rail geometry.
 * No shimmer: the dashboard settles once, it does not glimmer while waiting.
 */
const PendingDashboard = () => (
  <div className="flex flex-col gap-(--space-section)">
    <p className="sr-only" role="status">
      Loading your library
    </p>
    <div
      aria-hidden="true"
      className="grid grid-cols-[2rem_minmax(0,1fr)] gap-x-3 sm:grid-cols-[3rem_minmax(0,1fr)] sm:gap-x-5"
    >
      <div className="pt-0.5">
        <div className="h-4 w-6 rounded bg-muted" />
      </div>
      <div className="flex flex-col gap-4">
        <div className="h-3 w-28 rounded bg-muted" />
        <div className="flex items-baseline gap-3">
          <div className="h-9 w-16 rounded bg-muted md:h-10" />
          <div className="h-4 w-40 rounded bg-muted/70" />
        </div>
      </div>
    </div>
    <div
      aria-hidden="true"
      className="grid grid-cols-[2rem_minmax(0,1fr)] gap-x-3 sm:grid-cols-[3rem_minmax(0,1fr)] sm:gap-x-5"
    >
      <div className="pt-0.5">
        <div className="h-4 w-6 rounded bg-muted" />
      </div>
      <div className="flex flex-col gap-4">
        <div className="h-3 w-32 rounded bg-muted" />
        <div className="flex flex-col divide-y divide-border overflow-hidden rounded-xl border border-border bg-surface-1">
          {[0, 1, 2].map((row) => (
            <div key={row} className="flex items-center justify-between p-4">
              <div className="h-4 w-1/2 max-w-56 rounded bg-muted" />
              <div className="h-4 w-16 rounded bg-muted/70" />
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
)

export default PendingDashboard
