import { expect, test as setup } from "@playwright/test"
import { apiBaseUrl, firstSuperuser, firstSuperuserPassword } from "./config.ts"

const authFile = "playwright/.auth/user.json"

setup("authenticate", async ({ page, request }) => {
  // Login behavior has its own browser tests. The shared setup calls the
  // authenticated API directly so unrelated route tests do not depend on
  // form timing, toast rendering, or a second navigation race.
  const response = await request.post(
    `${apiBaseUrl}/api/v1/login/access-token`,
    {
      form: {
        username: firstSuperuser,
        password: firstSuperuserPassword,
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
  await page.goto("/")
  await expect(page).toHaveURL("/")

  await page.context().storageState({ path: authFile })
})
