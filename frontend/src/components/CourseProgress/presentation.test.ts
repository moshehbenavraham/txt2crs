import { describe, expect, it } from "vitest"

import type { JobStatusPublic } from "@/client"
import {
  buildJobProgressPresentation,
  getActiveJobTimingPresentation,
  getInputWarningsPresentation,
  getProgressUnitsLabel,
} from "./presentation"

function jobSnapshot(
  status: JobStatusPublic["status"],
  stage: JobStatusPublic["progress"]["stage"],
): JobStatusPublic {
  return {
    job_id: "job-progress",
    status,
    revision: 2,
    progress: {
      stage,
      message: "Safe server progress.",
      completed_units: 3,
      total_units: 9,
    },
  } as JobStatusPublic
}

describe("course progress presentation", () => {
  it.each([
    ["accepted", "queued"],
    ["researching", "researching"],
    ["drafting", "drafting"],
    ["validating", "validating"],
    ["rendering", "rendering"],
    ["delivering", "delivering"],
  ] as const)("marks only the generated %s stage active", (status, stage) => {
    const presentation = buildJobProgressPresentation(
      jobSnapshot(status, stage),
    )

    expect(presentation.kind).toBe("active")
    expect(
      presentation.stages.filter((candidate) => candidate.state === "active"),
    ).toEqual([
      expect.objectContaining({
        id: stage,
      }),
    ])
  })

  it("completes the rail only for the generated completed/ready state", () => {
    const presentation = buildJobProgressPresentation(
      jobSnapshot("completed", "ready"),
    )

    expect(presentation.kind).toBe("completed")
    expect(presentation.heading).toBe("Course materials are ready")
    expect(
      presentation.stages.every((stage) => stage.state === "complete"),
    ).toBe(true)
  })

  it.each([
    ["failed", "failed", "Course generation stopped"],
    ["cancelled", "cancelled", "Course generation cancelled"],
  ] as const)(
    "renders a deliberate %s outcome without inventing a prior stage",
    (status, stage, heading) => {
      const presentation = buildJobProgressPresentation(
        jobSnapshot(status, stage),
      )

      expect(presentation.kind).toBe(status)
      expect(presentation.heading).toBe(heading)
      expect(
        presentation.stages.every(
          (candidate) => candidate.state === "inactive",
        ),
      ).toBe(true)
    },
  )

  it("describes known and unknown unit totals without inventing a percentage", () => {
    expect(getProgressUnitsLabel({ completed_units: 3, total_units: 9 })).toBe(
      "3 of 9 course-building steps confirmed",
    )
    expect(
      getProgressUnitsLabel({ completed_units: 3, total_units: null }),
    ).toBe("3 course-building steps confirmed")
  })

  it("derives live elapsed, activity, and pace-based remaining time from confirmed backend timestamps", () => {
    expect(
      getActiveJobTimingPresentation(
        {
          created_at: "2026-07-21T10:00:00Z",
          updated_at: "2026-07-21T10:01:00Z",
          runtime_activity_at: "2026-07-21T10:01:18Z",
          progress: {
            completed_units: 4,
            total_units: 12,
          },
        },
        Date.parse("2026-07-21T10:01:20Z"),
      ),
    ).toEqual({
      elapsedTimeLabel: "1m 20s",
      estimatedTimeLeftLabel: "~2m 0s",
      latestCheckpointLabel: "20s ago",
      latestRuntimeActivityLabel: "just now",
      progressPercentage: 33,
    })
  })

  it("keeps the ETA honest when there is not enough confirmed pace data", () => {
    const nowMilliseconds = Date.parse("2026-07-21T10:02:00Z")
    const baseSnapshot = {
      created_at: "2026-07-21T10:00:00Z",
      updated_at: "2026-07-21T10:01:00Z",
      runtime_activity_at: null,
    }

    expect(
      getActiveJobTimingPresentation(
        {
          ...baseSnapshot,
          progress: { completed_units: 0, total_units: 12 },
        },
        nowMilliseconds,
      ).estimatedTimeLeftLabel,
    ).toBe("Calculating")
    expect(
      getActiveJobTimingPresentation(
        {
          ...baseSnapshot,
          progress: { completed_units: 3, total_units: null },
        },
        nowMilliseconds,
      ).estimatedTimeLeftLabel,
    ).toBe("Calculating")
    expect(
      getActiveJobTimingPresentation(
        {
          ...baseSnapshot,
          progress: { completed_units: 12, total_units: 12 },
        },
        nowMilliseconds,
      ).estimatedTimeLeftLabel,
    ).toBe("Finalizing")
    expect(
      getActiveJobTimingPresentation(
        {
          ...baseSnapshot,
          progress: { completed_units: 6, total_units: 12 },
        },
        Date.parse("2026-07-21T10:03:00Z"),
      ).estimatedTimeLeftLabel,
    ).toBe("~1m 0s")
  })

  it("keeps checkpoint and runtime activity truthful when no worker heartbeat exists", () => {
    const presentation = getActiveJobTimingPresentation(
      {
        created_at: "2026-07-21T10:00:00Z",
        updated_at: "2026-07-21T10:01:00Z",
        runtime_activity_at: null,
        progress: { completed_units: 4, total_units: 12 },
      },
      Date.parse("2026-07-21T10:01:20Z"),
    )

    expect(presentation.latestCheckpointLabel).toBe("20s ago")
    expect(presentation.latestRuntimeActivityLabel).toBe("Awaiting worker")
  })

  it("preserves bounded extraction warnings and names a truncated remainder", () => {
    expect(
      getInputWarningsPresentation({
        extraction_warnings: [
          "One embedded chart could not be read.",
          "Speaker notes were not included.",
        ],
        warnings_truncated: true,
      }),
    ).toEqual({
      warnings: [
        "One embedded chart could not be read.",
        "Speaker notes were not included.",
      ],
      hasAdditionalWarnings: true,
    })
    expect(
      getInputWarningsPresentation({
        extraction_warnings: [],
        warnings_truncated: false,
      }),
    ).toBeNull()
  })
})
