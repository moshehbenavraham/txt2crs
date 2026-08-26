import { expect, type Page, test } from "@playwright/test"

import type {
  JobLibraryPublic,
  JobLibrarySummaryPublic,
  JobStatus,
} from "../src/client"

const libraryEndpointPattern = "**/api/v1/jobs*"
const longCourseTitle = "W".repeat(500)

function libraryJob(
  jobId: string,
  status: JobStatus,
  title: string,
): JobLibrarySummaryPublic {
  const isActive = !["completed", "failed", "cancelled"].includes(status)
  const failure =
    status === "failed"
      ? {
          code: "generation_failed" as const,
          message: "Course generation could not be completed.",
        }
      : status === "cancelled"
        ? {
            code: "cancelled" as const,
            message: "Course generation was cancelled.",
          }
        : null
  return {
    schema_version: "1.0",
    job_id: jobId,
    revision: isActive ? 2 : 8,
    status,
    title,
    input_type: "prompt",
    created_at: "2026-07-20T09:00:00Z",
    updated_at: "2026-07-20T09:15:00Z",
    progress: {
      stage:
        status === "completed"
          ? "ready"
          : status === "failed"
            ? "failed"
            : status === "cancelled"
              ? "cancelled"
              : "researching",
      message:
        status === "completed"
          ? "Your course materials are ready."
          : "Researching authoritative sources for your course.",
      completed_units: isActive ? 2 : 8,
      total_units: isActive ? null : 8,
    },
    failure,
    artifacts: {
      available: status === "completed",
      count: status === "completed" ? 16 : 0,
      manifest_url:
        status === "completed" ? `/api/v1/jobs/${jobId}/artifacts` : null,
    },
  }
}

function pageWithoutContinuation(
  data: JobLibrarySummaryPublic[],
): JobLibraryPublic {
  return { schema_version: "1.0", data, next_cursor: null }
}

async function horizontalOverflow(page: Page): Promise<number> {
  return page.evaluate(
    () =>
      document.documentElement.scrollWidth -
      document.documentElement.clientWidth,
  )
}

function captureBrowserFailures(page: Page): string[] {
  // Browser-only failures can leave the DOM partially usable while hiding a
  // serious runtime problem. Keep them as test evidence instead of relying on
  // the terminal output from Vite or Playwright's web server.
  const browserFailures: string[] = []
  page.on("console", (message) => {
    if (message.type() === "error") {
      browserFailures.push(`console: ${message.text()}`)
    }
  })
  page.on("pageerror", (error) => {
    browserFailures.push(`pageerror: ${error.message}`)
  })
  return browserFailures
}

test.describe("course library", () => {
  test("shows loading and empty recovery with persistent desktop and mobile navigation", async ({
    page,
  }) => {
    // Annotate the gate explicitly. Without it TypeScript infers `() => never`
    // from the throwing placeholder, and the later `resolve` assignment (which
    // returns `void`) becomes a type error.
    let releaseLibraryResponse: () => void = () => {
      throw new Error("The library response gate was not initialized.")
    }
    const libraryResponseGate = new Promise<void>((resolve) => {
      releaseLibraryResponse = resolve
    })
    await page.route(libraryEndpointPattern, async (route) => {
      await libraryResponseGate
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        json: pageWithoutContinuation([]),
      })
    })

    await page.setViewportSize({ width: 1440, height: 900 })
    await page.goto("/library")
    await expect(
      page.getByRole("region", { name: "Loading courses" }),
    ).toBeVisible()
    releaseLibraryResponse()

    await expect(
      page.getByRole("heading", { name: "My courses" }),
    ).toBeVisible()
    await expect(
      page.getByRole("heading", { name: "Your course shelf is ready" }),
    ).toBeVisible()
    await expect(page.getByRole("link", { name: "My courses" })).toBeVisible()

    await page.setViewportSize({ width: 375, height: 812 })
    await page.getByRole("button", { name: /Sidebar/ }).click()
    const mobileLibraryLink = page.getByRole("link", { name: "My courses" })
    await expect(mobileLibraryLink).toBeVisible()
    await mobileLibraryLink.focus()
    await expect(mobileLibraryLink).toBeFocused()
    expect(await horizontalOverflow(page)).toBeLessThanOrEqual(0)
  })

  test("offers a safe retry for a permanent collection error", async ({
    page,
  }) => {
    let collectionReadCount = 0
    await page.route(libraryEndpointPattern, async (route) => {
      collectionReadCount += 1
      await route.fulfill({
        status: 422,
        contentType: "application/problem+json",
        json: {
          type: "about:blank",
          title: "Invalid course library page",
          status: 422,
          detail: "The private cursor detail must not reach the page.",
          code: "VALIDATION_4001",
          trace_id: "library-browser-test",
        },
      })
    })

    await page.goto("/library")
    await expect(
      page.getByText("Your course library could not be loaded"),
    ).toBeVisible()
    await expect(page.getByText("private cursor detail")).toHaveCount(0)
    await page.getByRole("button", { name: "Try again" }).click()
    await expect.poll(() => collectionReadCount).toBe(2)
  })

  test("renders exhaustive states, long titles, pagination, themes, and responsive actions", async ({
    page,
  }) => {
    const browserFailures = captureBrowserFailures(page)
    const firstPage: JobLibraryPublic = {
      schema_version: "1.0",
      data: [
        libraryJob("job-active", "researching", longCourseTitle),
        libraryJob("job-completed", "completed", "Python variables"),
        libraryJob("job-failed", "failed", "Database indexes"),
        libraryJob("job-cancelled", "cancelled", "Tidal ecology"),
      ],
      next_cursor: "opaque-older-page",
    }
    const secondPage = pageWithoutContinuation([
      libraryJob("job-older", "completed", "Accessible course design"),
    ])
    const requestedCursors: Array<string | null> = []
    await page.route(libraryEndpointPattern, async (route) => {
      const cursor = new URL(route.request().url()).searchParams.get("cursor")
      requestedCursors.push(cursor)
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        json: cursor === "opaque-older-page" ? secondPage : firstPage,
      })
    })

    await page.setViewportSize({ width: 1440, height: 900 })
    await page.goto("/library")
    await expect(page.getByText("In progress", { exact: true })).toBeVisible()
    await expect(page.getByText("Ready", { exact: true })).toBeVisible()
    await expect(
      page.getByText("Needs attention", { exact: true }),
    ).toBeVisible()
    await expect(page.getByText("Cancelled", { exact: true })).toBeVisible()
    await expect(page.getByText(longCourseTitle)).toBeVisible()
    expect(await horizontalOverflow(page)).toBeLessThanOrEqual(0)

    const completedCourseLink = page.getByRole("link", {
      name: "Open course",
      exact: true,
    })
    await expect(completedCourseLink).toHaveAttribute(
      "href",
      "/jobs/job-completed",
    )
    await completedCourseLink.focus()
    await expect(completedCourseLink).toBeFocused()

    await page.getByRole("button", { name: "Load older courses" }).click()
    await expect(page.getByText("Accessible course design")).toBeVisible()
    expect(requestedCursors).toContain("opaque-older-page")
    await expect(
      page.getByRole("button", { name: "Load older courses" }),
    ).toHaveCount(0)

    await page.evaluate(() => {
      localStorage.setItem("vite-ui-theme", "light")
    })
    await page.reload()
    await expect(page.locator("html")).toHaveClass(/light/)
    await expect(page.getByText(longCourseTitle)).toBeVisible()
    await page.screenshot({
      fullPage: true,
      path: "/tmp/txt2crs-course-library-light-desktop.png",
    })

    await page.setViewportSize({ width: 375, height: 812 })
    await page.evaluate(() => {
      localStorage.setItem("vite-ui-theme", "dark")
    })
    await page.reload()
    await expect(page.locator("html")).toHaveClass(/dark/)
    const longTitle = page.getByText(longCourseTitle)
    await expect(longTitle).toBeVisible()
    const longTitleLayout = await longTitle.evaluate((title) => {
      const bounds = title.getBoundingClientRect()
      return {
        right: bounds.right,
        viewportWidth: window.innerWidth,
        scrollWidth: title.scrollWidth,
        clientWidth: title.clientWidth,
      }
    })
    expect(longTitleLayout.right).toBeLessThanOrEqual(
      longTitleLayout.viewportWidth,
    )
    expect(longTitleLayout.scrollWidth).toBeLessThanOrEqual(
      longTitleLayout.clientWidth,
    )
    expect(await horizontalOverflow(page)).toBeLessThanOrEqual(0)
    const actionTargetFailures = await page
      .getByRole("link", { name: /View progress|Open course|Review job/ })
      .evaluateAll((links) =>
        links
          .filter((link) => link.getBoundingClientRect().height < 44)
          .map((link) => link.textContent?.trim() ?? ""),
      )
    expect(actionTargetFailures).toEqual([])
    await page.screenshot({
      fullPage: true,
      path: "/tmp/txt2crs-course-library-dark-mobile.png",
    })
    await expect(page.locator("vite-error-overlay")).toHaveCount(0)
    expect(browserFailures).toEqual([])
  })
})
