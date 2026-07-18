import { expect, type Page, test } from "@playwright/test"
import { createUser } from "./utils/privateApi"
import { randomEmail } from "./utils/random"
import { logInUser } from "./utils/user"

const strongPassword = () => `Apex!${Math.random().toString(36).slice(2, 12)}`

const documentOverflowX = (page: Page) =>
  page.evaluate(
    () =>
      document.documentElement.scrollWidth -
      document.documentElement.clientWidth,
  )

const createItemFromDialog = async (page: Page, title: string) => {
  await page.getByRole("button", { name: "Create item" }).first().click()
  const dialog = page.getByRole("dialog")
  await expect(dialog).toBeVisible()
  await dialog.getByLabel(/Title/).fill(title)
  await dialog.getByRole("button", { name: "Create item" }).click()
  await expect(dialog).not.toBeVisible()
}

// --- Populated state (superuser storage state) ---

test("Dashboard shows workspace identity, exact library status, preview, and administration", async ({
  page,
}) => {
  await page.goto("/")

  await expect(
    page.getByRole("heading", { name: "Workspace overview" }),
  ).toBeVisible()
  await expect(page.getByRole("link", { name: "Open library" })).toBeVisible()
  await expect(
    page.getByRole("button", { name: "Create item" }).first(),
  ).toBeVisible()

  // Guarantee a populated library, then verify the index sections
  await createItemFromDialog(page, `Dashboard QA ${Date.now()}`)

  await expect(
    page.getByRole("heading", { name: "Library status" }),
  ).toBeVisible()
  await expect(page.getByText(/\d+ items? in your library/)).toBeVisible()
  await expect(
    page.getByRole("heading", { name: "Library preview" }),
  ).toBeVisible()
  // Superusers see administration with an exact account count
  await expect(
    page.getByRole("heading", { name: "Administration" }),
  ).toBeVisible()
  await expect(page.getByText(/\d+ registered accounts?/)).toBeVisible()
})

// --- Error and retry (superuser storage state) ---

test("Dashboard data failure shows inline retry without redirecting to login", async ({
  page,
}) => {
  let failRequests = true
  await page.route("**/api/v1/items/**", (route) => {
    if (failRequests) {
      return route.abort()
    }
    return route.fallback()
  })

  await page.goto("/")

  // Page identity stays visible while the library fails to load
  await expect(
    page.getByRole("heading", { name: "Workspace overview" }),
  ).toBeVisible()
  await expect(page.getByText("We could not load your library")).toBeVisible({
    timeout: 20000,
  })
  await expect(page).toHaveURL("/")

  failRequests = false
  await page.getByRole("button", { name: "Try again" }).click()
  await expect(
    page.getByRole("heading", { name: "Library status" }),
  ).toBeVisible({ timeout: 20000 })
})

// --- Empty state, first creation, and permission (fresh regular user) ---

test.describe("Fresh regular user", () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test("Empty dashboard onboards, first item populates it, no administration section", async ({
    page,
  }) => {
    const email = randomEmail()
    const password = strongPassword()
    await createUser({ email, password, fullName: "Dashboard QA User" })
    await logInUser(page, email, password)

    // Onboarding replaces zero-value modules
    await expect(
      page.getByRole("heading", { name: "Start your workspace" }),
    ).toBeVisible()

    const title = "My first item"
    await createItemFromDialog(page, title)

    // Populated: exact count and truthful preview
    await expect(page.getByText("1 item in your library")).toBeVisible()
    await expect(
      page.getByRole("heading", { name: "Library preview" }),
    ).toBeVisible()
    await expect(page.getByText(title)).toBeVisible()

    // Role-aware: workspace actions for regular users, no administration
    await expect(
      page.getByRole("heading", { name: "Workspace actions" }),
    ).toBeVisible()
    await expect(
      page.getByRole("heading", { name: "Administration" }),
    ).not.toBeVisible()
  })
})

// --- Mobile representations ---

test.describe("Mobile viewport", () => {
  test.use({ viewport: { width: 375, height: 812 } })

  test("Dashboard fits the mobile viewport with a 44px primary action", async ({
    page,
  }) => {
    await page.goto("/")
    await expect(
      page.getByRole("heading", { name: "Workspace overview" }),
    ).toBeVisible()

    expect(await documentOverflowX(page)).toBeLessThanOrEqual(0)

    const createButton = page
      .getByRole("button", { name: "Create item" })
      .first()
    const box = await createButton.boundingBox()
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44)
  })

  test("Items page renders the record list without horizontal table scrolling", async ({
    page,
  }) => {
    await page.goto("/items")
    await expect(page.getByRole("heading", { name: "Items" })).toBeVisible()

    expect(await documentOverflowX(page)).toBeLessThanOrEqual(0)
    // The desktop table representation is not used on mobile
    await expect(page.locator("table")).toBeHidden()
  })
})

// --- Reduced motion ---

test.describe("Reduced motion", () => {
  test("Overlay and route final states are complete and focus is preserved", async ({
    page,
  }) => {
    await page.emulateMedia({ reducedMotion: "reduce" })
    await page.goto("/")

    const trigger = page.getByRole("button", { name: "Create item" }).first()
    await trigger.click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    // The safety clamp collapses overlay animation to an instant
    const animationSeconds = await dialog.evaluate((el) =>
      Number.parseFloat(getComputedStyle(el).animationDuration),
    )
    expect(animationSeconds).toBeLessThan(0.05)

    // Controls are enabled and focus is contained, then returned
    await expect(dialog.getByLabel(/Title/)).toBeEditable()
    await page.keyboard.press("Escape")
    await expect(dialog).not.toBeVisible()
    await expect(trigger).toBeFocused()

    // Route change resolves instantly to the complete Items workspace
    await page.getByRole("link", { name: "Open library" }).click()
    await page.waitForURL(/\/items/)
    await expect(page.getByRole("heading", { name: "Items" })).toBeVisible()
  })
})
