import { expect, type Page, test } from "@playwright/test"

import type {
  SystemAuthenticationPublic,
  SystemReadinessPublic,
  UserPublic,
} from "../src/client/types.gen"

const CODEX_DEVICE_AUTH_URL = "https://auth.openai.com/codex/device"

const readySystem: SystemReadinessPublic = {
  schema_version: "1.0",
  status: "ready",
  accepting_jobs: true,
  configured_model_id: "gpt-5.6-sol",
  enabled_input_modes: [
    "prompt",
    "text",
    "url",
    "youtube",
    "pdf",
    "document",
    "slides",
    "image",
    "audio",
    "video",
  ],
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
}

const signedOut: SystemAuthenticationPublic = {
  state: "signed_out",
  verification_url: null,
  user_code: null,
  message: "Dedicated ChatGPT subscription is not connected.",
}

const waiting: SystemAuthenticationPublic = {
  state: "waiting_for_user",
  verification_url: CODEX_DEVICE_AUTH_URL,
  user_code: "ABCD-1234",
  message: "Open the verification page and enter the short code.",
}

const authenticated: SystemAuthenticationPublic = {
  state: "authenticated",
  verification_url: null,
  user_code: null,
  message: "Dedicated ChatGPT subscription is connected.",
}

async function mockSystemState(
  page: Page,
  {
    readiness = readySystem,
    authentication = signedOut,
    start = waiting,
  }: {
    readiness?: SystemReadinessPublic
    authentication?: SystemAuthenticationPublic
    start?: SystemAuthenticationPublic
  } = {},
) {
  await page.route("**/api/v1/system/readiness", (route) =>
    route.fulfill({ status: 200, json: readiness }),
  )
  await page.route("**/api/v1/system/auth/status", (route) =>
    route.fulfill({ status: 200, json: authentication }),
  )
  await page.route("**/api/v1/system/auth/start", (route) =>
    route.fulfill({ status: 200, json: start }),
  )
}

test("superuser navigation opens the complete safe setup workspace", async ({
  page,
}) => {
  await mockSystemState(page)
  await page.goto("/setup")

  await expect(
    page.getByRole("heading", { name: "System setup" }),
  ).toBeVisible()
  await expect(page.getByText("Platform ready", { exact: true })).toBeVisible()
  await expect(page.getByText("gpt-5.6-sol", { exact: true })).toBeVisible()
  await expect(page.getByText("Image", { exact: true })).toBeVisible()
  await expect(page.getByText("Audio", { exact: true })).toBeVisible()
  await expect(page.getByText("Video", { exact: true })).toBeVisible()
  await expect(
    page.getByRole("heading", { name: "System checks" }),
  ).toBeVisible()
  await expect(
    page.getByRole("button", { name: "Connect ChatGPT" }),
  ).toBeVisible()
  const deviceAuthenticationLink = page.getByRole("link", {
    name: "Open Codex device authentication",
  })
  await expect(deviceAuthenticationLink).toBeVisible()
  await expect(deviceAuthenticationLink).toHaveAttribute(
    "href",
    CODEX_DEVICE_AUTH_URL,
  )
  await expect(deviceAuthenticationLink).toContainText(CODEX_DEVICE_AUTH_URL)
  await expect(
    page.getByText(/oauth|access token|refresh token|codex_home/i),
  ).toHaveCount(0)
})

test("non-superusers redirect before any system endpoint request", async ({
  page,
}) => {
  let systemRequestCount = 0
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/system/")) {
      systemRequestCount += 1
    }
  })
  const normalUser: UserPublic = {
    id: "11111111-1111-4111-8111-111111111111",
    email: "learner@example.com",
    full_name: "Learner",
    is_active: true,
    is_superuser: false,
  }
  await page.route("**/api/v1/users/me", (route) =>
    route.fulfill({ status: 200, json: normalUser }),
  )

  await page.goto("/setup")

  await expect(page).toHaveURL(/\/forbidden$/)
  await expect(
    page.getByRole("heading", { name: "Not authorized" }),
  ).toBeVisible()
  expect(systemRequestCount).toBe(0)
})

test("device ceremony starts, copies safe code, polls, and removes terminal challenge", async ({
  context,
  page,
}) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"])
  let readinessReads = 0
  let statusReads = 0
  let ceremonyStarted = false
  await page.route("**/api/v1/system/readiness", (route) => {
    readinessReads += 1
    return route.fulfill({ status: 200, json: readySystem })
  })
  await page.route("**/api/v1/system/auth/start", (route) => {
    ceremonyStarted = true
    return route.fulfill({ status: 200, json: waiting })
  })
  await page.route("**/api/v1/system/auth/status", (route) => {
    statusReads += 1
    const authenticationState =
      ceremonyStarted && statusReads >= 3
        ? authenticated
        : ceremonyStarted
          ? waiting
          : signedOut
    return route.fulfill({
      status: 200,
      json: authenticationState,
    })
  })
  await page.goto("/setup")

  await page.getByRole("button", { name: "Connect ChatGPT" }).click()
  await expect(page.getByText("ABCD-1234", { exact: true })).toBeVisible()
  const verificationLink = page.getByRole("link", {
    name: "Open Codex device authentication",
  })
  await expect(verificationLink).toHaveAttribute("href", CODEX_DEVICE_AUTH_URL)
  await page.getByRole("button", { name: "Copy authentication code" }).click()
  await expect(page.getByRole("status")).toContainText("Code copied")

  await expect(
    page.getByRole("heading", { name: "ChatGPT connected" }),
  ).toBeVisible({ timeout: 5000 })
  await expect(page.getByRole("status")).not.toContainText("Code copied")
  await expect(page.getByText("ABCD-1234", { exact: true })).toHaveCount(0)
  await expect(verificationLink).toBeVisible()
  await expect(verificationLink).toHaveAttribute("href", CODEX_DEVICE_AUTH_URL)
  expect(statusReads).toBeGreaterThanOrEqual(3)
  expect(readinessReads).toBeGreaterThanOrEqual(2)
})

test("an already-authenticated page does not refetch readiness on mount", async ({
  page,
}) => {
  let readinessReads = 0
  await page.route("**/api/v1/system/readiness", (route) => {
    readinessReads += 1
    return route.fulfill({ status: 200, json: readySystem })
  })
  await page.route("**/api/v1/system/auth/status", (route) =>
    route.fulfill({ status: 200, json: authenticated }),
  )

  await page.goto("/setup")
  await expect(
    page.getByRole("heading", { name: "ChatGPT connected" }),
  ).toBeVisible()
  await expect(
    page.getByRole("link", { name: "Open Codex device authentication" }),
  ).toHaveAttribute("href", CODEX_DEVICE_AUTH_URL)
  // Give effects and query notifications time to settle so a duplicate
  // invalidation cannot pass by briefly reporting only the first request.
  await page.waitForTimeout(300)

  expect(readinessReads).toBe(1)
})

test("bounded long codes and repeated safe values remain responsive without key warnings", async ({
  page,
}) => {
  const repeatedValueReadiness: SystemReadinessPublic = {
    ...readySystem,
    enabled_input_modes: ["prompt", "prompt"],
    warnings: ["Repeatable safe warning.", "Repeatable safe warning."],
    recovery_actions: [
      "Repeatable safe recovery action.",
      "Repeatable safe recovery action.",
    ],
  }
  const longestAllowedCode = "A".repeat(64)
  const longCodeWaiting: SystemAuthenticationPublic = {
    ...waiting,
    user_code: longestAllowedCode,
  }
  const duplicateKeyWarnings: string[] = []
  page.on("console", (message) => {
    if (message.type() === "error" && message.text().includes("same key")) {
      duplicateKeyWarnings.push(message.text())
    }
  })
  await page.setViewportSize({ width: 320, height: 700 })
  await mockSystemState(page, {
    readiness: repeatedValueReadiness,
    authentication: longCodeWaiting,
  })

  await page.goto("/setup")

  const authenticationCode = page.getByText(longestAllowedCode, {
    exact: true,
  })
  await expect(authenticationCode).toBeVisible()
  expect(
    await page
      .getByText(
        "Core services and shared admission capacity are operational. Learner-specific availability appears in Create course.",
        { exact: true },
      )
      .evaluate((element) => element.getBoundingClientRect().width),
  ).toBeGreaterThanOrEqual(200)
  expect(
    await page
      .getByText("ChatGPT or API-key authentication for course generation.", {
        exact: true,
      })
      .evaluate((element) => element.getBoundingClientRect().width),
  ).toBeGreaterThanOrEqual(150)
  expect(
    await authenticationCode.evaluate(
      (element) => element.scrollWidth - element.clientWidth,
    ),
  ).toBeLessThanOrEqual(0)
  expect(
    await page.evaluate(
      () =>
        document.documentElement.scrollWidth -
        document.documentElement.clientWidth,
    ),
  ).toBeLessThanOrEqual(0)
  expect(duplicateKeyWarnings).toEqual([])
})

test("unavailable and failed states stay actionable, responsive, dark, and still", async ({
  page,
}) => {
  await page.addInitScript(() => {
    localStorage.setItem("vite-ui-theme", "dark")
  })
  await page.emulateMedia({ reducedMotion: "reduce" })
  await page.setViewportSize({ width: 375, height: 812 })
  await mockSystemState(page, {
    readiness: {
      ...readySystem,
      status: "unavailable",
      accepting_jobs: false,
      checks: {
        ...readySystem.checks,
        authentication: "unavailable",
        research: "unavailable",
      },
      warnings: ["Dedicated ChatGPT authentication is required."],
      recovery_actions: ["Connect ChatGPT, then refresh readiness."],
    },
    authentication: {
      state: "failed",
      verification_url: null,
      user_code: null,
      message: "System authentication failed. Start a new attempt.",
    },
  })

  await page.goto("/setup")

  await expect(page.locator("html")).toHaveClass(/dark/)
  await expect(
    page.getByText("Course system is unavailable", { exact: true }),
  ).toBeVisible()
  await expect(
    page.getByRole("button", { name: "Try connection again" }),
  ).toBeVisible()
  await expect(
    page.getByRole("link", { name: "Open Codex device authentication" }),
  ).toHaveAttribute("href", CODEX_DEVICE_AUTH_URL)
  const safeAuthenticationMessage = page.getByText(
    "System authentication failed. Start a new attempt.",
    { exact: true },
  )
  await expect(safeAuthenticationMessage).toBeVisible()
  expect(
    await safeAuthenticationMessage.evaluate(
      (element) => getComputedStyle(element).webkitLineClamp,
    ),
  ).toBe("none")
  await expect(
    page.getByText("uv run --package txt2crs txt2crs-system-auth"),
  ).toBeVisible()
  const recoveryCommand = page.locator("pre").filter({
    hasText: "uv run --package txt2crs txt2crs-system-auth",
  })
  expect(
    await recoveryCommand.evaluate(
      (element) => element.scrollWidth - element.clientWidth,
    ),
  ).toBeLessThanOrEqual(0)
  await expect(page.getByRole("status")).toContainText(
    "Course system is unavailable",
  )
  expect(
    await page.evaluate(
      () =>
        document.documentElement.scrollWidth -
        document.documentElement.clientWidth,
    ),
  ).toBeLessThanOrEqual(0)

  await page.keyboard.press("Tab")
  const focusedElement = page.locator(":focus")
  await expect(focusedElement).toBeVisible()
  const animationSeconds = await page
    .getByRole("region", { name: "System status" })
    .evaluate((element) =>
      Number.parseFloat(getComputedStyle(element).animationDuration || "0"),
    )
  expect(animationSeconds).toBeLessThan(0.05)
})
