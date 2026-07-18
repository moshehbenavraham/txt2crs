import { expect, test } from "@playwright/test"
import { createUser } from "./utils/privateApi"
import {
  randomEmail,
  randomItemDescription,
  randomItemTitle,
  randomPassword,
} from "./utils/random"
import { logInUser } from "./utils/user"

test("Items page shows its title and description", async ({ page }) => {
  await page.goto("/items")

  await expect(page.getByRole("heading", { name: "Items" })).toBeVisible()
  await expect(
    page.getByText("Create and manage the items in your library."),
  ).toBeVisible()
})

test("Create item button is visible", async ({ page }) => {
  await page.goto("/items")

  await expect(page.getByRole("button", { name: "Create item" })).toBeVisible()
})

test.describe("Items management", () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  let email: string
  const password = randomPassword()

  test.beforeAll(async () => {
    email = randomEmail()
    await createUser({ email, password })
  })

  test.beforeEach(async ({ page }) => {
    await logInUser(page, email, password)
    await page.goto("/items")
  })

  test("creates an item with a description", async ({ page }) => {
    const title = randomItemTitle()
    const description = randomItemDescription()

    await page.getByRole("button", { name: "Create item" }).click()
    const dialog = page.getByRole("dialog")
    await dialog.getByLabel("Title").fill(title)
    await dialog.getByLabel("Description").fill(description)
    await dialog.getByRole("button", { name: "Create item" }).click()

    await expect(page.getByText("Item created successfully")).toBeVisible()
    await expect(page.getByRole("row").filter({ hasText: title })).toBeVisible()
  })

  test("creates an item with only required fields", async ({ page }) => {
    const title = randomItemTitle()

    await page.getByRole("button", { name: "Create item" }).click()
    const dialog = page.getByRole("dialog")
    await dialog.getByLabel("Title").fill(title)
    await dialog.getByRole("button", { name: "Create item" }).click()

    await expect(page.getByText("Item created successfully")).toBeVisible()
    await expect(page.getByRole("row").filter({ hasText: title })).toBeVisible()
  })

  test("cancels item creation", async ({ page }) => {
    await page.getByRole("button", { name: "Create item" }).click()
    const dialog = page.getByRole("dialog")
    await dialog.getByLabel("Title").fill("Canceled Item")
    await dialog.getByRole("button", { name: "Cancel" }).click()

    await expect(dialog).not.toBeVisible()
  })

  test("requires a title", async ({ page }) => {
    await page.getByRole("button", { name: "Create item" }).click()
    const dialog = page.getByRole("dialog")
    await dialog.getByLabel("Title").fill("")
    await dialog.getByLabel("Title").blur()

    await expect(dialog.getByText("Title is required")).toBeVisible()
  })

  test.describe("Edit and delete", () => {
    let itemTitle: string

    test.beforeEach(async ({ page }) => {
      itemTitle = randomItemTitle()

      await page.getByRole("button", { name: "Create item" }).click()
      const dialog = page.getByRole("dialog")
      await dialog.getByLabel("Title").fill(itemTitle)
      await dialog.getByRole("button", { name: "Create item" }).click()
      await expect(page.getByText("Item created successfully")).toBeVisible()
      await expect(dialog).not.toBeVisible()
    })

    test("edits an item", async ({ page }) => {
      const itemRow = page.getByRole("row").filter({ hasText: itemTitle })
      await itemRow.getByRole("button").last().click()
      await page.getByRole("menuitem", { name: "Edit Item" }).click()

      const updatedTitle = randomItemTitle()
      const dialog = page.getByRole("dialog")
      await dialog.getByLabel("Title").fill(updatedTitle)
      await dialog.getByRole("button", { name: "Save" }).click()

      await expect(page.getByText("Item updated successfully")).toBeVisible()
      await expect(
        page.getByRole("row").filter({ hasText: updatedTitle }),
      ).toBeVisible()
    })

    test("deletes an item", async ({ page }) => {
      const itemRow = page.getByRole("row").filter({ hasText: itemTitle })
      await itemRow.getByRole("button").last().click()
      await page.getByRole("menuitem", { name: "Delete Item" }).click()

      await page
        .getByRole("dialog")
        .getByRole("button", { name: "Delete" })
        .click()

      await expect(
        page.getByText("The item was deleted successfully"),
      ).toBeVisible()
      await expect(page.getByText(itemTitle)).not.toBeVisible()
    })
  })
})

test.describe("Items empty state", () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test("shows guidance when no items exist", async ({ page }) => {
    const email = randomEmail()
    const password = randomPassword()
    await createUser({ email, password })
    await logInUser(page, email, password)

    await page.goto("/items")

    await expect(page.getByText("You don't have any items yet")).toBeVisible()
    await expect(page.getByText("Add a new item to get started")).toBeVisible()
  })
})
