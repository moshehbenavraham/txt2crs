import { expect, type Page, test } from "@playwright/test"

const documentOverflowX = (page: Page) =>
  page.evaluate(
    () =>
      document.documentElement.scrollWidth -
      document.documentElement.clientWidth,
  )

test("Dashboard describes the four-part learning package without donor navigation", async ({
  page,
}) => {
  await page.goto("/")

  await expect(
    page.getByRole("heading", { name: "Course workspace" }),
  ).toBeVisible()
  await expect(
    page.getByRole("heading", { name: "One input. Four learning assets." }),
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
  await expect(page.getByRole("link", { name: "Items" })).not.toBeVisible()
})

test("Retired donor route resolves to the application not-found surface", async ({
  page,
}) => {
  await page.goto("/items")
  await expect(page.getByTestId("not-found")).toBeVisible()
  await expect(
    page.getByText("The page you are looking for was not found."),
  ).toBeVisible()
})

test.describe("Mobile viewport", () => {
  test.use({ viewport: { width: 375, height: 812 } })

  test("Dashboard fits the mobile viewport with a 44px account action", async ({
    page,
  }) => {
    await page.goto("/")
    await expect(
      page.getByRole("heading", { name: "Course workspace" }),
    ).toBeVisible()

    expect(await documentOverflowX(page)).toBeLessThanOrEqual(0)

    const accountLink = page.getByRole("link", { name: "Account settings" })
    const box = await accountLink.boundingBox()
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44)
    await accountLink.click()
    await expect(page).toHaveURL(/\/settings$/)
    await expect(
      page.getByRole("heading", { name: "User Settings" }),
    ).toBeVisible()
  })
})

test.describe("Reduced motion", () => {
  test("Account navigation resolves directly to its complete final state", async ({
    page,
  }) => {
    await page.emulateMedia({ reducedMotion: "reduce" })
    await page.goto("/")

    await page.getByRole("link", { name: "Account settings" }).click()
    await expect(page).toHaveURL(/\/settings$/)
    await expect(
      page.getByRole("heading", { name: "User Settings" }),
    ).toBeVisible()
  })
})
