import type { JobAdmissionCapacityPublic } from "@/client"

export interface AdmissionCapacityDisplay {
  availableLabel: string
  isAvailable: boolean
  title: string
  usageLabel: string
  usagePercentage: number
}

/** Translate seconds into the rolling-window language learners need. */
export function formatAdmissionWindow(windowSeconds: number): string {
  const wholeHours = windowSeconds / 3_600
  if (Number.isInteger(wholeHours)) {
    return `Rolling ${wholeHours}-hour window`
  }
  const wholeMinutes = Math.round(windowSeconds / 60)
  return `Rolling ${wholeMinutes}-minute window`
}

/** Format the exact expiry in the learner's locale while preserving UTC data. */
export function formatReservationExpiry(expiry: string): string {
  const parsedExpiry = new Date(expiry)
  if (Number.isNaN(parsedExpiry.getTime())) {
    return "Reset time unavailable"
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(parsedExpiry)
}

/** Build singular-aware, non-technical copy for the capacity strip. */
export function getAdmissionCapacityDisplay(
  capacity: JobAdmissionCapacityPublic,
): AdmissionCapacityDisplay {
  const isAvailable = capacity.available_jobs > 0
  const generationNoun =
    capacity.available_jobs === 1 ? "generation" : "generations"
  const usagePercentage = Math.min(
    Math.round((capacity.owner_jobs_used / capacity.owner_job_limit) * 100),
    100,
  )

  return {
    availableLabel: isAvailable
      ? `${capacity.available_jobs} ${generationNoun} ready`
      : "No generations ready",
    isAvailable,
    title: isAvailable
      ? "Room to keep learning"
      : "Your next opening is scheduled",
    usageLabel: `${capacity.owner_jobs_used} of ${capacity.owner_job_limit} reservations used`,
    usagePercentage,
  }
}
