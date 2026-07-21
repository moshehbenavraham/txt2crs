import { describe, expect, it } from "vitest"

import { buildLoginHref, normalizeAuthReturnTo } from "./auth-return"

describe("authentication return paths", () => {
  it("preserves an owner-scoped job deep link including query and hash", () => {
    expect(normalizeAuthReturnTo("/jobs/job-123?view=progress#current")).toBe(
      "/jobs/job-123?view=progress#current",
    )
    expect(buildLoginHref("/jobs/job-123?view=progress#current")).toBe(
      "/login?returnTo=%2Fjobs%2Fjob-123%3Fview%3Dprogress%23current",
    )
  })

  it.each([
    "https://attacker.example/jobs/job-123",
    "//attacker.example/jobs/job-123",
    "/\\attacker.example/jobs/job-123",
    "/login",
    "/login?returnTo=/jobs/job-123",
    "jobs/job-123",
  ])("rejects unsafe or recursive return target %s", (candidate) => {
    expect(normalizeAuthReturnTo(candidate)).toBe("/create")
  })
})
