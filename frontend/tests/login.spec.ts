import { expect, type Page, test } from "@playwright/test"
import { firstSuperuser, firstSuperuserPassword } from "./config.ts"
import { randomPassword } from "./utils/random.ts"

test.use({ storageState: { cookies: [], origins: [] } })

// The default Compose suite exercises the configured operator account. The
// isolated jobs suite creates a fresh normal user instead, so login assertions
// must follow the credentials owned by the active test environment.
const loginEmail = process.env.PLAYWRIGHT_TEST_USER_EMAIL ?? firstSuperuser
const loginPassword =
  process.env.PLAYWRIGHT_TEST_USER_PASSWORD ?? firstSuperuserPassword

const fillForm = async (page: Page, email: string, password: string) => {
  await page.getByTestId("email-input").fill(email)
  await page.getByTestId("password-input").fill(password)
}

const verifyInput = async (page: Page, testId: string) => {
  const input = page.getByTestId(testId)
  await expect(input).toBeVisible()
  await expect(input).toHaveValue("")
  await expect(input).toBeEditable()
}

test("Inputs are visible, empty and editable", async ({ page }) => {
  await page.goto("/login")

  await verifyInput(page, "email-input")
  await verifyInput(page, "password-input")
})

test("Sign In button is visible", async ({ page }) => {
  await page.goto("/login")

  await expect(page.getByRole("button", { name: "Sign In" })).toBeVisible()
})

test("Forgot Password link is visible", async ({ page }) => {
  await page.goto("/login")

  await expect(
    page.getByRole("link", { name: "Forgot password?" }),
  ).toBeVisible()
})

test("Log in with valid email and password ", async ({ page }) => {
  await page.goto("/login")

  await fillForm(page, loginEmail, loginPassword)
  await page.getByRole("button", { name: "Sign In" }).click()

  await page.waitForURL("/create")

  await expect(
    page.getByRole("heading", { name: "Create a course" }),
  ).toBeVisible()
})

test("restores the originally requested protected deep link after login", async ({
  page,
}) => {
  await page.goto("/jobs/job-deep-link")
  await expect(page).toHaveURL(/\/login\?returnTo=%2Fjobs%2Fjob-deep-link$/)

  await fillForm(page, loginEmail, loginPassword)
  await page.getByRole("button", { name: "Sign In" }).click()

  await expect(page).toHaveURL(/\/jobs\/job-deep-link$/)
})

test("Log in with invalid email", async ({ page }) => {
  await page.goto("/login")

  await fillForm(page, "invalidemail", loginPassword)
  await page.getByRole("button", { name: "Sign In" }).click()

  await expect(page.getByText("Invalid email address")).toBeVisible()
})

test("Log in with invalid password", async ({ page }) => {
  const password = randomPassword()

  await page.goto("/login")
  await fillForm(page, loginEmail, password)
  await page.getByRole("button", { name: "Sign In" }).click()

  await expect(page.getByText("Incorrect email or password")).toBeVisible()
})

// Log out

test("Successful log out", async ({ page }) => {
  await page.goto("/login")

  await fillForm(page, loginEmail, loginPassword)
  await page.getByRole("button", { name: "Sign In" }).click()

  await page.waitForURL("/create")

  await expect(
    page.getByRole("heading", { name: "Create a course" }),
  ).toBeVisible()

  await page.getByTestId("user-menu").click()
  await page.getByRole("menuitem", { name: "Log out" }).click()
  await page.waitForURL("/login")
})

test("Logged-out user cannot access protected routes", async ({ page }) => {
  await page.goto("/login")

  await fillForm(page, loginEmail, loginPassword)
  await page.getByRole("button", { name: "Sign In" }).click()

  await page.waitForURL("/create")

  await expect(
    page.getByRole("heading", { name: "Create a course" }),
  ).toBeVisible()

  await page.getByTestId("user-menu").click()
  await page.getByRole("menuitem", { name: "Log out" }).click()
  await page.waitForURL("/login")

  await page.goto("/create")
  await expect(page).toHaveURL(/\/login\?returnTo=%2Fcreate$/)
})

test("Redirects to /login when token is wrong", async ({ page }) => {
  await page.goto("/settings")
  await page.evaluate(() => {
    sessionStorage.setItem("access_token", "invalid_token")
  })
  await page.goto("/settings")
  await expect(page).toHaveURL(/\/login\?returnTo=%2Fsettings$/)
})
