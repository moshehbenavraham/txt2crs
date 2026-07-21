import path from "node:path"
import { defineConfig, devices } from "@playwright/test"
import dotenv from "dotenv"

// Browser journeys target the judge-facing stack, whose single source of
// truth is the repository-root .env. Host-only frontend/.env values belong to
// direct Vite development and must never redirect the E2E API client.
const repositoryEnvironmentPath = path.resolve(import.meta.dirname, "../.env")
dotenv.config({ path: repositoryEnvironmentPath })

const frontendBaseURL =
  process.env.PLAYWRIGHT_BASE_URL ??
  process.env.FRONTEND_HOST ??
  "http://localhost:5195"
const backendPort = process.env.BACKEND_PORT ?? "8016"
const apiBaseURL =
  process.env.PLAYWRIGHT_API_URL ??
  process.env.VITE_API_URL ??
  `http://localhost:${backendPort}`

// Worker processes and existing test helpers consume this explicit value.
process.env.VITE_API_URL = apiBaseURL

const frontendPort = (() => {
  try {
    const port = new URL(frontendBaseURL).port
    return port || "5195"
  } catch {
    return "5195"
  }
})()

/**
 * Read environment variables from file.
 * https://github.com/motdotla/dotenv
 */

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  testDir: './tests',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: process.env.CI ? "blob" : "html",
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: frontendBaseURL,

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: "on-first-retry",
  },

  /* Configure projects for major browsers */
  projects: [
    { name: "setup", testMatch: /.*\.setup\.ts/ },

    {
      name: "chromium",
      use: {
        ...devices['Desktop Chrome'],
        storageState: "playwright/.auth/user.json",
      },
      dependencies: ["setup"],
    },

    // {
    //   name: 'firefox',
    //   use: {
    //     ...devices['Desktop Firefox'],
    //     storageState: 'playwright/.auth/user.json',
    //   },
    //   dependencies: ['setup'],
    // },

    // {
    //   name: 'webkit',
    //   use: {
    //     ...devices['Desktop Safari'],
    //     storageState: 'playwright/.auth/user.json',
    //   },
    //   dependencies: ['setup'],
    // },

    /* Test against mobile viewports. */
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] },
    // },

    /* Test against branded browsers. */
    // {
    //   name: 'Microsoft Edge',
    //   use: { ...devices['Desktop Edge'], channel: 'msedge' },
    // },
    // {
    //   name: 'Google Chrome',
    //   use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    // },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: `npm run dev -- --host 127.0.0.1 --port ${frontendPort} --strictPort`,
    url: frontendBaseURL,
    reuseExistingServer: !process.env.CI,
  },
})
