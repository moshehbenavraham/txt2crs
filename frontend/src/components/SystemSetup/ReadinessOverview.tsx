import { Clock3, Layers3, Sparkles } from "lucide-react"

import type { SystemReadinessPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { getInputModeLabel, getReadinessDisplay } from "./presentation"

interface ReadinessOverviewProps {
  readiness: SystemReadinessPublic
}

function formatCheckedAt(checkedAt: string): string {
  const parsedTime = new Date(checkedAt)
  if (Number.isNaN(parsedTime.getTime())) {
    return "Unknown check time"
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(parsedTime)
}

export function ReadinessOverview({ readiness }: ReadinessOverviewProps) {
  const display = getReadinessDisplay(readiness)

  return (
    <Card>
      <CardHeader className="has-data-[slot=card-action]:grid-cols-1 sm:has-data-[slot=card-action]:grid-cols-[1fr_auto]">
        <div className="min-w-0">
          <p className="mb-1 text-caption font-semibold text-muted-foreground">
            Course system
          </p>
          <CardTitle className="font-display text-display-md">
            <h2>{display.title}</h2>
          </CardTitle>
        </div>
        <CardDescription>{display.description}</CardDescription>
        <CardAction className="col-start-1 row-start-3 row-span-1 justify-self-start sm:col-start-2 sm:row-start-1 sm:row-span-2 sm:justify-self-end">
          <Badge variant={display.badgeVariant}>{display.label}</Badge>
        </CardAction>
      </CardHeader>

      <CardContent className="flex flex-col gap-5">
        <Separator />
        <dl className="grid gap-4 sm:grid-cols-3">
          <div className="flex min-w-0 items-start gap-3">
            <Sparkles
              aria-hidden="true"
              className="mt-0.5 size-5 shrink-0 text-muted-foreground"
            />
            <div className="min-w-0">
              <dt className="text-caption font-semibold text-muted-foreground">
                Model
              </dt>
              <dd className="truncate font-mono text-body-sm text-foreground">
                {readiness.configured_model_id}
              </dd>
            </div>
          </div>
          <div className="flex min-w-0 items-start gap-3">
            <Layers3
              aria-hidden="true"
              className="mt-0.5 size-5 shrink-0 text-muted-foreground"
            />
            <div className="min-w-0">
              <dt className="text-caption font-semibold text-muted-foreground">
                Admission
              </dt>
              <dd className="text-body-sm text-foreground">
                {readiness.accepting_jobs
                  ? "Accepting course work"
                  : "New work paused"}
              </dd>
            </div>
          </div>
          <div className="flex min-w-0 items-start gap-3">
            <Clock3
              aria-hidden="true"
              className="mt-0.5 size-5 shrink-0 text-muted-foreground"
            />
            <div className="min-w-0">
              <dt className="text-caption font-semibold text-muted-foreground">
                Last checked
              </dt>
              <dd className="text-body-sm text-foreground">
                {formatCheckedAt(readiness.checked_at)}
              </dd>
            </div>
          </div>
        </dl>

        <div className="flex flex-col gap-2">
          <h2 className="text-caption font-semibold text-muted-foreground">
            Enabled source inputs
          </h2>
          <div className="flex flex-wrap gap-2">
            {readiness.enabled_input_modes.map((inputMode, inputModeIndex) => (
              <Badge
                // The safe API bounds this list but does not promise unique
                // values. Include position so repeated capabilities cannot
                // trigger React key warnings in development.
                key={`${inputMode}-${inputModeIndex}`}
                variant="outline"
              >
                {getInputModeLabel(inputMode)}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
