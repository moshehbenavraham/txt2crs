import { describe, expect, it } from "vitest"

import type { JobAdmissionCapacityPublic } from "@/client"
import {
  formatAdmissionWindow,
  getAdmissionCapacityDisplay,
} from "./presentation"

const capacity = (
  changes: Partial<JobAdmissionCapacityPublic> = {},
): JobAdmissionCapacityPublic => ({
  schema_version: "1.0",
  window_seconds: 86_400,
  owner_job_limit: 10,
  owner_jobs_used: 2,
  owner_jobs_remaining: 8,
  shared_jobs_remaining: 18,
  available_jobs: 8,
  next_reservation_expires_at: "2026-07-22T09:00:00Z",
  ...changes,
})

describe("course admission capacity presentation", () => {
  it("makes available work and owner usage immediately legible", () => {
    expect(getAdmissionCapacityDisplay(capacity())).toMatchObject({
      availableLabel: "8 generations ready",
      title: "Room to keep learning",
      usageLabel: "2 of 10 reservations used",
      usagePercentage: 20,
      isAvailable: true,
    })
  })

  it("uses honest exhausted and singular copy", () => {
    expect(
      getAdmissionCapacityDisplay(
        capacity({
          owner_jobs_used: 10,
          owner_jobs_remaining: 0,
          available_jobs: 0,
        }),
      ),
    ).toMatchObject({
      availableLabel: "No generations ready",
      title: "Your next opening is scheduled",
      isAvailable: false,
    })
    expect(
      getAdmissionCapacityDisplay(capacity({ available_jobs: 1 })),
    ).toMatchObject({ availableLabel: "1 generation ready" })
  })

  it("describes reviewed rolling windows without backend terminology", () => {
    expect(formatAdmissionWindow(86_400)).toBe("Rolling 24-hour window")
    expect(formatAdmissionWindow(3_600)).toBe("Rolling 1-hour window")
  })
})
