import { CalendarClock, Gauge, RefreshCw, ShieldCheck } from "lucide-react"

import type { JobAdmissionCapacityPublic } from "@/client"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import {
  formatAdmissionWindow,
  formatReservationExpiry,
  getAdmissionCapacityDisplay,
} from "./presentation"

interface CourseCapacityStripProps {
  capacity?: JobAdmissionCapacityPublic
  isError: boolean
  isPending: boolean
  onRetry: () => void
}

/**
 * Put admission truth before the workbench without making it feel punitive.
 *
 * This composition deliberately uses one continuous editorial surface rather
 * than a cluster of dashboard cards. The large availability figure answers
 * the immediate question; the progress rail and dates explain the policy.
 */
export function CourseCapacityStrip({
  capacity,
  isError,
  isPending,
  onRetry,
}: CourseCapacityStripProps) {
  if (isPending) {
    return (
      <section
        aria-label="Loading course-generation capacity"
        aria-busy="true"
        className="border-y border-border-strong bg-surface-1 px-5 py-6 sm:px-8"
      >
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_13rem_minmax(15rem,0.72fr)] lg:items-center">
          <div className="space-y-3">
            <Skeleton className="h-3 w-32" />
            <Skeleton className="h-7 w-64" />
            <Skeleton className="h-4 w-full max-w-lg" />
          </div>
          <Skeleton className="h-20 w-40" />
          <Skeleton className="h-16 w-full" />
        </div>
      </section>
    )
  }

  if (isError || !capacity) {
    return (
      <Alert variant="warning">
        <Gauge aria-hidden="true" />
        <AlertTitle>Generation capacity could not be displayed</AlertTitle>
        <AlertDescription>
          <p>
            You can keep preparing your course. The server will still verify
            capacity before accepting it.
          </p>
          <Button
            type="button"
            variant="outline"
            className="mt-3 min-h-11"
            onClick={onRetry}
          >
            <RefreshCw data-icon="inline-start" />
            Check capacity again
          </Button>
        </AlertDescription>
      </Alert>
    )
  }

  const display = getAdmissionCapacityDisplay(capacity)
  const sharedCapacityIsLimiting =
    capacity.available_jobs < capacity.owner_jobs_remaining

  return (
    <section
      aria-labelledby="course-capacity-title"
      data-testid="course-capacity"
      className="relative overflow-hidden border-y border-border-strong bg-surface-1"
    >
      <div
        aria-hidden="true"
        className={`absolute inset-y-0 left-0 w-1 ${display.isAvailable ? "bg-primary" : "bg-warning"}`}
      />
      <div className="grid gap-7 px-5 py-6 sm:px-8 sm:py-7 lg:grid-cols-[minmax(0,1fr)_13rem_minmax(15rem,0.72fr)] lg:items-center lg:gap-10">
        <div className="min-w-0">
          <div className="mb-3 flex items-center gap-3">
            <span className="grid size-10 shrink-0 place-items-center rounded-full border border-border-strong bg-background text-primary shadow-xs">
              <ShieldCheck aria-hidden="true" className="size-5" />
            </span>
            <div>
              <p className="text-caption text-primary">Generation capacity</p>
              <h2
                id="course-capacity-title"
                className="font-display text-display-sm text-foreground"
              >
                {display.title}
              </h2>
            </div>
          </div>
          <p className="max-w-xl text-body-sm leading-6 text-muted-foreground">
            Every accepted course reserves a complete research and generation
            budget. Openings return individually as this rolling window moves.
          </p>
        </div>

        <div className="min-w-0 border-l-2 border-accent pl-5">
          <Badge variant={display.isAvailable ? "success" : "warning"}>
            {display.availableLabel}
          </Badge>
          <div className="mt-2 flex items-end gap-2">
            <span className="font-display text-5xl leading-none text-foreground">
              {capacity.available_jobs}
            </span>
            <span className="pb-1 text-body-sm text-muted-foreground">
              available now
            </span>
          </div>
          <div
            role="progressbar"
            aria-label={display.usageLabel}
            aria-valuemin={0}
            aria-valuemax={capacity.owner_job_limit}
            aria-valuenow={Math.min(
              capacity.owner_jobs_used,
              capacity.owner_job_limit,
            )}
            className="mt-4 h-1.5 overflow-hidden rounded-full bg-stage-track"
          >
            <div
              className="h-full rounded-full bg-stage-complete transition-[width] duration-(--motion-duration-state)"
              style={{ width: `${display.usagePercentage}%` }}
            />
          </div>
          <p className="mt-2 text-caption text-muted-foreground">
            {display.usageLabel}
          </p>
        </div>

        <dl className="grid gap-4 border-t border-border pt-5 sm:grid-cols-2 lg:grid-cols-1 lg:border-t-0 lg:border-l lg:pt-0 lg:pl-7">
          <div className="flex items-start gap-3">
            <Gauge
              aria-hidden="true"
              className="mt-0.5 size-4 shrink-0 text-primary"
            />
            <div>
              <dt className="text-caption text-muted-foreground">Policy</dt>
              <dd className="text-body-sm text-foreground">
                {formatAdmissionWindow(capacity.window_seconds)}
              </dd>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CalendarClock
              aria-hidden="true"
              className="mt-0.5 size-4 shrink-0 text-primary"
            />
            <div>
              <dt className="text-caption text-muted-foreground">
                Next reservation expiry
              </dt>
              <dd className="text-body-sm text-foreground">
                {capacity.next_reservation_expires_at ? (
                  <time dateTime={capacity.next_reservation_expires_at}>
                    {formatReservationExpiry(
                      capacity.next_reservation_expires_at,
                    )}
                  </time>
                ) : (
                  "All of your reservations are open"
                )}
              </dd>
            </div>
          </div>
          {sharedCapacityIsLimiting ? (
            <div className="sm:col-span-2 lg:col-span-1">
              <dt className="sr-only">Shared capacity</dt>
              <dd className="text-caption leading-5 text-warning">
                Shared course capacity currently has {capacity.available_jobs}{" "}
                {capacity.available_jobs === 1 ? "opening" : "openings"}.
              </dd>
            </div>
          ) : null}
        </dl>
      </div>
    </section>
  )
}
