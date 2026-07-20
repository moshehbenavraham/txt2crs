import { readFileSync } from "node:fs"
import { expect, test as teardown } from "@playwright/test"
import { apiBaseUrl, authFile } from "./config.ts"

function readTestAccessToken(): string | null {
  let persistedState: unknown
  try {
    persistedState = JSON.parse(readFileSync(authFile, "utf8"))
  } catch {
    return null
  }
  if (
    typeof persistedState !== "object" ||
    persistedState === null ||
    !("origins" in persistedState) ||
    !Array.isArray(persistedState.origins)
  ) {
    return null
  }

  for (const origin of persistedState.origins) {
    if (
      typeof origin !== "object" ||
      origin === null ||
      !("localStorage" in origin) ||
      !Array.isArray(origin.localStorage)
    ) {
      continue
    }
    const tokenEntry = origin.localStorage.find(
      (entry: unknown) =>
        typeof entry === "object" &&
        entry !== null &&
        "name" in entry &&
        entry.name === "access_token" &&
        "value" in entry &&
        typeof entry.value === "string",
    ) as { value: string } | undefined
    if (tokenEntry) {
      return tokenEntry.value
    }
  }
  return null
}

teardown(
  "remove the isolated learner and all owned engine state",
  async ({ request }) => {
    if (process.env.PLAYWRIGHT_CREATE_USER !== "1") {
      return
    }

    // The setup project persists its already-issued bearer token in a fresh,
    // run-owned storage-state file. Reusing it avoids a second login and still
    // lets teardown run when a browser assertion fails midway through.
    const accessToken = readTestAccessToken()
    if (accessToken === null) {
      return
    }
    const deleteResponse = await request.delete(
      `${apiBaseUrl}/api/v1/users/me`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      },
    )

    expect(deleteResponse.status()).toBe(200)
  },
)
