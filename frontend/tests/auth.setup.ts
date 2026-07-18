import { test as setup } from "@playwright/test"
import { firstSuperuser, firstSuperuserPassword } from "./config.ts"

const authFile = "playwright/.auth/user.json"

setup("authenticate", async ({ page }) => {
  await page.goto("/login")
  await page.getByTestId("email-input").fill(firstSuperuser)
  await page.getByTestId("password-input").fill(firstSuperuserPassword)
  await page.getByRole("button", { name: "Sign In" }).click()
  await page.waitForURL("/")

  // Playwright storage state persists localStorage but not sessionStorage.
  // Seed the legacy location so each test context exercises the app's
  // one-time migration into session-scoped storage.
  await page.evaluate(() => {
    const token = sessionStorage.getItem("access_token")
    if (token) {
      localStorage.setItem("access_token", token)
    }
  })

  await page.context().storageState({ path: authFile })
})
