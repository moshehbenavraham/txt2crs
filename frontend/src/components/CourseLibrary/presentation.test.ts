import { describe, expect, it } from "vitest"

import type { JobLibrarySummaryPublic } from "@/client"
import { getLibraryJobPresentation } from "./presentation"

const summary = (
  status: JobLibrarySummaryPublic["status"],
): JobLibrarySummaryPublic =>
  ({
    job_id: "job-library",
    status,
    progress: {
      stage: status === "completed" ? "ready" : "queued",
      message:
        status === "completed"
          ? "Your course materials are ready."
          : "Your course request is queued.",
      completed_units: 0,
      total_units: null,
    },
    artifacts: { available: status === "completed", count: 0 },
  }) as JobLibrarySummaryPublic

describe("course library presentation", () => {
  it.each([
    ["accepted", "In progress", "View progress"],
    ["researching", "In progress", "View progress"],
    ["drafting", "In progress", "View progress"],
    ["validating", "In progress", "View progress"],
    ["rendering", "In progress", "View progress"],
    ["delivering", "In progress", "View progress"],
    ["completed", "Ready", "Open course"],
    ["failed", "Needs attention", "Review job"],
    ["cancelled", "Cancelled", "Review job"],
  ] as const)(
    "maps %s to exhaustive learner-facing status and action copy",
    (status, label, actionLabel) => {
      expect(getLibraryJobPresentation(summary(status))).toMatchObject({
        label,
        actionLabel,
      })
    },
  )
})
