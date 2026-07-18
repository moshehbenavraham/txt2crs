import { expect, test } from "@playwright/test"
import { createUser } from "./utils/privateApi"
import { randomEmail } from "./utils/random"
import { logInUser, logOutUser } from "./utils/user"

test.use({ storageState: { cookies: [], origins: [] } })

const strongPassword = () => `Apex!${Math.random().toString(36).slice(2, 12)}`

test("Non-superuser direct /admin navigation redirects to forbidden without logout", async ({
  page,
}) => {
  const email = randomEmail()
  const password = strongPassword()

  await createUser({
    email,
    password,
    fullName: "Admin Guard User",
  })
  await logInUser(page, email, password)

  const privilegedAdminRequests: string[] = []
  page.on("request", (request) => {
    if (
      request.method() === "GET" &&
      request.url().includes("/api/v1/users/?skip=0&limit=100")
    ) {
      privilegedAdminRequests.push(request.url())
    }
  })

  await page.goto("/admin")
  await page.waitForURL("/forbidden")
  await expect(
    page.getByRole("heading", { name: "Not authorized" }),
  ).toBeVisible()

  const token = await page.evaluate(
    () =>
      sessionStorage.getItem("access_token") ??
      localStorage.getItem("access_token"),
  )
  expect(token).not.toBeNull()
  expect(privilegedAdminRequests).toHaveLength(0)

  await page.goto("/settings")
  await expect(page).toHaveURL(/\/settings$/)
})

test("Account switch shows fresh current user after logout/login boundary", async ({
  page,
}) => {
  const firstUserEmail = randomEmail()
  const secondUserEmail = randomEmail()
  const firstUserPassword = strongPassword()
  const secondUserPassword = strongPassword()
  const firstUserName = "Switch User One"
  const secondUserName = "Switch User Two"

  await createUser({
    email: firstUserEmail,
    password: firstUserPassword,
    fullName: firstUserName,
  })
  await createUser({
    email: secondUserEmail,
    password: secondUserPassword,
    fullName: secondUserName,
  })

  await logInUser(page, firstUserEmail, firstUserPassword)
  await expect(page.getByTestId("user-menu")).toContainText(firstUserName)

  await logOutUser(page)
  await logInUser(page, secondUserEmail, secondUserPassword)

  await expect(page.getByTestId("user-menu")).toContainText(secondUserName)
  await expect(page.getByTestId("user-menu")).not.toContainText(firstUserName)
})
