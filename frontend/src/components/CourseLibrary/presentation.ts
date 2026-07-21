import type { JobLibrarySummaryPublic } from "@/client"

export type LibraryBadgeVariant = "info" | "success" | "destructive" | "outline"

interface LibraryJobPresentation {
  label: string
  actionLabel: string
  badgeVariant: LibraryBadgeVariant
  message: string
  isActive: boolean
}

/**
 * Convert every durable engine status into one exhaustive learner-facing row.
 * Keeping this as a switch means a generated API status addition fails type
 * checking until its visual state and action copy are deliberately reviewed.
 */
export function getLibraryJobPresentation(
  summary: JobLibrarySummaryPublic,
): LibraryJobPresentation {
  switch (summary.status) {
    case "accepted":
    case "researching":
    case "drafting":
    case "validating":
    case "rendering":
    case "delivering":
      return {
        label: "In progress",
        actionLabel: "View progress",
        badgeVariant: "info",
        message: summary.progress.message,
        isActive: true,
      }
    case "completed":
      return {
        label: "Ready",
        actionLabel: "Open course",
        badgeVariant: "success",
        message: summary.progress.message,
        isActive: false,
      }
    case "failed":
      return {
        label: "Needs attention",
        actionLabel: "Review job",
        badgeVariant: "destructive",
        message:
          summary.failure?.message ??
          "Course generation could not be completed.",
        isActive: false,
      }
    case "cancelled":
      return {
        label: "Cancelled",
        actionLabel: "Review job",
        badgeVariant: "outline",
        message: summary.failure?.message ?? "Course generation was cancelled.",
        isActive: false,
      }
    default: {
      const exhaustiveStatus: never = summary.status
      return exhaustiveStatus
    }
  }
}

/** Return a short source label without exposing any raw learner input. */
export function getLibraryInputLabel(
  inputType: JobLibrarySummaryPublic["input_type"],
): string {
  switch (inputType) {
    case "prompt":
      return "prompt"
    case "text":
      return "pasted text"
    case "url":
      return "web source"
    case "pdf":
      return "PDF"
    case "document":
      return "document"
    case "slides":
      return "presentation"
    case "image":
      return "image"
    case "audio":
      return "audio"
    case "video":
      return "video"
    default: {
      const exhaustiveInputType: never = inputType
      return exhaustiveInputType
    }
  }
}

/** Format the server timestamp predictably and retain the raw value in time. */
export function formatLibraryTimestamp(timestamp: string): string {
  const parsedTimestamp = new Date(timestamp)
  if (Number.isNaN(parsedTimestamp.getTime())) {
    return "Time unavailable"
  }
  return new Intl.DateTimeFormat("en", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZone: "UTC",
    timeZoneName: "short",
  }).format(parsedTimestamp)
}
