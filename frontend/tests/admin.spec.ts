import { expect, test } from "@playwright/test"
import { firstSuperuser, firstSuperuserPassword } from "./config.ts"
import { createUser } from "./utils/privateApi"
import { randomEmail, randomPassword } from "./utils/random"
import { logInUser } from "./utils/user"

test("Admin page shows its title and description", async ({ page }) => {
  await page.goto("/admin")

  await expect(page.getByRole("heading", { name: "Users" })).toBeVisible()
  await expect(
    page.getByText("Manage user accounts and permissions."),
  ).toBeVisible()
})

test("Create user button is visible", async ({ page }) => {
  await page.goto("/admin")

  await expect(page.getByRole("button", { name: "Create user" })).toBeVisible()
})

test.describe("Admin user management", () => {
  test("creates a user", async ({ page }) => {
    await page.goto("/admin")

    const email = randomEmail()
    const password = randomPassword()
    const fullName = "Test User Admin"

    await page.getByRole("button", { name: "Create user" }).click()
    const dialog = page.getByRole("dialog")
    await dialog.getByPlaceholder("Email").fill(email)
    await dialog.getByPlaceholder("Full name").fill(fullName)
    await dialog.getByPlaceholder("Password").first().fill(password)
    await dialog.getByPlaceholder("Password").last().fill(password)
    await dialog.getByRole("button", { name: "Create user" }).click()

    await expect(page.getByText("User created successfully")).toBeVisible()
    await expect(dialog).not.toBeVisible()
    await expect(page.getByRole("row").filter({ hasText: email })).toBeVisible()
  })

  test("creates a superuser", async ({ page }) => {
    await page.goto("/admin")

    const email = randomEmail()
    const password = randomPassword()

    await page.getByRole("button", { name: "Create user" }).click()
    const dialog = page.getByRole("dialog")
    await dialog.getByPlaceholder("Email").fill(email)
    await dialog.getByPlaceholder("Password").first().fill(password)
    await dialog.getByPlaceholder("Password").last().fill(password)
    await dialog.getByLabel("Is superuser?").check()
    await dialog.getByLabel("Is active?").check()
    await dialog.getByRole("button", { name: "Create user" }).click()

    await expect(page.getByText("User created successfully")).toBeVisible()
    await expect(dialog).not.toBeVisible()
    const userRow = page.getByRole("row").filter({ hasText: email })
    await expect(userRow.getByText("Superuser")).toBeVisible()
  })

  test("edits a user", async ({ page }) => {
    await page.goto("/admin")

    const email = randomEmail()
    const password = randomPassword()
    const updatedName = "Updated Name"

    await page.getByRole("button", { name: "Create user" }).click()
    let dialog = page.getByRole("dialog")
    await dialog.getByPlaceholder("Email").fill(email)
    await dialog.getByPlaceholder("Full name").fill("Original Name")
    await dialog.getByPlaceholder("Password").first().fill(password)
    await dialog.getByPlaceholder("Password").last().fill(password)
    await dialog.getByRole("button", { name: "Create user" }).click()
    await expect(page.getByText("User created successfully")).toBeVisible()
    await expect(dialog).not.toBeVisible()

    const userRow = page.getByRole("row").filter({ hasText: email })
    await userRow.getByRole("button").click()
    await page.getByRole("menuitem", { name: "Edit User" }).click()

    dialog = page.getByRole("dialog")
    await dialog.getByPlaceholder("Full name").fill(updatedName)
    await dialog.getByRole("button", { name: "Save" }).click()

    await expect(page.getByText("User updated successfully")).toBeVisible()
    await expect(
      page.getByRole("row").filter({ hasText: email }).getByText(updatedName),
    ).toBeVisible()
  })

  test("deletes a user", async ({ page }) => {
    await page.goto("/admin")

    const email = randomEmail()
    const password = randomPassword()

    await page.getByRole("button", { name: "Create user" }).click()
    const dialog = page.getByRole("dialog")
    await dialog.getByPlaceholder("Email").fill(email)
    await dialog.getByPlaceholder("Password").first().fill(password)
    await dialog.getByPlaceholder("Password").last().fill(password)
    await dialog.getByRole("button", { name: "Create user" }).click()
    await expect(page.getByText("User created successfully")).toBeVisible()
    await expect(dialog).not.toBeVisible()

    const userRow = page.getByRole("row").filter({ hasText: email })
    await userRow.getByRole("button").click()
    await page.getByRole("menuitem", { name: "Delete User" }).click()
    await page
      .getByRole("dialog")
      .getByRole("button", { name: "Delete" })
      .click()

    await expect(
      page.getByText("The user was deleted successfully"),
    ).toBeVisible()
    await expect(userRow).not.toBeVisible()
  })

  test("cancels user creation", async ({ page }) => {
    await page.goto("/admin")

    await page.getByRole("button", { name: "Create user" }).click()
    const dialog = page.getByRole("dialog")
    await dialog.getByPlaceholder("Email").fill("test@example.com")
    await dialog.getByRole("button", { name: "Cancel" }).click()

    await expect(dialog).not.toBeVisible()
  })

  test("requires a valid email", async ({ page }) => {
    await page.goto("/admin")

    await page.getByRole("button", { name: "Create user" }).click()
    const dialog = page.getByRole("dialog")
    await dialog.getByPlaceholder("Email").fill("invalid-email")
    await dialog.getByPlaceholder("Email").blur()

    await expect(dialog.getByText("Invalid email address")).toBeVisible()
  })

  test("requires an eight-character password", async ({ page }) => {
    await page.goto("/admin")

    await page.getByRole("button", { name: "Create user" }).click()
    const dialog = page.getByRole("dialog")
    await dialog.getByPlaceholder("Email").fill(randomEmail())
    await dialog.getByPlaceholder("Password").first().fill("short")
    await dialog.getByPlaceholder("Password").last().fill("short")
    await dialog.getByRole("button", { name: "Create user" }).click()

    await expect(
      dialog.getByText("Password must be at least 8 characters"),
    ).toBeVisible()
  })

  test("requires matching passwords", async ({ page }) => {
    await page.goto("/admin")

    await page.getByRole("button", { name: "Create user" }).click()
    const dialog = page.getByRole("dialog")
    await dialog.getByPlaceholder("Email").fill(randomEmail())
    await dialog.getByPlaceholder("Password").first().fill(randomPassword())
    await dialog.getByPlaceholder("Password").last().fill("Different!12345")
    await dialog.getByPlaceholder("Password").last().blur()

    await expect(dialog.getByText("The passwords don't match")).toBeVisible()
  })
})

test.describe("Admin access control", () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test("redirects a non-superuser to the forbidden page", async ({ page }) => {
    const email = randomEmail()
    const password = randomPassword()
    await createUser({ email, password })
    await logInUser(page, email, password)

    await page.goto("/admin")

    await expect(page).toHaveURL(/\/forbidden$/)
    await expect(
      page.getByRole("heading", { name: "Not authorized" }),
    ).toBeVisible()
  })

  test("allows a superuser to access the page", async ({ page }) => {
    await logInUser(page, firstSuperuser, firstSuperuserPassword)

    await page.goto("/admin")

    await expect(page.getByRole("heading", { name: "Users" })).toBeVisible()
  })
})
