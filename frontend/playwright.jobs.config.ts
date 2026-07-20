import { mkdtempSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import path from "node:path"
import { defineConfig, devices } from "@playwright/test"
import "dotenv/config"

const backendBaseUrl = "http://127.0.0.1:8017"
const frontendBaseUrl = "http://127.0.0.1:5197"
const inheritedBrowserTestRootDirectory =
  process.env.TXT2CRS_BROWSER_TEST_ROOT_DIRECTORY
const browserTestRootDirectory =
  inheritedBrowserTestRootDirectory ??
  mkdtempSync(path.join(tmpdir(), "txt2crs-browser-"))
const browserTestUserEmail =
  process.env.PLAYWRIGHT_TEST_USER_EMAIL ??
  `browser-${process.pid}-${Date.now()}@example.com`
const browserTestUserPassword = "Browser-only-123!"
const jobsAuthFile = path.join(browserTestRootDirectory, "jobs-user.json")
const deterministicStateDirectory = path.join(browserTestRootDirectory, "state")

const requestedScenario = process.env.TXT2CRS_BROWSER_SCENARIO ?? "complete"
if (requestedScenario !== "complete" && requestedScenario !== "failed") {
  throw new Error("TXT2CRS_BROWSER_SCENARIO must be either complete or failed.")
}

// The setup test and learner scenarios read these values in their worker
// processes. Assigning them before Playwright forks keeps the dedicated run
// independent from the Compose-driven default configuration.
process.env.VITE_API_URL = backendBaseUrl
process.env.PLAYWRIGHT_AUTH_FILE = jobsAuthFile
process.env.PLAYWRIGHT_CREATE_USER = "1"
process.env.PLAYWRIGHT_JOBS_FIXTURE = "1"
process.env.PLAYWRIGHT_TEST_USER_EMAIL = browserTestUserEmail
process.env.PLAYWRIGHT_TEST_USER_PASSWORD = browserTestUserPassword
process.env.TXT2CRS_BROWSER_SCENARIO = requestedScenario
process.env.TXT2CRS_BROWSER_TEST_ROOT_DIRECTORY = browserTestRootDirectory

// The deterministic engine closes SQLite and artifact descriptors during the
// ASGI lifespan. Once Playwright has stopped both web servers, this process
// removes the now-unowned temporary directory. Worker processes inherit the
// root and must not delete it when their individual project exits.
if (inheritedBrowserTestRootDirectory === undefined) {
  process.once("exit", () => {
    rmSync(browserTestRootDirectory, { recursive: true, force: true })
  })
}

export default defineConfig({
  testDir: "./tests",
  testMatch: ["auth.setup.ts", "auth.teardown.ts", "course-journey.spec.ts"],
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: process.env.CI ? "blob" : "list",
  use: {
    baseURL: frontendBaseUrl,
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "setup",
      testMatch: /.*\.setup\.ts/,
      teardown: "cleanup",
    },
    {
      name: "cleanup",
      testMatch: /.*\.teardown\.ts/,
    },
    {
      name: "chromium",
      testIgnore: /.*\.(setup|teardown)\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        storageState: jobsAuthFile,
      },
      dependencies: ["setup"],
    },
  ],
  webServer: [
    {
      command:
        "uv run --directory ../backend uvicorn " +
        "tests.browser.deterministic_app:" +
        "create_deterministic_browser_app_from_environment --factory " +
        "--host 127.0.0.1 --port 8017",
      url: `${backendBaseUrl}/api/v1/utils/health-check/`,
      reuseExistingServer: false,
      timeout: 30_000,
      stdout: "pipe",
      stderr: "pipe",
      env: {
        TXT2CRS_ENABLE_BROWSER_TEST_APP: "1",
        TXT2CRS_BROWSER_TEST_STATE_DIRECTORY: deterministicStateDirectory,
        TXT2CRS_BROWSER_TEST_SCENARIO: requestedScenario,
        TXT2CRS_BROWSER_TEST_FRONTEND_HOST: frontendBaseUrl,
        // The login CSRF dependency intentionally reads the process-level
        // Settings singleton, so its normal allowed origin must match Vite.
        FRONTEND_HOST: frontendBaseUrl,
        ENABLE_PUBLIC_SIGNUP: "true",
      },
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 5197 --strictPort",
      url: frontendBaseUrl,
      reuseExistingServer: false,
      timeout: 30_000,
      stdout: "pipe",
      stderr: "pipe",
      env: {
        VITE_API_URL: backendBaseUrl,
      },
    },
  ],
})
