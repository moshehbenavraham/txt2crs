import { describe, expect, it } from "vitest"

import type { SystemAuthenticationState, SystemReadinessPublic } from "@/client"
import {
  getAuthenticationDisplay,
  getInputModeLabel,
  getReadinessDisplay,
  SYSTEM_CHECK_DEFINITIONS,
  SYSTEM_SETUP_CLI_COMMAND,
} from "./presentation"

const readiness = (
  overrides: Partial<SystemReadinessPublic> = {},
): SystemReadinessPublic => ({
  schema_version: "1.0",
  status: "ready",
  accepting_jobs: true,
  configured_model_id: "gpt-5.6-sol",
  enabled_input_modes: ["prompt", "text", "url"],
  checks: {
    authentication: "ready",
    model: "ready",
    research: "ready",
    storage: "ready",
    worker: "ready",
    inputs: "ready",
    admission: "ready",
    runtime_ownership: "ready",
  },
  warnings: [],
  recovery_actions: [],
  checked_at: "2026-07-19T18:00:00Z",
  is_fresh: true,
  ...overrides,
})

describe("system setup presentation", () => {
  it("uses one explicit verdict for ready, degraded, unavailable, and stale state", () => {
    expect(getReadinessDisplay(readiness())).toMatchObject({
      label: "Operational",
      title: "Platform ready",
      badgeVariant: "success",
    })
    expect(
      getReadinessDisplay(
        readiness({ status: "degraded", accepting_jobs: false }),
      ),
    ).toMatchObject({
      label: "Attention needed",
      title: "Setup needs attention",
      badgeVariant: "warning",
    })
    expect(
      getReadinessDisplay(
        readiness({ status: "unavailable", accepting_jobs: false }),
      ),
    ).toMatchObject({
      label: "Setup required",
      title: "Course system is unavailable",
      badgeVariant: "destructive",
    })
    expect(getReadinessDisplay(readiness({ is_fresh: false }))).toMatchObject({
      label: "Refresh overdue",
      title: "Readiness status is stale",
      badgeVariant: "warning",
    })
  })

  it.each<[SystemAuthenticationState, string, string, string | undefined]>([
    [
      "signed_out",
      "Not connected",
      "Connect ChatGPT (optional)",
      "Connect ChatGPT",
    ],
    ["waiting_for_user", "Waiting for approval", "Finish on OpenAI", undefined],
    ["authenticated", "Connected", "ChatGPT connected", undefined],
    [
      "failed",
      "Connection failed",
      "Reconnect ChatGPT",
      "Try connection again",
    ],
  ])(
    "maps %s authentication without inventing provider detail",
    (state, label, title, actionLabel) => {
      const display = getAuthenticationDisplay(state)

      expect(display.label).toBe(label)
      expect(display.title).toBe(title)
      expect(display.actionLabel).toBe(actionLabel)
      expect(JSON.stringify(display).toLowerCase()).not.toMatch(
        /oauth|access token|refresh token|account email|codex_home/,
      )
    },
  )

  it("keeps the complete coarse check order stable and numbered", () => {
    expect(SYSTEM_CHECK_DEFINITIONS.map((check) => check.key)).toEqual([
      "authentication",
      "model",
      "research",
      "storage",
      "worker",
      "inputs",
      "admission",
      "runtime_ownership",
    ])
    expect(SYSTEM_CHECK_DEFINITIONS.map((check) => check.index)).toEqual([
      "01",
      "02",
      "03",
      "04",
      "05",
      "06",
      "07",
      "08",
    ])
  })

  it("uses state-neutral check descriptions beside ready or unavailable badges", () => {
    const allCheckDescriptions = SYSTEM_CHECK_DEFINITIONS.map(
      (check) => check.description,
    ).join(" ")

    expect(allCheckDescriptions).not.toMatch(
      /\b(?:is|are) (?:connected|available|ready|enabled)|passed their checks|no other operation/i,
    )
  })

  it("uses human input labels and the documented package CLI command", () => {
    expect(getInputModeLabel("youtube")).toBe("YouTube")
    expect(getInputModeLabel("document")).toBe("Document")
    expect(getInputModeLabel("slides")).toBe("Slides")
    // Media adapters are optional capabilities, but an enabled one must still
    // render meaningful copy instead of an empty setup badge.
    expect(getInputModeLabel("image")).toBe("Image")
    expect(getInputModeLabel("audio")).toBe("Audio")
    expect(getInputModeLabel("video")).toBe("Video")
    expect(SYSTEM_SETUP_CLI_COMMAND).toBe(
      "uv run --package txt2crs txt2crs-system-auth",
    )
    expect(SYSTEM_SETUP_CLI_COMMAND).not.toMatch(
      /secret|token|password|codex-home/i,
    )
  })
})
