import { expect, test as setup } from "@playwright/test"
import {
  apiBaseUrl,
  authFile,
  firstSuperuser,
  firstSuperuserPassword,
} from "./config.ts"

setup("authenticate", async ({ page, request }) => {
  const shouldCreateIsolatedUser = process.env.PLAYWRIGHT_CREATE_USER === "1"
  const email = process.env.PLAYWRIGHT_TEST_USER_EMAIL ?? firstSuperuser
  const password =
    process.env.PLAYWRIGHT_TEST_USER_PASSWORD ?? firstSuperuserPassword

  if (shouldCreateIsolatedUser) {
    // The dedicated jobs server enables the real local-only signup route and
    // creates a unique normal user. This avoids changing or depending on an
    // operator account while retaining the production password hashing and
    // database-backed authentication path.
    const signupResponse = await request.post(
      `${apiBaseUrl}/api/v1/users/signup`,
      {
        data: {
          email,
          password,
          full_name: "Browser Journey Learner",
        },
      },
    )
    expect(signupResponse.status()).toBe(201)
  }

  // Login behavior has its own browser tests. The shared setup calls the
  // authenticated API directly so unrelated route tests do not depend on
  // form timing, toast rendering, or a second navigation race.
  const response = await request.post(
    `${apiBaseUrl}/api/v1/login/access-token`,
    {
      form: {
        username: email,
        password,
      },
    },
  )
  expect(response.ok()).toBe(true)
  const payload: unknown = await response.json()
  expect(payload).toMatchObject({ access_token: expect.any(String) })
  const accessToken = (payload as { access_token: string }).access_token

  await page.goto("/login")
  await page.evaluate((token) => {
    sessionStorage.setItem("access_token", token)
    // Playwright storage state persists localStorage but not sessionStorage.
    // Seed the legacy location so each fresh test context exercises the
    // application's one-time migration into session-scoped storage.
    localStorage.setItem("access_token", token)
  }, accessToken)
  // Validate the final protected landing route and its current-user guard.
  await page.goto("/create")
  await expect(page).toHaveURL("/create")
  await expect(
    page.getByRole("heading", { name: "Create a course" }),
  ).toBeVisible()

  // Storage state does not persist sessionStorage. Re-seed the one-time legacy
  // location after the route check so every new browser context can exercise
  // the application's migration into session-only storage.
  await page.evaluate((token) => {
    sessionStorage.removeItem("access_token")
    localStorage.setItem("access_token", token)
  }, accessToken)

  await page.context().storageState({ path: authFile })
})
