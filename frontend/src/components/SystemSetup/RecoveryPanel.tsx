import { Terminal, TriangleAlert } from "lucide-react"

import type { SystemReadinessPublic } from "@/client"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { SYSTEM_SETUP_CLI_COMMAND } from "./presentation"

interface RecoveryPanelProps {
  readiness: SystemReadinessPublic
}

export function RecoveryPanel({ readiness }: RecoveryPanelProps) {
  const hasRecoveryDetail =
    readiness.warnings.length > 0 || readiness.recovery_actions.length > 0

  return (
    <Card className="h-full min-w-0">
      <CardHeader>
        <CardTitle>
          <h2>Operator recovery</h2>
        </CardTitle>
        <CardDescription>
          Follow only these browser-safe actions. Run the package command when
          browser authentication is unavailable.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <Alert variant={hasRecoveryDetail ? "warning" : "info"}>
          <TriangleAlert aria-hidden="true" />
          <AlertTitle>
            {hasRecoveryDetail ? "Action may be required" : "No active warning"}
          </AlertTitle>
          <AlertDescription>
            {hasRecoveryDetail ? (
              <div className="flex flex-col gap-3">
                {readiness.warnings.length > 0 ? (
                  <ul className="list-disc pl-4">
                    {readiness.warnings.map((warning) => (
                      <li key={warning}>{warning}</li>
                    ))}
                  </ul>
                ) : null}
                {readiness.recovery_actions.length > 0 ? (
                  <ol className="list-decimal pl-4">
                    {readiness.recovery_actions.map((action) => (
                      <li key={action}>{action}</li>
                    ))}
                  </ol>
                ) : null}
              </div>
            ) : (
              "All reported checks are clear. Keep the command below for local recovery."
            )}
          </AlertDescription>
        </Alert>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <Terminal
              aria-hidden="true"
              className="size-4 text-muted-foreground"
            />
            <h3 className="text-caption font-semibold text-muted-foreground">
              Package authentication command
            </h3>
          </div>
          <pre className="max-w-full whitespace-pre-wrap break-words rounded-xl border border-border bg-surface-2 p-4">
            <code className="font-mono text-body-sm text-foreground">
              {SYSTEM_SETUP_CLI_COMMAND}
            </code>
          </pre>
          <p className="text-body-sm text-muted-foreground">
            Run it from the engine package environment while the application
            runtime is stopped.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
