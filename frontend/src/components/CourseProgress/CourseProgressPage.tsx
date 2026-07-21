import { onlineManager } from "@tanstack/react-query"
import { Link } from "@tanstack/react-router"
import {
  Activity,
  Check,
  Circle,
  CircleDot,
  Clipboard,
  Clock3,
  FileCheck2,
  RefreshCw,
  Timer,
  TriangleAlert,
  WifiOff,
} from "lucide-react"
import { useEffect, useRef, useState, useSyncExternalStore } from "react"

import { PageHeader } from "@/components/Common/PageHeader"
import {
  buildJobProgressPresentation,
  getActiveJobTimingPresentation,
  getInputWarningsPresentation,
  getProgressUnitsLabel,
  getTimeSinceLabel,
  type ProductStagePresentation,
} from "@/components/CourseProgress/presentation"
import { useJobProgressQuery } from "@/components/CourseProgress/queries"
import { CourseResultsWorkspace } from "@/components/CourseResults/CourseResultsWorkspace"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { ApiError } from "@/lib/api-error"
import type { JobId } from "@/lib/types"

interface CourseProgressPageProps {
  jobId: JobId
}

function useBrowserOnlineState(): boolean {
  return useSyncExternalStore(
    (onStoreChange) => onlineManager.subscribe(onStoreChange),
    () => onlineManager.isOnline(),
    () => true,
  )
}

function useLiveCurrentTime(): number {
  const [currentTime, setCurrentTime] = useState(() => Date.now())

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setCurrentTime(Date.now())
    }, 1_000)
    return () => {
      window.clearInterval(intervalId)
    }
  }, [])

  return currentTime
}

function isUniformUnavailableError(error: unknown): boolean {
  return (
    error instanceof ApiError && (error.status === 404 || error.status === 422)
  )
}

function getProgressHeaderDescription(
  kind: ReturnType<typeof buildJobProgressPresentation>["kind"],
): string {
  switch (kind) {
    case "active":
      return "Follow each confirmed course-building stage. This private page is safe to revisit."
    case "completed":
      return "Generation is complete, and the private results summary is ready."
    case "failed":
    case "cancelled":
      return "This private course job has reached a safe terminal state."
    default: {
      const exhaustiveKind: never = kind
      return exhaustiveKind
    }
  }
}

/** Owner-scoped course progress with no source-content or infrastructure data. */
export function CourseProgressPage({ jobId }: CourseProgressPageProps) {
  const jobQuery = useJobProgressQuery(jobId)
  const isOnline = useBrowserOnlineState()

  if (!jobQuery.data && (!isOnline || jobQuery.fetchStatus === "paused")) {
    return (
      <ProgressConnectionState
        kind="offline"
        isRetrying={jobQuery.isFetching}
        onRetry={() => {
          void jobQuery.refetch()
        }}
      />
    )
  }
  if (jobQuery.isPending) {
    return <CourseProgressLoading />
  }
  if (!jobQuery.data && isUniformUnavailableError(jobQuery.error)) {
    return <CourseJobUnavailable />
  }
  if (!jobQuery.data) {
    return (
      <ProgressConnectionState
        kind="reconnecting"
        isRetrying={jobQuery.isFetching}
        onRetry={() => {
          void jobQuery.refetch()
        }}
      />
    )
  }

  return (
    <CourseProgressWorkspace
      jobId={jobId}
      snapshot={jobQuery.data}
      isCheckingForUpdates={jobQuery.isFetching}
      isReconnecting={
        !isOnline || jobQuery.isError || jobQuery.fetchStatus === "paused"
      }
      lastCheckedAt={jobQuery.dataUpdatedAt}
    />
  )
}

interface CourseProgressWorkspaceProps {
  jobId: JobId
  snapshot: NonNullable<ReturnType<typeof useJobProgressQuery>["data"]>
  isCheckingForUpdates: boolean
  isReconnecting: boolean
  lastCheckedAt: number
}

function CourseProgressWorkspace({
  jobId,
  snapshot,
  isCheckingForUpdates,
  isReconnecting,
  lastCheckedAt,
}: CourseProgressWorkspaceProps) {
  const presentation = buildJobProgressPresentation(snapshot)
  const inputWarnings = getInputWarningsPresentation(snapshot.input)
  const isActive = presentation.kind === "active"
  const safeStatusMessage =
    presentation.kind === "failed"
      ? (snapshot.failure?.message ?? snapshot.progress.message)
      : snapshot.progress.message

  return (
    <div className="grid gap-(--space-section)">
      <PageHeader
        eyebrow="Course progress"
        title={presentation.heading}
        description={getProgressHeaderDescription(presentation.kind)}
        actions={<JobReference jobId={jobId} />}
      />

      {isReconnecting ? (
        <Alert variant="warning">
          <WifiOff aria-hidden="true" />
          <AlertTitle>Reconnecting</AlertTitle>
          <AlertDescription>
            Showing the last confirmed course update while the connection
            returns.
          </AlertDescription>
        </Alert>
      ) : null}

      {inputWarnings ? (
        <Alert variant="warning">
          <TriangleAlert aria-hidden="true" />
          <AlertTitle>Source extraction notes</AlertTitle>
          <AlertDescription>
            {inputWarnings.warnings.length > 0 ? (
              <ul className="grid list-disc gap-1 pl-5">
                {inputWarnings.warnings.map((warning, warningIndex) => (
                  // Extraction adapters may legitimately report the same
                  // bounded note more than once for different source parts.
                  // Include the stable response order so React never receives
                  // duplicate sibling keys.
                  <li
                    key={`${warningIndex}-${warning}`}
                    className="break-words"
                  >
                    {warning}
                  </li>
                ))}
              </ul>
            ) : null}
            {inputWarnings.hasAdditionalWarnings ? (
              <p className={inputWarnings.warnings.length > 0 ? "mt-2" : ""}>
                Additional source notes were omitted from this bounded summary.
              </p>
            ) : null}
          </AlertDescription>
        </Alert>
      ) : null}

      <div className="grid gap-10 lg:grid-cols-[minmax(17rem,0.72fr)_minmax(0,1.28fr)] lg:items-start">
        <CourseStageRail stages={presentation.stages} />

        <section
          aria-labelledby="current-course-status"
          className="border-y border-border-strong bg-workbench px-5 py-8 sm:px-8"
        >
          <p className="text-caption text-primary">
            {presentation.kind === "active"
              ? "Current update"
              : "Terminal update"}
          </p>
          <h2 id="current-course-status" className="mt-3 text-display-md">
            {safeStatusMessage}
          </h2>
          <p className="mt-5 text-body-sm text-muted-foreground">
            {getProgressUnitsLabel(snapshot.progress)}
          </p>

          {isActive ? (
            <LiveProgressTelemetry
              snapshot={snapshot}
              isCheckingForUpdates={isCheckingForUpdates}
              isReconnecting={isReconnecting}
              lastCheckedAt={lastCheckedAt}
            />
          ) : null}

          <span className="sr-only" role="status" aria-live="polite">
            Confirmed update {snapshot.revision}: {safeStatusMessage}{" "}
            {getProgressUnitsLabel(snapshot.progress)}
          </span>

          {presentation.kind === "completed" ? (
            <CompletionHandoff snapshot={snapshot} />
          ) : null}

          {presentation.kind === "failed" ||
          presentation.kind === "cancelled" ? (
            <TerminalRecovery />
          ) : null}
        </section>
      </div>

      {presentation.kind === "completed" ? (
        <CourseResultsWorkspace jobId={jobId} snapshot={snapshot} />
      ) : null}
    </div>
  )
}

interface LiveProgressTelemetryProps {
  snapshot: CourseProgressWorkspaceProps["snapshot"]
  isCheckingForUpdates: boolean
  isReconnecting: boolean
  lastCheckedAt: number
}

/**
 * Isolate the one-second clock so the large stage rail and results workspace
 * do not rerender merely to keep elapsed and estimated time current.
 */
function LiveProgressTelemetry({
  snapshot,
  isCheckingForUpdates,
  isReconnecting,
  lastCheckedAt,
}: LiveProgressTelemetryProps) {
  const currentTimeMilliseconds = useLiveCurrentTime()
  const timing = getActiveJobTimingPresentation(
    snapshot,
    currentTimeMilliseconds,
  )
  const progressUnitsLabel = getProgressUnitsLabel(snapshot.progress)
  const totalUnits = snapshot.progress.total_units
  const hasKnownTotal = totalUnits !== null && totalUnits !== undefined
  const statusCheckLabel =
    lastCheckedAt > 0
      ? getTimeSinceLabel(lastCheckedAt, currentTimeMilliseconds)
      : "pending"

  return (
    <section
      aria-label="Live course progress"
      className="mt-8 border-t border-border pt-6"
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex min-w-0 items-start gap-3">
          <span
            className={`mt-1.5 size-2.5 shrink-0 rounded-full ring-4 ${
              isReconnecting
                ? "bg-warning ring-warning/15"
                : "bg-primary ring-primary/15"
            }`}
          />
          <div className="min-w-0">
            <p className="font-medium text-foreground">
              {isReconnecting
                ? "Backend updates paused"
                : "Live backend updates"}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              {isCheckingForUpdates && !isReconnecting
                ? "Checking for the next confirmed update now"
                : `Status checked ${statusCheckLabel}`}
            </p>
          </div>
        </div>
        <p className="shrink-0 text-caption text-primary">
          Confirmed update {snapshot.revision.toLocaleString()}
        </p>
      </div>

      <div className="mt-6">
        <div className="flex items-end justify-between gap-4">
          <p className="text-xs text-muted-foreground">Confirmed progress</p>
          <p className="text-xs font-medium text-foreground">
            {progressUnitsLabel}
          </p>
        </div>
        <div
          role="progressbar"
          aria-label="Confirmed course-building progress"
          aria-valuemin={hasKnownTotal ? 0 : undefined}
          aria-valuemax={hasKnownTotal ? totalUnits : undefined}
          aria-valuenow={
            hasKnownTotal ? snapshot.progress.completed_units : undefined
          }
          aria-valuetext={progressUnitsLabel}
          className="mt-3 h-2 overflow-hidden bg-muted"
        >
          <div
            className={
              timing.progressPercentage === null
                ? "h-full w-1/3 bg-primary/60"
                : "h-full bg-primary transition-[width] duration-(--motion-duration-state) ease-(--ease-out-quart) motion-reduce:transition-none"
            }
            style={
              timing.progressPercentage === null
                ? undefined
                : { width: `${timing.progressPercentage}%` }
            }
          />
        </div>
      </div>

      <dl className="mt-6 grid gap-px border border-border bg-border sm:grid-cols-3">
        <div className="bg-background p-4">
          <dt className="flex items-center gap-2 text-xs text-muted-foreground">
            <Clock3 aria-hidden="true" className="size-4" />
            Elapsed
          </dt>
          <dd
            data-testid="elapsed-time"
            className="mt-2 font-mono text-lg font-medium text-foreground"
          >
            {timing.elapsedTimeLabel}
          </dd>
        </div>
        <div className="bg-background p-4">
          <dt className="flex items-center gap-2 text-xs text-muted-foreground">
            <Timer aria-hidden="true" className="size-4" />
            Estimated time left
          </dt>
          <dd
            data-testid="estimated-time-left"
            className="mt-2 font-mono text-lg font-medium text-foreground"
          >
            {timing.estimatedTimeLeftLabel}
          </dd>
        </div>
        <div className="bg-background p-4">
          <dt className="flex items-center gap-2 text-xs text-muted-foreground">
            <Activity aria-hidden="true" className="size-4" />
            Latest checkpoint
          </dt>
          <dd className="mt-2 font-mono text-lg font-medium text-foreground">
            {timing.latestActivityLabel}
          </dd>
        </div>
      </dl>

      <p className="mt-4 text-xs leading-5 text-muted-foreground">
        Only durable backend checkpoints move the meter; an active stage may
        work for several minutes between confirmed updates. The estimate
        recalculates as those checkpoints arrive and may change because
        research, drafting, and rendering take different amounts of time.
      </p>
      <p className="mt-2 text-body-sm text-muted-foreground">
        You can close this page and return to the same private job.
      </p>
    </section>
  )
}

function CourseStageRail({ stages }: { stages: ProductStagePresentation[] }) {
  return (
    <section aria-labelledby="course-building-stages">
      <p
        id="course-building-stages"
        className="text-caption text-muted-foreground"
      >
        Build stages
      </p>
      <ol className="mt-5 border-y border-border-strong">
        {stages.map((stage) => (
          <li
            key={stage.id}
            aria-current={stage.state === "active" ? "step" : undefined}
            className="grid grid-cols-[2rem_minmax(0,1fr)] gap-3 border-b border-border py-4 last:border-b-0"
          >
            <StageIcon stage={stage} />
            <div className={stage.state === "inactive" ? "opacity-55" : ""}>
              <p
                className={
                  stage.state === "active"
                    ? "font-medium text-stage-active"
                    : stage.state === "complete"
                      ? "font-medium text-stage-complete"
                      : "font-medium text-foreground"
                }
              >
                {stage.label}
              </p>
              <p className="mt-1 text-xs leading-5 text-muted-foreground">
                {stage.description}
              </p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}

function StageIcon({ stage }: { stage: ProductStagePresentation }) {
  if (stage.state === "complete") {
    return (
      <span className="flex size-7 items-center justify-center border border-stage-complete/40 bg-stage-complete/10 text-stage-complete">
        <Check aria-hidden="true" className="size-4" />
        <span className="sr-only">Completed</span>
      </span>
    )
  }
  if (stage.state === "active") {
    return (
      <span className="flex size-7 items-center justify-center border border-stage-active bg-stage-active/10 text-stage-active">
        <CircleDot aria-hidden="true" className="size-4" />
        <span className="sr-only">Current stage</span>
      </span>
    )
  }
  return (
    <span className="flex size-7 items-center justify-center text-stage-inactive">
      <Circle aria-hidden="true" className="size-4" />
      <span className="sr-only">
        {stage.state === "inactive" ? "Not disclosed" : "Upcoming"}
      </span>
    </span>
  )
}

function CompletionHandoff({
  snapshot,
}: {
  snapshot: CourseProgressWorkspaceProps["snapshot"]
}) {
  return (
    <div
      id="course-results"
      className="mt-8 border-t border-border-strong pt-7"
    >
      <FileCheck2 aria-hidden="true" className="size-6 text-stage-complete" />
      <h3 className="mt-4 break-all text-xl">
        {snapshot.result?.title ?? "Complete learning package"}
      </h3>
      <p className="mt-3 text-body-sm leading-6 text-muted-foreground">
        The private course, review materials, student assessment, and instructor
        answer key are ready in this results workspace.
      </p>
      {snapshot.result ? (
        <p className="mt-3 text-body-sm text-muted-foreground">
          {snapshot.result.module_count.toLocaleString()}{" "}
          {snapshot.result.module_count === 1 ? "module" : "modules"} {"\u00b7"}{" "}
          {snapshot.result.objective_count.toLocaleString()}{" "}
          {snapshot.result.objective_count === 1
            ? "learning objective"
            : "learning objectives"}
        </p>
      ) : null}
    </div>
  )
}

function TerminalRecovery() {
  return (
    <div className="mt-8 border-t border-border-strong pt-7">
      <p className="max-w-xl text-body-sm leading-6 text-muted-foreground">
        This job will not restart automatically. Adjust the source or learning
        intent before trying again.
      </p>
      <Button asChild className="mt-5 min-h-11">
        <Link to="/create">Create another course</Link>
      </Button>
    </div>
  )
}

function JobReference({ jobId }: { jobId: JobId }) {
  const [copyState, setCopyState] = useState<"idle" | "copied" | "unavailable">(
    "idle",
  )
  const resetTimerRef = useRef<number | null>(null)

  useEffect(
    () => () => {
      if (resetTimerRef.current !== null) {
        window.clearTimeout(resetTimerRef.current)
      }
    },
    [],
  )

  const copyJobReference = async () => {
    try {
      await navigator.clipboard.writeText(jobId)
      setCopyState("copied")
    } catch {
      setCopyState("unavailable")
    }
    if (resetTimerRef.current !== null) {
      window.clearTimeout(resetTimerRef.current)
    }
    resetTimerRef.current = window.setTimeout(() => {
      setCopyState("idle")
    }, 2_000)
  }

  return (
    <div className="min-w-0">
      <p className="text-xs text-muted-foreground">Private job reference</p>
      <div className="mt-1 flex min-w-0 items-center gap-2">
        <code className="max-w-52 truncate text-xs">{jobId}</code>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="min-h-11"
          onClick={copyJobReference}
          aria-label="Copy job reference"
        >
          <Clipboard aria-hidden="true" />
          Copy
        </Button>
      </div>
      <span className="sr-only" role="status" aria-live="polite">
        {copyState === "copied"
          ? "Job reference copied"
          : copyState === "unavailable"
            ? "Job reference could not be copied"
            : ""}
      </span>
    </div>
  )
}

function CourseProgressLoading() {
  return (
    <div className="grid gap-(--space-section)" aria-busy="true">
      <PageHeader
        eyebrow="Course progress"
        title="Opening your course job"
        description="Checking the latest private update."
      />
      <div className="grid gap-10 lg:grid-cols-[minmax(17rem,0.72fr)_minmax(0,1.28fr)]">
        <div className="grid gap-3 border-y border-border-strong py-5">
          {Array.from({ length: 7 }, (_, index) => (
            <div
              // The fixed count mirrors the seven public stage definitions.
              key={index}
              className="h-12 animate-pulse bg-muted motion-reduce:animate-none"
            />
          ))}
        </div>
        <div className="min-h-64 animate-pulse border-y border-border-strong bg-workbench motion-reduce:animate-none" />
      </div>
    </div>
  )
}

interface ProgressConnectionStateProps {
  isRetrying: boolean
  kind: "offline" | "reconnecting"
  onRetry: () => void
}

function ProgressConnectionState({
  isRetrying,
  kind,
  onRetry,
}: ProgressConnectionStateProps) {
  const isOffline = kind === "offline"
  return (
    <div className="flex min-h-[55vh] items-center justify-center">
      <section className="w-full max-w-2xl border-y border-border-strong bg-workbench px-5 py-10 text-center sm:px-8">
        {isOffline ? (
          <WifiOff aria-hidden="true" className="mx-auto size-7 text-warning" />
        ) : (
          <RefreshCw
            aria-hidden="true"
            className="mx-auto size-7 text-primary"
          />
        )}
        <h1 className="mt-5 text-display-md">
          {isOffline ? "You are offline" : "Reconnecting to course progress"}
        </h1>
        <p className="mx-auto mt-4 max-w-lg text-muted-foreground">
          {isOffline
            ? "Reconnect to the internet, then retry this private course job."
            : "The last course update could not be loaded safely. Retry without creating a new job."}
        </p>
        <Button
          type="button"
          onClick={onRetry}
          disabled={isRetrying}
          className="mt-7 min-h-11"
        >
          <RefreshCw aria-hidden="true" />
          {isRetrying ? "Checking again" : "Retry progress"}
        </Button>
      </section>
    </div>
  )
}

export function CourseJobUnavailable() {
  return (
    <div className="flex min-h-[55vh] items-center justify-center">
      <section className="w-full max-w-2xl border-y border-border-strong bg-workbench px-5 py-10 text-center sm:px-8">
        <TriangleAlert
          aria-hidden="true"
          className="mx-auto size-7 text-warning"
        />
        <h1 className="mt-5 text-display-md">Course job not available</h1>
        <p className="mx-auto mt-4 max-w-lg text-muted-foreground">
          This course job could not be opened. It may not exist or may not
          belong to this account.
        </p>
        <Button asChild className="mt-7 min-h-11">
          <Link to="/create">Create a new course</Link>
        </Button>
      </section>
    </div>
  )
}

export function CourseProgressUnexpectedError() {
  return (
    <div className="flex min-h-[55vh] items-center justify-center">
      <section className="w-full max-w-2xl border-y border-border-strong bg-workbench px-5 py-10 text-center sm:px-8">
        <TriangleAlert
          aria-hidden="true"
          className="mx-auto size-7 text-warning"
        />
        <h1 className="mt-5 text-display-md">
          Course progress could not be displayed
        </h1>
        <p className="mx-auto mt-4 max-w-lg text-muted-foreground">
          Reload this private page. If the problem continues, create a new
          course request.
        </p>
        <div className="mt-7 flex flex-col justify-center gap-3 sm:flex-row">
          <Button
            type="button"
            variant="outline"
            className="min-h-11"
            onClick={() => window.location.reload()}
          >
            Reload page
          </Button>
          <Button asChild className="min-h-11">
            <Link to="/create">Create a new course</Link>
          </Button>
        </div>
      </section>
    </div>
  )
}
