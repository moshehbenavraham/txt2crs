import {
  Check,
  Clipboard,
  ExternalLink,
  KeyRound,
  ShieldCheck,
} from "lucide-react"

import type { SystemAuthenticationPublic } from "@/client"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useCopyToClipboard } from "@/hooks/useCopyToClipboard"
import {
  getAuthenticationDisplay,
  type SetupAlertVariant,
} from "./presentation"

interface AuthenticationPanelProps {
  authentication: SystemAuthenticationPublic
  isStarting: boolean
  startErrorMessage?: string
  onStart: () => void
  onCopyAnnouncement: (message: string) => void
}

export function AuthenticationPanel({
  authentication,
  isStarting,
  startErrorMessage,
  onStart,
  onCopyAnnouncement,
}: AuthenticationPanelProps) {
  const display = getAuthenticationDisplay(authentication.state)
  const [copiedText, copyToClipboard] = useCopyToClipboard()
  const hasChallenge =
    authentication.state === "waiting_for_user" &&
    authentication.verification_url !== null &&
    authentication.user_code !== null

  const handleCopyCode = async () => {
    if (!authentication.user_code) {
      return
    }

    const copySucceeded = await copyToClipboard(authentication.user_code)
    onCopyAnnouncement(
      copySucceeded
        ? "Code copied"
        : "Copy unavailable. Select the code manually.",
    )
  }

  return (
    <Card className="h-full min-w-0">
      <CardHeader className="has-data-[slot=card-action]:grid-cols-1 sm:has-data-[slot=card-action]:grid-cols-[1fr_auto]">
        <div>
          <p className="mb-1 text-caption font-semibold text-muted-foreground">
            Dedicated identity
          </p>
          <CardTitle>
            <h2>{display.title}</h2>
          </CardTitle>
        </div>
        <CardDescription>{display.description}</CardDescription>
        <CardAction className="col-start-1 row-start-3 row-span-1 justify-self-start sm:col-start-2 sm:row-start-1 sm:row-span-2 sm:justify-self-end">
          <Badge variant={display.badgeVariant}>{display.label}</Badge>
        </CardAction>
      </CardHeader>

      <CardContent className="flex flex-1 flex-col gap-4">
        <Alert variant={display.alertVariant as SetupAlertVariant}>
          {authentication.state === "authenticated" ? (
            <ShieldCheck aria-hidden="true" />
          ) : (
            <KeyRound aria-hidden="true" />
          )}
          <AlertTitle>{authentication.message}</AlertTitle>
          <AlertDescription>
            {authentication.state === "waiting_for_user"
              ? "The page updates automatically when approval finishes."
              : "No account identity or credential is shown in this workspace."}
          </AlertDescription>
        </Alert>

        {hasChallenge ? (
          <div className="flex flex-col gap-4 rounded-xl border border-border bg-surface-2 p-4 sm:p-5">
            <div className="flex flex-col gap-1">
              <p className="text-caption font-semibold text-muted-foreground">
                Authentication code
              </p>
              <p className="font-mono text-2xl font-medium tracking-wider text-foreground sm:text-3xl">
                {authentication.user_code}
              </p>
            </div>
            <div className="flex flex-col gap-2 sm:flex-row">
              <Button className="h-11 sm:h-10" asChild>
                <a
                  href={authentication.verification_url ?? undefined}
                  target="_blank"
                  rel="noreferrer"
                  aria-label="Open OpenAI verification page"
                >
                  <ExternalLink data-icon="inline-start" />
                  Open verification page
                </a>
              </Button>
              <Button
                type="button"
                variant="outline"
                className="h-11 sm:h-10"
                onClick={handleCopyCode}
                aria-label="Copy authentication code"
              >
                {copiedText === authentication.user_code ? (
                  <Check data-icon="inline-start" />
                ) : (
                  <Clipboard data-icon="inline-start" />
                )}
                {copiedText === authentication.user_code
                  ? "Copied"
                  : "Copy code"}
              </Button>
            </div>
          </div>
        ) : null}

        {startErrorMessage ? (
          <Alert variant="destructive">
            <KeyRound aria-hidden="true" />
            <AlertTitle>Connection could not start</AlertTitle>
            <AlertDescription>{startErrorMessage}</AlertDescription>
          </Alert>
        ) : null}
      </CardContent>

      {display.actionLabel ? (
        <CardFooter>
          <Button
            type="button"
            className="h-11 w-full sm:w-auto"
            disabled={isStarting}
            onClick={onStart}
          >
            <KeyRound data-icon="inline-start" />
            {isStarting ? "Starting connection..." : display.actionLabel}
          </Button>
        </CardFooter>
      ) : null}
    </Card>
  )
}
