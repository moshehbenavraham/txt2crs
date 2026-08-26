import type {
  SystemAuthenticationState,
  SystemInputMode,
  SystemReadinessChecksPublic,
  SystemReadinessPublic,
} from "@/client"

export type SetupBadgeVariant =
  | "success"
  | "warning"
  | "destructive"
  | "info"
  | "secondary"

export type SetupAlertVariant =
  | "success"
  | "warning"
  | "destructive"
  | "info"
  | "default"

export interface ReadinessDisplay {
  label: string
  title: string
  description: string
  badgeVariant: SetupBadgeVariant
  alertVariant: SetupAlertVariant
}

export interface AuthenticationDisplay {
  label: string
  title: string
  description: string
  badgeVariant: SetupBadgeVariant
  alertVariant: SetupAlertVariant
  actionLabel?: string
}

export interface SystemCheckDefinition {
  key: keyof SystemReadinessChecksPublic
  index: string
  label: string
  description: string
}

/**
 * The API intentionally exposes only eight coarse checks. Keeping this list
 * explicit makes display order stable and prevents a future private field
 * from appearing just because it was added to an object.
 */
export const SYSTEM_CHECK_DEFINITIONS: readonly SystemCheckDefinition[] = [
  {
    key: "authentication",
    index: "01",
    label: "Codex credentials",
    description: "ChatGPT or API-key authentication for course generation.",
  },
  {
    key: "model",
    index: "02",
    label: "Configured model",
    description: "Configured generation model for the provider runtime.",
  },
  {
    key: "research",
    index: "03",
    label: "Research tools",
    description: "Reviewed tool boundary for evidence gathering.",
  },
  {
    key: "storage",
    index: "04",
    label: "Private storage",
    description: "Private persistence for course state and artifacts.",
  },
  {
    key: "worker",
    index: "05",
    label: "Course worker",
    description: "Serial worker responsible for durable generation jobs.",
  },
  {
    key: "inputs",
    index: "06",
    label: "Source inputs",
    description: "Input adapters that normalize supported source material.",
  },
  {
    key: "admission",
    index: "07",
    label: "Admission capacity",
    description: "Capacity gate for accepting another durable request.",
  },
  {
    key: "runtime_ownership",
    index: "08",
    label: "Runtime ownership",
    description: "Exclusive ownership guard for the provider runtime.",
  },
] as const

const INPUT_MODE_LABELS: Record<SystemInputMode, string> = {
  prompt: "Prompt",
  text: "Text",
  url: "Web page",
  youtube: "YouTube",
  pdf: "PDF",
  document: "Document",
  slides: "Slides",
  image: "Image",
  audio: "Audio",
  video: "Video",
}

export const SYSTEM_SETUP_CLI_COMMAND =
  "uv run --package txt2crs txt2crs-system-auth"

export function getInputModeLabel(inputMode: SystemInputMode): string {
  return INPUT_MODE_LABELS[inputMode]
}

export function getReadinessDisplay(
  readiness: Pick<
    SystemReadinessPublic,
    "status" | "accepting_jobs" | "is_fresh"
  >,
): ReadinessDisplay {
  // Freshness wins over a formerly-ready result. A stale cache cannot promise
  // that the system still accepts work.
  if (!readiness.is_fresh) {
    return {
      label: "Refresh overdue",
      title: "Readiness status is stale",
      description:
        "Refresh the system status before relying on the last known checks.",
      badgeVariant: "warning",
      alertVariant: "warning",
    }
  }

  if (readiness.status === "ready" && readiness.accepting_jobs) {
    return {
      label: "Operational",
      title: "Platform ready",
      description:
        "Core services and shared admission capacity are operational. Learner-specific availability appears in Create course.",
      badgeVariant: "success",
      alertVariant: "success",
    }
  }

  if (readiness.status === "unavailable") {
    return {
      label: "Setup required",
      title: "Course system is unavailable",
      description:
        "One or more required services need operator attention before course work can begin.",
      badgeVariant: "destructive",
      alertVariant: "destructive",
    }
  }

  return {
    label: "Attention needed",
    title: "Setup needs attention",
    description:
      "The system is reachable, but it is not currently accepting new course work.",
    badgeVariant: "warning",
    alertVariant: "warning",
  }
}

export function getAuthenticationDisplay(
  state: SystemAuthenticationState,
): AuthenticationDisplay {
  switch (state) {
    case "signed_out":
      return {
        label: "Not connected",
        title: "Connect ChatGPT (optional)",
        description:
          "Use device login when this installation does not authenticate with an API key.",
        badgeVariant: "secondary",
        alertVariant: "info",
        actionLabel: "Connect ChatGPT",
      }
    case "waiting_for_user":
      return {
        label: "Waiting for approval",
        title: "Finish on OpenAI",
        description:
          "Open the approved verification page and enter the short code shown here.",
        badgeVariant: "info",
        alertVariant: "info",
      }
    case "authenticated":
      return {
        label: "Connected",
        title: "ChatGPT connected",
        description: "The ChatGPT identity is available to the course runtime.",
        badgeVariant: "success",
        alertVariant: "success",
      }
    case "failed":
      return {
        label: "Connection failed",
        title: "Reconnect ChatGPT",
        description:
          "The previous ceremony ended safely. Start a new attempt when the runtime is available.",
        badgeVariant: "destructive",
        alertVariant: "destructive",
        actionLabel: "Try connection again",
      }
  }
}
