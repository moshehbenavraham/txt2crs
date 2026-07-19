import { CheckCircle2, CircleX } from "lucide-react"

import type { SystemReadinessChecksPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { SYSTEM_CHECK_DEFINITIONS } from "./presentation"

interface SystemChecklistProps {
  checks: SystemReadinessChecksPublic
}

export function SystemChecklist({ checks }: SystemChecklistProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <h2 id="system-checks-title">System checks</h2>
        </CardTitle>
        <CardDescription>
          Eight coarse signals determine whether the course system can accept
          new work.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <section
          aria-labelledby="system-checks-title"
          className="grid overflow-hidden rounded-xl border border-border md:grid-cols-2"
        >
          {SYSTEM_CHECK_DEFINITIONS.map((definition) => {
            const isReady = checks[definition.key] === "ready"

            return (
              <div
                key={definition.key}
                className="grid grid-cols-[2rem_minmax(0,1fr)] items-start gap-3 border-b border-border p-4 last:border-b-0 sm:grid-cols-[2rem_minmax(0,1fr)_auto] md:[&:nth-last-child(-n+2)]:border-b-0 md:[&:nth-child(odd)]:border-r"
              >
                <span
                  aria-hidden="true"
                  className="pt-0.5 font-mono text-body-sm text-muted-foreground"
                >
                  {definition.index}
                </span>
                <div className="min-w-0">
                  <h3 className="text-body font-medium text-foreground">
                    {definition.label}
                  </h3>
                  <p className="mt-1 text-body-sm text-muted-foreground">
                    {definition.description}
                  </p>
                </div>
                <Badge
                  className="col-start-2 sm:col-start-3 sm:row-start-1"
                  variant={isReady ? "success" : "destructive"}
                >
                  {isReady ? (
                    <CheckCircle2 aria-hidden="true" />
                  ) : (
                    <CircleX aria-hidden="true" />
                  )}
                  {isReady ? "Ready" : "Unavailable"}
                </Badge>
              </div>
            )
          })}
        </section>
      </CardContent>
    </Card>
  )
}
