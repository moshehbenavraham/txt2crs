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

const CODEX_DEVICE_AUTH_URL = "https://auth.openai.com/codex/device"

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
          <AlertTitle className="line-clamp-none break-words">
            {authentication.message}
          </AlertTitle>
          <AlertDescription>
            {authentication.state === "waiting_for_user"
              ? "The page updates automatically when approval finishes."
              : "No account identity or credential is shown in this workspace."}
          </AlertDescription>
        </Alert>

        {/*
          Keep the reviewed OpenAI destination independent from the short-lived
          device challenge. This gives operators a safe, predictable link in
          every authentication state, including before a code has been issued.
        */}
        <Button
          variant="outline"
          className="h-auto min-h-11 w-full justify-start whitespace-normal py-3 text-left"
          asChild
        >
          <a
            href={CODEX_DEVICE_AUTH_URL}
            target="_blank"
            rel="noreferrer"
            aria-label="Open Codex device authentication"
          >
            <ExternalLink data-icon="inline-start" className="shrink-0" />
            <span className="break-all">{CODEX_DEVICE_AUTH_URL}</span>
          </a>
        </Button>

        {hasChallenge ? (
          <div className="flex flex-col gap-4 rounded-xl border border-border bg-surface-2 p-4 sm:p-5">
            <div className="flex flex-col gap-1">
              <p className="text-caption font-semibold text-muted-foreground">
                Authentication code
              </p>
              <p className="break-all font-mono text-2xl font-medium tracking-wider text-foreground sm:text-3xl">
                {authentication.user_code}
              </p>
            </div>
            <div>
              <Button
                type="button"
                variant="outline"
                className="h-11 w-full sm:h-10 sm:w-auto"
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
