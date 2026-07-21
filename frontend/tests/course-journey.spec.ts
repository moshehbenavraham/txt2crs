import { expect, type Page, test } from "@playwright/test"
import type {
  ArtifactDeliverable,
  ArtifactFormat,
  ArtifactManifestPublic,
} from "../src/client"
import {
  ARTIFACT_FORMAT_LABELS,
  formatArtifactByteSize,
} from "../src/components/CourseResults/presentation"
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
  rootSelector: string | null = null,
): Promise<ContrastAuditFailure[]> {
  return page.evaluate((selectedRoot) => {
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
    const auditRoot =
      selectedRoot === null
        ? document.body
        : document.querySelector<HTMLElement>(selectedRoot)
    if (auditRoot === null) {
      throw new Error("The requested contrast-audit root does not exist.")
    }
    const textNodeWalker = document.createTreeWalker(
      auditRoot,
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
  }, rootSelector)
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

  test("keeps the topic handoff action visible at a common laptop fold", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 1265, height: 708 })
    await signOutForPublicRoute(page)

    const handoffAction = page.getByRole("button", {
      name: "Save topic and continue to sign in",
    })
    const actionBox = await handoffAction.boundingBox()

    expect(actionBox).not.toBeNull()
    expect(
      (actionBox?.y ?? 708) + (actionBox?.height ?? 0),
    ).toBeLessThanOrEqual(708)
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
    const artifactManifestResponse = page.waitForResponse((response) => {
      const responseUrl = new URL(response.url())
      return (
        response.request().method() === "GET" &&
        /\/api\/v1\/jobs\/[^/]+\/artifacts$/.test(responseUrl.pathname) &&
        response.status() === 200
      )
    })
    await createCourse.dblclick()

    await expect(page).toHaveURL(/\/jobs\/[A-Za-z0-9._:-]+$/)
    await expect(
      page.getByRole("heading", {
        name: /Building your learning package|Course materials are ready/,
      }),
    ).toBeVisible({ timeout: 12_000 })
    const jobUrl = page.url()

    await page.reload()
    await expect(page).toHaveURL(jobUrl)
    await expect(
      page.getByRole("heading", {
        level: 2,
        name: /queued securely|course materials are ready/i,
      }),
    ).toBeVisible({ timeout: 12_000 })

    await expect(
      page.getByRole("heading", {
        name: "Course materials are ready",
        exact: true,
      }),
    ).toBeVisible({ timeout: 15_000 })
    const publicationWorkspace = page.getByRole("region", {
      name: "Learning package publications",
    })
    await expect(publicationWorkspace).toBeVisible()
    const publicationNames = [
      "Course",
      "Review pack",
      "Assessment",
      "Instructor answer key",
    ] as const
    const manifest = (await (
      await artifactManifestResponse
    ).json()) as ArtifactManifestPublic
    expect(manifest.deliverables).toHaveLength(4)
    const manifestArtifacts = manifest.deliverables.flatMap(
      ({ artifacts }) => artifacts,
    )
    expect(manifestArtifacts).toHaveLength(16)
    expect(manifest.deliverables.map(({ deliverable }) => deliverable)).toEqual(
      ["course", "review_pack", "assessment", "answer_key"],
    )
    for (const artifact of manifestArtifacts) {
      expect(artifact.file_name).not.toMatch(/[\\/]/)
      expect(
        [...artifact.file_name].some((character) => {
          const characterCode = character.charCodeAt(0)
          return (
            characterCode < 32 || (characterCode >= 127 && characterCode <= 159)
          )
        }),
      ).toBe(false)
      expect(Number.isSafeInteger(artifact.size_bytes)).toBe(true)
      expect(artifact.size_bytes).toBeGreaterThan(0)
    }
    expect(
      await publicationWorkspace
        .getByRole("article")
        .evaluateAll((articles) =>
          articles.map((article) => article.getAttribute("data-deliverable")),
        ),
    ).toEqual(["course", "review_pack", "assessment", "answer_key"])

    for (const publicationName of publicationNames) {
      const publication = page.getByRole("article", {
        name: publicationName,
      })
      await expect(publication).toBeVisible()
      await expect(publication).toContainText("4 formats")
    }

    const answerKey = page.getByRole("article", {
      name: "Instructor answer key",
    })
    const answerKeyToggle = answerKey.getByRole("button", {
      name: "Show answer key downloads",
    })
    const answerKeyFormats = answerKey.locator(
      'ul[aria-label="Instructor answer key formats"]',
    )
    await expect(answerKeyToggle).toHaveAttribute("aria-expanded", "false")
    await expect(answerKeyFormats).toBeHidden()
    await answerKeyToggle.focus()
    await page.keyboard.press("Enter")
    await expect(
      answerKey.getByRole("button", { name: "Hide answer key downloads" }),
    ).toHaveAttribute("aria-expanded", "true")
    await expect(answerKeyFormats).toBeVisible()
    await expect(answerKeyFormats.getByRole("listitem")).toHaveCount(4)

    const publicationNameByDeliverable: Record<
      ArtifactDeliverable,
      (typeof publicationNames)[number]
    > = {
      course: "Course",
      review_pack: "Review pack",
      assessment: "Assessment",
      answer_key: "Instructor answer key",
    }
    const expectedFormatOrder: ArtifactFormat[] = [
      "html",
      "markdown",
      "pdf",
      "docx",
    ]
    for (const deliverable of manifest.deliverables) {
      const publication = page.getByRole("article", {
        name: publicationNameByDeliverable[deliverable.deliverable],
      })
      const formatList = publication.getByRole("list", {
        name: `${publicationNameByDeliverable[deliverable.deliverable]} formats`,
      })
      const formatListItems = formatList.getByRole("listitem")
      await expect(formatListItems).toHaveCount(4)
      expect(deliverable.artifacts.map(({ format }) => format).sort()).toEqual(
        [...expectedFormatOrder].sort(),
      )
      for (const [formatIndex, format] of expectedFormatOrder.entries()) {
        await expect(formatListItems.nth(formatIndex)).toContainText(
          ARTIFACT_FORMAT_LABELS[format],
        )
      }
      for (const artifact of deliverable.artifacts) {
        const formatListItem = formatListItems.filter({
          hasText: ARTIFACT_FORMAT_LABELS[artifact.format],
        })
        await expect(formatListItem).toContainText(
          formatArtifactByteSize(artifact.size_bytes),
        )
      }
    }
    await answerKey
      .getByRole("button", { name: "Hide answer key downloads" })
      .click()

    const coursePublication = page.getByRole("article", { name: "Course" })
    const courseFormats = coursePublication.getByRole("button", {
      name: "Course download formats",
    })
    await courseFormats.focus()
    await page.keyboard.press("Enter")
    const formatMenu = page.getByRole("menu")
    await expect(formatMenu.getByText("Download format")).toBeVisible()
    await expect(formatMenu.getByRole("menuitem")).toHaveCount(4)
    await expect(
      formatMenu.getByRole("menuitem", { name: /^HTML / }),
    ).toBeVisible()
    await expect(
      formatMenu.getByRole("menuitem", { name: /^Markdown / }),
    ).toBeVisible()
    await expect(
      formatMenu.getByRole("menuitem", { name: /^PDF / }),
    ).toBeVisible()
    await expect(
      formatMenu.getByRole("menuitem", { name: /^DOCX / }),
    ).toBeVisible()
    await expect
      .poll(
        () =>
          formatMenu
            .getByRole("menuitem")
            .evaluateAll((menuItems) =>
              menuItems
                .filter(
                  (menuItem) => menuItem.getBoundingClientRect().height < 44,
                )
                .map((menuItem) => menuItem.textContent?.trim() ?? ""),
            ),
        { message: "format-menu target-size failures" },
      )
      .toEqual([])
    await page.keyboard.press("Escape")
    await expect(courseFormats).toBeFocused()

    const pdfDownload = coursePublication.getByRole("button", {
      name: "Download Course PDF",
    })
    const downloadPromise = page.waitForEvent("download")
    await pdfDownload.click()
    const download = await downloadPromise
    expect(download.suggestedFilename()).toBe("python-basics-course.pdf")
    const downloadedFilePath = await download.path()
    expect(downloadedFilePath).not.toBeNull()
    expect(
      (await import("node:fs")).statSync(downloadedFilePath as string).size,
    ).toBeGreaterThan(0)

    const previewTrigger = coursePublication.getByRole("button", {
      name: "Preview Course HTML",
    })
    const previewConsoleIssues: string[] = []
    const previewPageErrors: string[] = []
    const previewNetworkEscapes: string[] = []
    page.on("console", (message) => {
      if (message.type() === "warning" || message.type() === "error") {
        previewConsoleIssues.push(message.text())
      }
    })
    page.on("pageerror", (error) => {
      previewPageErrors.push(error.message)
    })
    page.on("request", (request) => {
      if (request.url().startsWith("https://preview-escape.invalid/")) {
        previewNetworkEscapes.push(request.url())
      }
    })
    await previewTrigger.click()
    const previewDialog = page.getByRole("dialog", {
      name: "Course HTML preview",
    })
    await expect(previewDialog).toBeVisible()
    const previewCloseButton = previewDialog.getByRole("button", {
      name: "Close",
    })
    await expect
      .poll(
        () =>
          previewCloseButton.evaluate(
            (button) => button.getBoundingClientRect().height,
          ),
        { message: "preview close target size" },
      )
      .toBeGreaterThanOrEqual(44)
    const previewFrame = previewDialog.locator("iframe")
    await expect(previewFrame).toHaveAttribute("sandbox", "")
    await expect(previewFrame).toHaveAttribute("referrerpolicy", "no-referrer")
    await expect(previewFrame).toHaveAttribute("title", "Course HTML preview")
    await expect(previewFrame).not.toHaveAttribute("src", /.+/)
    await expect(previewFrame).toHaveAttribute("srcdoc", /Python Basics/)
    const securedPreviewDocument = page.frameLocator(
      'iframe[title="Course HTML preview"]',
    )
    await expect(
      securedPreviewDocument.getByRole("heading", { name: "Python Basics" }),
    ).toBeVisible()
    await expect(
      securedPreviewDocument.locator("script, iframe, form, object, embed"),
    ).toHaveCount(0)
    await expect(
      securedPreviewDocument.locator(
        'meta[http-equiv="Content-Security-Policy"]',
      ),
    ).toHaveAttribute("content", /default-src 'none'/)
    await page.keyboard.press("Escape")
    await expect(previewTrigger).toBeFocused()

    const courseHtmlArtifact = manifest.deliverables
      .find(({ deliverable }) => deliverable === "course")
      ?.artifacts.find(({ format }) => format === "html")
    if (courseHtmlArtifact === undefined) {
      throw new Error("The deterministic course HTML artifact is required.")
    }
    const hostilePreviewPrefix = [
      "<!doctype html><html><head>",
      '<style>@import url("https://preview-escape.invalid/style.css");</style>',
      "</head><body>",
      "<main><h1>Hostile preview marker</h1>",
      '<a href="https://preview-escape.invalid/navigation">Leave</a>',
      '<img src="https://preview-escape.invalid/tracker.png">',
      '<form action="https://preview-escape.invalid/form"><input autofocus></form>',
      '<iframe src="https://preview-escape.invalid/frame"></iframe>',
      '<script>parent.document.body.dataset.previewInjected = "true"</script>',
      "</main></body></html>",
    ].join("")
    const hostilePreviewByteLength = Buffer.byteLength(hostilePreviewPrefix)
    expect(hostilePreviewByteLength).toBeLessThan(courseHtmlArtifact.size_bytes)
    const hostilePreviewBody =
      hostilePreviewPrefix +
      " ".repeat(courseHtmlArtifact.size_bytes - hostilePreviewByteLength)
    await page.route(
      `**/api/v1/jobs/${manifest.job_id}/artifacts/${courseHtmlArtifact.artifact_id}`,
      async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "text/html",
          body: hostilePreviewBody,
        })
      },
    )

    await previewTrigger.click()
    await expect(previewDialog).toBeVisible()
    const hostilePreviewDocument = page.frameLocator(
      'iframe[title="Course HTML preview"]',
    )
    await expect(
      hostilePreviewDocument.getByRole("heading", {
        name: "Hostile preview marker",
      }),
    ).toBeVisible()
    await expect(
      hostilePreviewDocument.locator(
        "script, iframe, form, input, style, a[href], img[src]",
      ),
    ).toHaveCount(0)
    await expect(page.getByText("Hostile preview marker")).toHaveCount(0)
    expect(
      await page.evaluate(() => document.body.dataset.previewInjected ?? null),
    ).toBeNull()
    expect(previewNetworkEscapes).toEqual([])
    expect(previewPageErrors).toEqual([])
    expect(previewConsoleIssues).toEqual([])
    await page.keyboard.press("Escape")

    await expect(
      page.getByRole("heading", { name: "Sources and research notes" }),
    ).toBeVisible()
    await expect(
      page.getByRole("link", { name: "The Python Tutorial" }),
    ).toHaveAttribute("rel", /noopener/)

    const renderedQaMatrix = [
      { width: 320, height: 568, expectedRows: 4 },
      { width: 375, height: 812, expectedRows: 4 },
      { width: 768, height: 900, expectedRows: 2 },
      { width: 1280, height: 577, expectedRows: 1 },
      { width: 1440, height: 900, expectedRows: 1 },
    ] as const
    const screenshotDirectory =
      process.env.RESULTS_QA_SCREENSHOT_DIRECTORY?.replace(/\/$/, "")

    for (const theme of ["light", "dark"] as const) {
      await page.evaluate((selectedTheme) => {
        document.documentElement.classList.remove("light", "dark")
        document.documentElement.classList.add(selectedTheme)
        localStorage.setItem("vite-ui-theme", selectedTheme)
      }, theme)

      for (const viewport of renderedQaMatrix) {
        await page.setViewportSize(viewport)
        await expect(publicationWorkspace).toBeVisible()

        // Crossing the desktop navigation breakpoint deliberately animates the
        // shell's content inset. Let that bounded transition finish before
        // treating the card positions as the stable layout baseline.
        await page.waitForTimeout(300)
        const folioGeometry = await publicationWorkspace
          .getByRole("article")
          .evaluateAll((articles) =>
            articles.map((article) => {
              const bounds = article.getBoundingClientRect()
              return {
                x: Math.round(bounds.x),
                y: Math.round(bounds.y),
                width: Math.round(bounds.width),
              }
            }),
          )
        expect(
          new Set(folioGeometry.map(({ y }) => y)).size,
          `${theme} ${viewport.width}px result rows`,
        ).toBe(viewport.expectedRows)

        const targetSizeFailures = await publicationWorkspace
          .getByRole("button")
          .evaluateAll((buttons) =>
            buttons
              .filter((button) => {
                const bounds = button.getBoundingClientRect()
                return bounds.width > 0 && bounds.height > 0
              })
              .filter((button) => {
                const bounds = button.getBoundingClientRect()
                return bounds.height < 44
              })
              .map((button) => button.textContent?.trim() ?? ""),
          )
        expect(
          targetSizeFailures,
          `${theme} ${viewport.width}px target-size failures`,
        ).toEqual([])
        expect(
          await page.evaluate(
            () =>
              document.documentElement.scrollWidth -
              document.documentElement.clientWidth,
          ),
          `${theme} ${viewport.width}px horizontal overflow`,
        ).toBeLessThanOrEqual(0)
        if (viewport.width === 1280) {
          const answerKeyBounds = await answerKey.boundingBox()
          const answerKeyToggleBounds = await answerKeyToggle.boundingBox()
          expect(answerKeyBounds).not.toBeNull()
          expect(answerKeyToggleBounds).not.toBeNull()
          expect(answerKeyToggleBounds!.x).toBeGreaterThanOrEqual(
            answerKeyBounds!.x,
          )
          expect(
            answerKeyToggleBounds!.x + answerKeyToggleBounds!.width,
          ).toBeLessThanOrEqual(answerKeyBounds!.x + answerKeyBounds!.width)
        }
        expect(
          await auditVisibleTextContrast(
            page,
            'section[aria-labelledby="learning-package-publications"]',
          ),
          `${theme} ${viewport.width}px contrast failures`,
        ).toEqual([])

        await page.waitForTimeout(50)
        const settledFolioGeometry = await publicationWorkspace
          .getByRole("article")
          .evaluateAll((articles) =>
            articles.map((article) => {
              const bounds = article.getBoundingClientRect()
              return {
                x: Math.round(bounds.x),
                y: Math.round(bounds.y),
                width: Math.round(bounds.width),
              }
            }),
          )
        expect(
          settledFolioGeometry,
          `${theme} ${viewport.width}px stable folio geometry`,
        ).toEqual(folioGeometry)

        // Capture after the stability assertion. A full-page Playwright
        // screenshot temporarily adjusts the page viewport and can otherwise
        // look like a layout shift while the browser restores its dimensions.
        if (screenshotDirectory) {
          await page.screenshot({
            fullPage: true,
            path: `${screenshotDirectory}/results-${theme}-${viewport.width}.png`,
          })
        }
      }
    }

    await page.setViewportSize({ width: 320, height: 568 })
    const completionTitle = page.locator("#course-results h3")
    // Use the immutable source URL so the locator remains attached while its
    // text is intentionally replaced with a hostile long string.
    const sourceTitle = page.locator(
      'a[href="https://docs.python.org/3/tutorial/"] span',
    )
    const originalCompletionTitle = await completionTitle.textContent()
    const originalSourceTitle = await sourceTitle.textContent()
    const longUnbrokenTitle = "W".repeat(255)
    await completionTitle.evaluate((heading, replacementTitle) => {
      heading.textContent = replacementTitle
    }, longUnbrokenTitle)
    expect(
      await page.evaluate(
        () =>
          document.documentElement.scrollWidth -
          document.documentElement.clientWidth,
      ),
      "long result title overflow",
    ).toBeLessThanOrEqual(0)
    await completionTitle.evaluate((heading, replacementTitle) => {
      heading.textContent = replacementTitle
    }, originalCompletionTitle ?? "")

    await sourceTitle.evaluate((link, replacementTitle) => {
      link.textContent = replacementTitle
    }, longUnbrokenTitle)
    expect(
      await page.evaluate(
        () =>
          document.documentElement.scrollWidth -
          document.documentElement.clientWidth,
      ),
      "long source title overflow",
    ).toBeLessThanOrEqual(0)
    await sourceTitle.evaluate((link, replacementTitle) => {
      link.textContent = replacementTitle
    }, originalSourceTitle ?? "")

    // Browser zoom reduces the CSS viewport rather than multiplying rem
    // values. A 720px CSS viewport is therefore the layout-equivalent of the
    // 1440px desktop target viewed at 200% zoom.
    await page.setViewportSize({ width: 720, height: 450 })
    expect(
      await page.evaluate(
        () =>
          document.documentElement.scrollWidth -
          document.documentElement.clientWidth,
      ),
      "200% zoom-equivalent reflow overflow",
    ).toBeLessThanOrEqual(0)

    await page.emulateMedia({ reducedMotion: "reduce" })
    const reducedMotionDurationFailures = await publicationWorkspace.evaluate(
      (workspace) => {
        const parseDuration = (duration: string): number =>
          duration
            .split(",")
            .map((value) => value.trim())
            .reduce((maximumMilliseconds, value) => {
              const milliseconds = value.endsWith("ms")
                ? Number.parseFloat(value)
                : Number.parseFloat(value) * 1000
              return Math.max(maximumMilliseconds, milliseconds)
            }, 0)

        return [...workspace.querySelectorAll("*")]
          .map((element) => {
            const computedStyle = getComputedStyle(element)
            return {
              name:
                element.getAttribute("aria-label") ??
                element.textContent?.trim().slice(0, 40) ??
                element.tagName,
              animationMilliseconds: parseDuration(
                computedStyle.animationDuration,
              ),
              transitionMilliseconds: parseDuration(
                computedStyle.transitionDuration,
              ),
            }
          })
          .filter(
            ({ animationMilliseconds, transitionMilliseconds }) =>
              animationMilliseconds > 1 || transitionMilliseconds > 1,
          )
      },
    )
    expect(reducedMotionDurationFailures).toEqual([])
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

  test("shows live backend activity, elapsed time, and a recalculating completion estimate", async ({
    page,
  }) => {
    const progressJobId = "job-browser-live-progress"
    const createdAtMilliseconds = Date.now() - 80_000
    let statusReadCount = 0

    await page.route(`**/api/v1/jobs/${progressJobId}`, async (route) => {
      statusReadCount += 1
      const hasAdvanced = statusReadCount >= 2
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        json: {
          schema_version: "1.0",
          job_id: progressJobId,
          status: hasAdvanced ? "drafting" : "researching",
          revision: hasAdvanced ? 4 : 3,
          created_at: new Date(createdAtMilliseconds).toISOString(),
          updated_at: new Date(
            createdAtMilliseconds + (hasAdvanced ? 55_000 : 40_000),
          ).toISOString(),
          runtime_activity_at: new Date(
            createdAtMilliseconds + (hasAdvanced ? 75_000 : 60_000),
          ).toISOString(),
          progress: {
            stage: hasAdvanced ? "drafting" : "researching",
            message: hasAdvanced
              ? "Writing the course modules."
              : "Researching the course source.",
            completed_units: hasAdvanced ? 4 : 3,
            total_units: 12,
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

    await page.goto(`/jobs/${progressJobId}`)
    const liveProgress = page.getByRole("region", {
      name: "Live course progress",
    })
    await expect(liveProgress).toBeVisible()
    await expect(
      liveProgress.getByText("Elapsed", { exact: true }),
    ).toBeVisible()
    await expect(
      liveProgress.getByText("Estimated time left", { exact: true }),
    ).toBeVisible()
    await expect(liveProgress).toContainText("Confirmed update 3")

    const confirmedProgress = page.getByRole("progressbar", {
      name: "Confirmed course-building progress",
    })
    await expect(confirmedProgress).toHaveAttribute("aria-valuenow", "3")
    await expect(confirmedProgress).toHaveAttribute("aria-valuemax", "12")

    await expect(liveProgress).toContainText("Confirmed update 4", {
      timeout: 12_000,
    })
    await expect(
      page.getByRole("heading", { name: "Writing the course modules." }),
    ).toBeVisible()
    await expect(confirmedProgress).toHaveAttribute("aria-valuenow", "4")
    await expect(liveProgress.getByTestId("estimated-time-left")).toHaveText(
      "~1m 50s",
    )
    await expect(liveProgress.getByTestId("runtime-activity")).not.toHaveText(
      "Awaiting worker",
    )

    const elapsedTime = liveProgress.getByTestId("elapsed-time")
    const firstElapsedTime = await elapsedTime.textContent()
    await page.waitForTimeout(1_100)
    await expect(elapsedTime).not.toHaveText(firstElapsedTime ?? "")

    await page.setViewportSize({ width: 375, height: 812 })
    expect(
      await page.evaluate(
        () =>
          document.documentElement.scrollWidth -
          document.documentElement.clientWidth,
      ),
    ).toBeLessThanOrEqual(0)

    await page.emulateMedia({ reducedMotion: "reduce" })
    const progressFillTransitionDuration = await confirmedProgress
      .locator("div")
      .evaluate((progressFill) => ({
        reducedMotionMatches: window.matchMedia(
          "(prefers-reduced-motion: reduce)",
        ).matches,
        transitionDuration: getComputedStyle(progressFill).transitionDuration,
      }))
    expect(progressFillTransitionDuration.reducedMotionMatches).toBe(true)
    expect(
      Number.parseFloat(progressFillTransitionDuration.transitionDuration),
    ).toBeLessThanOrEqual(0.001)
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

  test("keeps unavailable publication indexes behind one safe retry state", async ({
    page,
  }) => {
    const completedJobId = "job-browser-publications-unavailable"
    let manifestReadCount = 0

    await page.route(`**/api/v1/jobs/${completedJobId}`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        json: {
          schema_version: "1.0",
          job_id: completedJobId,
          status: "completed",
          revision: 8,
          created_at: "2026-07-20T00:00:00Z",
          updated_at: "2026-07-20T00:04:00Z",
          progress: {
            stage: "ready",
            message: "Course materials are ready.",
            completed_units: 6,
            total_units: 6,
          },
          input: {
            type: "prompt",
            display_name: "Course prompt",
            size_bytes: 48,
            extraction_warnings: [],
            warnings_truncated: false,
          },
          failure: null,
          result: {
            title: "Private course",
            audience: "Adult learner",
            level: "beginner",
            language: "English",
            objective_count: 3,
            module_count: 2,
            sources: [],
            sources_truncated: false,
            conflicts: [],
            conflicts_truncated: false,
          },
          artifacts: {
            available: true,
            count: 16,
            manifest_url: `/api/v1/jobs/${completedJobId}/artifacts`,
          },
        },
      })
    })
    await page.route(
      `**/api/v1/jobs/${completedJobId}/artifacts`,
      async (route) => {
        manifestReadCount += 1
        await route.fulfill({
          status: 404,
          contentType: "application/problem+json",
          json: {
            type: "about:blank",
            title: "Not found",
            status: 404,
            detail: "private artifact storage path must never reach the page",
          },
        })
      },
    )

    await page.goto(`/jobs/${completedJobId}`)
    await expect(
      page.getByText("Publication files are not available"),
    ).toBeVisible()
    await expect(
      page.getByText("private artifact storage path", { exact: false }),
    ).toHaveCount(0)
    expect(manifestReadCount).toBe(1)

    await page.getByRole("button", { name: "Try again" }).click()
    await expect.poll(() => manifestReadCount).toBe(2)
    await expect(
      page.getByText("Publication files are not available"),
    ).toBeVisible()
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
