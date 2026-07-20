import { expect, type Page, test } from "@playwright/test"
import { apiBaseUrl, firstSuperuser, firstSuperuserPassword } from "./config.ts"

const jobsFixtureEnabled = process.env.PLAYWRIGHT_JOBS_FIXTURE === "1"
const jobsScenario = process.env.TXT2CRS_BROWSER_SCENARIO ?? "complete"
const learnerEmail = process.env.PLAYWRIGHT_TEST_USER_EMAIL ?? firstSuperuser
const learnerPassword =
  process.env.PLAYWRIGHT_TEST_USER_PASSWORD ?? firstSuperuserPassword

async function signOutForPublicRoute(page: Page) {
  // The public root performs no authenticated queries, so it is the safest
  // same-origin page on which to clear the storage state inherited from the
  // shared authenticated setup. Visiting `/login` first would intentionally
  // redirect a signed-in learner to `/create` and start a current-user request.
  await page.goto("/")
  await page.evaluate(() => {
    sessionStorage.clear()
    localStorage.clear()
  })
}

type ContrastAuditFailure = {
  text: string
  contrastRatio: number
  requiredRatio: number
}

/**
 * Audit the rendered text colors instead of comparing design-token strings.
 *
 * Browser-computed colors can be returned as OKLCH, so the canvas is used as a
 * standards-aware color parser. Backgrounds are composed from the document
 * root down to each text element so translucent surfaces are measured against
 * the color a learner actually sees.
 */
async function auditVisibleTextContrast(
  page: Page,
): Promise<ContrastAuditFailure[]> {
  return page.evaluate(() => {
    type RgbaColor = {
      red: number
      green: number
      blue: number
      alpha: number
    }

    const canvas = document.createElement("canvas")
    canvas.width = 1
    canvas.height = 1
    const canvasContext = canvas.getContext("2d", {
      willReadFrequently: true,
    })
    if (canvasContext === null) {
      throw new Error("The browser could not create a color parsing canvas.")
    }

    const parseColor = (cssColor: string): RgbaColor => {
      canvasContext.clearRect(0, 0, 1, 1)
      canvasContext.fillStyle = "rgba(0, 0, 0, 0)"
      canvasContext.fillStyle = cssColor
      canvasContext.fillRect(0, 0, 1, 1)
      const [red, green, blue, alpha] = canvasContext.getImageData(
        0,
        0,
        1,
        1,
      ).data
      return { red, green, blue, alpha: alpha / 255 }
    }

    const compositeColor = (
      foregroundColor: RgbaColor,
      backgroundColor: RgbaColor,
    ): RgbaColor => {
      const composedAlpha =
        foregroundColor.alpha +
        backgroundColor.alpha * (1 - foregroundColor.alpha)
      if (composedAlpha === 0) {
        return { red: 0, green: 0, blue: 0, alpha: 0 }
      }
      return {
        red:
          (foregroundColor.red * foregroundColor.alpha +
            backgroundColor.red *
              backgroundColor.alpha *
              (1 - foregroundColor.alpha)) /
          composedAlpha,
        green:
          (foregroundColor.green * foregroundColor.alpha +
            backgroundColor.green *
              backgroundColor.alpha *
              (1 - foregroundColor.alpha)) /
          composedAlpha,
        blue:
          (foregroundColor.blue * foregroundColor.alpha +
            backgroundColor.blue *
              backgroundColor.alpha *
              (1 - foregroundColor.alpha)) /
          composedAlpha,
        alpha: composedAlpha,
      }
    }

    const relativeLuminance = (color: RgbaColor): number => {
      const linearizeChannel = (channel: number): number => {
        const normalizedChannel = channel / 255
        return normalizedChannel <= 0.04045
          ? normalizedChannel / 12.92
          : ((normalizedChannel + 0.055) / 1.055) ** 2.4
      }
      return (
        0.2126 * linearizeChannel(color.red) +
        0.7152 * linearizeChannel(color.green) +
        0.0722 * linearizeChannel(color.blue)
      )
    }

    const contrastRatio = (
      firstColor: RgbaColor,
      secondColor: RgbaColor,
    ): number => {
      const firstLuminance = relativeLuminance(firstColor)
      const secondLuminance = relativeLuminance(secondColor)
      const lighterLuminance = Math.max(firstLuminance, secondLuminance)
      const darkerLuminance = Math.min(firstLuminance, secondLuminance)
      return (lighterLuminance + 0.05) / (darkerLuminance + 0.05)
    }

    const textElements = new Set<HTMLElement>()
    const textNodeWalker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
    )
    while (textNodeWalker.nextNode()) {
      const textNode = textNodeWalker.currentNode as Text
      if (textNode.nodeValue?.trim()) {
        const parentElement = textNode.parentElement
        if (parentElement !== null) {
          textElements.add(parentElement)
        }
      }
    }

    const failures: ContrastAuditFailure[] = []
    for (const textElement of textElements) {
      const elementStyle = getComputedStyle(textElement)
      const elementBounds = textElement.getBoundingClientRect()
      const isScreenReaderOnly =
        elementStyle.position === "absolute" &&
        elementBounds.width <= 1 &&
        elementBounds.height <= 1 &&
        elementStyle.overflow === "hidden"
      if (
        elementBounds.width === 0 ||
        elementBounds.height === 0 ||
        elementStyle.display === "none" ||
        elementStyle.visibility === "hidden" ||
        isScreenReaderOnly
      ) {
        continue
      }

      // CSS backgrounds do not inherit. Compose every ancestor surface in
      // paint order to determine the opaque color beneath this text node.
      const ancestors: HTMLElement[] = []
      let currentElement: HTMLElement | null = textElement
      while (currentElement !== null) {
        ancestors.unshift(currentElement)
        currentElement = currentElement.parentElement
      }
      let backgroundColor = parseColor("white")
      for (const ancestor of ancestors) {
        backgroundColor = compositeColor(
          parseColor(getComputedStyle(ancestor).backgroundColor),
          backgroundColor,
        )
      }

      const renderedTextColor = compositeColor(
        parseColor(elementStyle.color),
        backgroundColor,
      )
      const measuredRatio = contrastRatio(renderedTextColor, backgroundColor)
      const fontSize = Number.parseFloat(elementStyle.fontSize)
      const fontWeight = Number.parseInt(elementStyle.fontWeight, 10)
      const isLargeText =
        fontSize >= 24 || (fontSize >= 18.66 && fontWeight >= 700)
      const requiredRatio = isLargeText ? 3 : 4.5
      if (measuredRatio + 0.01 < requiredRatio) {
        failures.push({
          text: textElement.textContent?.trim().replace(/\s+/g, " ") ?? "",
          contrastRatio: Number(measuredRatio.toFixed(2)),
          requiredRatio,
        })
      }
    }

    return failures
  })
}

const interceptedProblem = {
  type: "about:blank",
  title: "Course request not accepted",
  status: 422,
  detail: "The intercepted browser contract request was inspected.",
  code: "JOB_7002",
  trace_id: "browser-contract-trace",
}

async function inspectRejectedSubmission(
  page: Page,
  endpointPath: "/api/v1/jobs" | "/api/v1/jobs/upload",
) {
  const responsePromise = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      new URL(response.url()).pathname === endpointPath,
  )
  await page.getByRole("button", { name: "Create my learning package" }).click()
  const response = await responsePromise
  expect(response.status()).toBe(422)
  return response.request()
}

test.describe("public learner landing", () => {
  test("explains the one-to-four transformation without product diagnostics", async ({
    page,
  }) => {
    await signOutForPublicRoute(page)
    await page.goto("/")

    await expect(
      page.getByRole("heading", {
        name: "Turn one source into a complete learning package",
      }),
    ).toBeVisible()
    await expect(
      page.getByRole("heading", { name: "Deep-researched course" }),
    ).toBeVisible()
    await expect(
      page.getByRole("heading", { name: "Review materials" }),
    ).toBeVisible()
    await expect(
      page.getByRole("heading", { name: "Student assessment" }),
    ).toBeVisible()
    await expect(
      page.getByRole("heading", { name: "Instructor answer key" }),
    ).toBeVisible()
    await expect(
      page.getByRole("link", { name: "Sign in to create a course" }),
    ).toBeVisible()
    await expect(
      page.getByText(/route owner|shell ready|runtime/i),
    ).toHaveCount(0)
  })

  test("preserves one bounded topic through sign in and consumes it on creation", async ({
    page,
  }) => {
    await signOutForPublicRoute(page)
    await page.getByLabel("Draft a course topic").fill("Teach tidal ecology.")
    await page
      .getByRole("button", { name: "Save topic and continue to sign in" })
      .click()

    await expect(page).toHaveURL("/login")
    await expect(
      page.getByText("Your saved course topic will be ready after sign in."),
    ).toBeVisible()
    await page.getByTestId("email-input").fill(learnerEmail)
    await page.getByTestId("password-input").fill(learnerPassword)
    await page.getByRole("button", { name: "Sign In" }).click()

    await expect(page).toHaveURL("/create")
    await expect(page.getByLabel("What should the course teach?")).toHaveValue(
      "Teach tidal ecology.",
    )
    await page.reload()
    await expect(page.getByLabel("What should the course teach?")).toHaveValue(
      "",
    )
  })

  test("fits a maximum draft and primary action at the 320px minimum", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 320, height: 720 })
    await signOutForPublicRoute(page)
    await page.getByLabel("Draft a course topic").fill("W".repeat(10_000))

    const handoffAction = page.getByRole("button", {
      name: "Save topic and continue to sign in",
    })
    const actionBox = await handoffAction.boundingBox()
    expect(actionBox?.height ?? 0).toBeGreaterThanOrEqual(44)
    expect(
      await page.evaluate(
        () =>
          document.documentElement.scrollWidth -
          document.documentElement.clientWidth,
      ),
    ).toBeLessThanOrEqual(0)
  })

  test("meets WCAG AA text contrast in light and dark themes", async ({
    page,
  }) => {
    await signOutForPublicRoute(page)

    for (const theme of ["light", "dark"] as const) {
      await page.evaluate((selectedTheme) => {
        localStorage.setItem("vite-ui-theme", selectedTheme)
      }, theme)
      await page.reload()
      await expect(page.locator("html")).toHaveClass(new RegExp(theme))
      await expect(
        page.getByRole("heading", {
          name: "Turn one source into a complete learning package",
        }),
      ).toBeVisible()

      const contrastFailures = await auditVisibleTextContrast(page)
      expect(contrastFailures, `${theme} theme contrast failures`).toEqual([])
    }
  })
})

test.describe("authenticated course intake", () => {
  test.skip(!jobsFixtureEnabled, "Requires the deterministic browser server.")

  test("switches source modes without retaining inactive source controls", async ({
    page,
  }) => {
    await page.goto("/create")

    await page.getByRole("tab", { name: "Pasted text" }).click()
    const pastedText = page.getByLabel("Paste the source text")
    await pastedText.fill("A bounded source preview for the learning studio.")
    await expect(
      page.getByRole("region", { name: "Source preview" }),
    ).toContainText("A bounded source preview")

    await page.getByRole("tab", { name: "Website" }).click()
    await expect(pastedText).toHaveCount(0)
    await expect(page.getByLabel("Source URL")).toHaveValue("")

    await page.getByRole("tab", { name: "Document" }).click()
    const sourceFile = page.getByLabel("Course source file")
    await sourceFile.setInputFiles({
      name: "course-source.pdf",
      mimeType: "application/pdf",
      buffer: Buffer.from("%PDF-1.7 private local preview fixture"),
    })
    const sourcePreview = page.getByRole("region", { name: "Source preview" })
    await expect(sourcePreview).toContainText("course-source.pdf")
    await expect(sourcePreview).toContainText("application/pdf")
    await expect(sourcePreview).not.toContainText("%PDF-1.7")
    await page.getByRole("button", { name: "Remove selected source" }).click()
    await expect(sourceFile).toHaveValue("")
  })

  test("supports bounded learning goals with keyboard focus recovery", async ({
    page,
  }) => {
    await page.goto("/create")

    await expect(page.getByLabel("Learning goal 1")).toBeVisible()
    await page.getByRole("button", { name: "Add learning goal" }).click()
    await expect(page.getByLabel("Learning goal 2")).toBeFocused()
    await page
      .getByLabel("Learning goal 2")
      .fill("Compare two examples from the source.")
    await page.getByRole("button", { name: "Remove goal 2" }).click()
    await expect(page.getByLabel("Learning goal 1")).toBeFocused()
    await expect(page.getByLabel("Adult learner")).toBeVisible()
    await expect(
      page.getByLabel("Allow AI and research processing"),
    ).not.toBeChecked()
  })

  test("submits one prompt and survives direct progress refresh", async ({
    page,
  }) => {
    test.skip(
      jobsScenario === "failed",
      "The failed scenario owns its terminal submission story below.",
    )

    await page.goto("/create")

    await page.getByRole("tab", { name: "Topic" }).click()
    await page
      .getByLabel("What should the course teach?")
      .fill("Teach Python variables.")
    await page
      .getByLabel("Learning goal 1")
      .fill("Explain and use Python variables.")
    await page.getByLabel("Adult learner").check()
    await page.getByLabel("Allow AI and research processing").check()

    const createCourse = page.getByRole("button", {
      name: "Create my learning package",
    })
    await createCourse.dblclick()

    await expect(page).toHaveURL(/\/jobs\/[A-Za-z0-9._:-]+$/)
    await expect(
      page.getByRole("heading", {
        name: /Building your learning package|Course materials are ready/,
      }),
    ).toBeVisible()
    const jobUrl = page.url()

    await page.reload()
    await expect(page).toHaveURL(jobUrl)
    await expect(
      page.getByRole("heading", {
        level: 2,
        name: /queued securely|course materials are ready/i,
      }),
    ).toBeVisible()
  })

  test("keeps upload metadata visible without parsing document content", async ({
    page,
  }) => {
    await page.goto("/create")
    await page.getByRole("tab", { name: "Document" }).click()
    await page.getByLabel("Course source file").setInputFiles({
      name: "marine-biology.pdf",
      mimeType: "application/pdf",
      buffer: Buffer.from("%PDF-1.7 test fixture"),
    })

    await expect(page.getByText("marine-biology.pdf")).toBeVisible()
    await expect(page.getByText("application/pdf")).toBeVisible()
    await expect(page.getByText("%PDF-1.7")).toHaveCount(0)
  })

  test("builds the generated request shape for all seven source families", async ({
    page,
  }) => {
    // The real deterministic journey above proves durable prompt execution.
    // These two interceptors stop only the inspected submission at the
    // browser boundary, allowing every other protected query to use the real
    // test server without creating six irrelevant jobs.
    await page.route("**/api/v1/jobs", async (route) => {
      await route.fulfill({
        status: 422,
        contentType: "application/problem+json",
        json: interceptedProblem,
      })
    })
    await page.route("**/api/v1/jobs/upload", async (route) => {
      await route.fulfill({
        status: 422,
        contentType: "application/problem+json",
        json: interceptedProblem,
      })
    })

    const jsonSources = [
      {
        tab: "Topic",
        label: "What should the course teach?",
        inputType: "prompt",
        value: "Teach the foundations of wetland ecology.",
      },
      {
        tab: "Pasted text",
        label: "Paste the source text",
        inputType: "text",
        value: "Wetlands slow water flow and create diverse habitats.",
      },
      {
        tab: "Website",
        label: "Source URL",
        inputType: "url",
        value: "https://example.org/wetland-ecology",
      },
      {
        tab: "YouTube",
        label: "YouTube URL",
        inputType: "youtube",
        value: "https://www.youtube.com/watch?v=wetlands101",
      },
    ] as const

    for (const source of jsonSources) {
      await page.goto("/create")
      await page.getByRole("tab", { name: source.tab }).click()
      await page.getByLabel(source.label).fill(source.value)
      await page.getByLabel("Adult learner").check()
      await page.getByLabel("Allow AI and research processing").check()

      const request = await inspectRejectedSubmission(page, "/api/v1/jobs")
      expect(request.headers()["idempotency-key"]).toMatch(/^course-/)
      expect(request.postDataJSON()).toEqual({
        input: {
          type: source.inputType,
          value: source.value,
        },
        preferences: {
          level: "auto",
          audience: null,
          prior_knowledge: null,
          learning_goals: [],
          language: "auto",
        },
        consent_to_ai_processing: true,
        learner_age_group: "adult",
      })
    }

    const uploadSources = [
      {
        fileName: "wetlands.pdf",
        mediaType: "application/pdf",
      },
      {
        fileName: "wetlands.docx",
        mediaType:
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      },
      {
        fileName: "wetlands.pptx",
        mediaType:
          "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      },
    ] as const

    for (const source of uploadSources) {
      await page.goto("/create")
      await page.getByRole("tab", { name: "Document" }).click()
      await page.getByLabel("Course source file").setInputFiles({
        name: source.fileName,
        mimeType: source.mediaType,
        buffer: Buffer.from("browser contract fixture"),
      })
      await page.getByLabel("Adult learner").check()
      await page.getByLabel("Allow AI and research processing").check()

      const request = await inspectRejectedSubmission(
        page,
        "/api/v1/jobs/upload",
      )
      const multipartBody = request.postDataBuffer()?.toString("utf8") ?? ""
      expect(request.headers()["idempotency-key"]).toMatch(/^course-/)
      expect(request.headers()["content-type"]).toContain(
        "multipart/form-data; boundary=",
      )
      expect(multipartBody.match(/name="metadata"/g)).toHaveLength(1)
      expect(multipartBody.match(/name="file"/g)).toHaveLength(1)
      expect(multipartBody).toContain(`filename="${source.fileName}"`)
      expect(multipartBody).toContain(`Content-Type: ${source.mediaType}`)
      expect(multipartBody).toContain('"consent_to_ai_processing":true')
      expect(multipartBody).toContain('"learner_age_group":"adult"')
      expect(multipartBody).not.toContain("sourceValue")
    }
  })

  test("renders bounded extraction notes and visible reconnection state", async ({
    context,
    page,
  }) => {
    const warningJobId = "job-browser-warning"
    await page.route(`**/api/v1/jobs/${warningJobId}`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        json: {
          schema_version: "1.0",
          job_id: warningJobId,
          status: "researching",
          revision: 3,
          created_at: "2026-07-20T00:00:00Z",
          updated_at: "2026-07-20T00:01:00Z",
          progress: {
            stage: "researching",
            message: "Researching the accepted source.",
            completed_units: 1,
            total_units: null,
          },
          input: {
            type: "document",
            display_name: "wetlands.docx",
            size_bytes: 2048,
            extraction_warnings: [
              "One embedded chart could not be read.",
              "Speaker notes were not included.",
            ],
            warnings_truncated: false,
          },
          failure: null,
          result: null,
          artifacts: {
            available: false,
            count: 0,
            manifest_url: null,
          },
        },
      })
    })

    await page.goto(`/jobs/${warningJobId}`)
    await expect(
      page.getByRole("heading", { name: "Building your learning package" }),
    ).toBeVisible()
    await expect(page.getByText("Source extraction notes")).toBeVisible()
    await expect(
      page.getByText("One embedded chart could not be read."),
    ).toBeVisible()

    await context.setOffline(true)
    await expect(page.getByText("Reconnecting", { exact: true })).toBeVisible()
    await expect(
      page.getByText(
        "Showing the last confirmed course update while the connection returns.",
      ),
    ).toBeVisible()
    await context.setOffline(false)
  })

  test("renders a generated cancellation without inventing completed stages", async ({
    page,
  }) => {
    const cancelledJobId = "job-browser-cancelled"
    await page.route(`**/api/v1/jobs/${cancelledJobId}`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        json: {
          schema_version: "1.0",
          job_id: cancelledJobId,
          status: "cancelled",
          revision: 4,
          created_at: "2026-07-20T00:00:00Z",
          updated_at: "2026-07-20T00:02:00Z",
          progress: {
            stage: "cancelled",
            message: "Course generation was cancelled.",
            completed_units: 1,
            total_units: null,
          },
          input: {
            type: "prompt",
            display_name: "Course prompt",
            size_bytes: 48,
            extraction_warnings: [],
            warnings_truncated: false,
          },
          failure: null,
          result: null,
          artifacts: {
            available: false,
            count: 0,
            manifest_url: null,
          },
        },
      })
    })

    await page.goto(`/jobs/${cancelledJobId}`)
    await expect(
      page.getByRole("heading", { name: "Course generation cancelled" }),
    ).toBeVisible()
    await expect(
      page.getByRole("link", { name: "Create another course" }),
    ).toBeVisible()
    await expect(page.getByText("Completed")).toHaveCount(0)
  })

  test("fits mobile and retains keyboard-visible primary actions", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await page.goto("/create")

    await expect(
      page.getByRole("heading", { name: "Create a course" }),
    ).toBeVisible()
    const createCourse = page.getByRole("button", {
      name: "Create my learning package",
    })
    const box = await createCourse.boundingBox()
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44)
    expect(
      await page.evaluate(
        () =>
          document.documentElement.scrollWidth -
          document.documentElement.clientWidth,
      ),
    ).toBeLessThanOrEqual(0)
  })

  test("uses one recovery state for missing and foreign-owned jobs", async ({
    page,
    request,
  }) => {
    const password = "Browser-only-123!"
    const foreignOwnerEmail = `foreign-${Date.now()}@example.com`
    const foreignSignup = await request.post(
      `${apiBaseUrl}/api/v1/users/signup`,
      {
        data: {
          email: foreignOwnerEmail,
          password,
          full_name: "Foreign Browser Owner",
        },
      },
    )
    expect(foreignSignup.status()).toBe(201)
    const foreignLogin = await request.post(
      `${apiBaseUrl}/api/v1/login/access-token`,
      {
        form: { username: foreignOwnerEmail, password },
      },
    )
    expect(foreignLogin.ok()).toBe(true)
    const foreignToken = (await foreignLogin.json()) as { access_token: string }
    try {
      const foreignSubmission = await request.post(
        `${apiBaseUrl}/api/v1/jobs`,
        {
          headers: {
            Authorization: `Bearer ${foreignToken.access_token}`,
            "Idempotency-Key": `foreign-${Date.now()}`,
          },
          data: {
            input: { type: "prompt", value: "Teach Python variables." },
            preferences: {
              level: "auto",
              audience: null,
              prior_knowledge: null,
              learning_goals: [],
              language: "auto",
            },
            consent_to_ai_processing: true,
            learner_age_group: "adult",
          },
        },
      )
      expect(foreignSubmission.status()).toBe(202)
      const foreignJob = (await foreignSubmission.json()) as { job_id: string }

      const unavailableHeading = page.getByRole("heading", {
        name: "Course job not available",
      })
      const unavailableCopy = page.getByText(
        "This course job could not be opened. It may not exist or may not belong to this account.",
      )
      await page.goto(`/jobs/${foreignJob.job_id}`)
      await expect(unavailableHeading).toBeVisible()
      await expect(unavailableCopy).toBeVisible()

      await page.goto("/jobs/missing-course-job")
      await expect(unavailableHeading).toBeVisible()
      await expect(unavailableCopy).toBeVisible()
    } finally {
      const deleteForeignOwner = await request.delete(
        `${apiBaseUrl}/api/v1/users/me`,
        {
          headers: {
            Authorization: `Bearer ${foreignToken.access_token}`,
          },
        },
      )
      expect(deleteForeignOwner.status()).toBe(200)
    }
  })
})

test.describe("safe terminal job states", () => {
  test.skip(
    !jobsFixtureEnabled || jobsScenario !== "failed",
    "Requires the deterministic failed-job scenario.",
  )

  test("renders a server-safe failure with a creation recovery path", async ({
    page,
  }) => {
    await page.goto("/create")
    await page
      .getByLabel("What should the course teach?")
      .fill("Teach a deterministic failing course.")
    await page.getByLabel("Adult learner").check()
    await page.getByLabel("Allow AI and research processing").check()
    await page
      .getByRole("button", { name: "Create my learning package" })
      .click()

    await expect(
      page.getByRole("heading", { name: "Course generation stopped" }),
    ).toBeVisible()
    await expect(
      page.getByRole("link", { name: "Create another course" }),
    ).toBeVisible()
    await expect(page.getByText(/traceback|provider|filesystem/i)).toHaveCount(
      0,
    )
  })
})
