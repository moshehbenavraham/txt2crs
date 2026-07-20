import { QueryClient } from "@tanstack/react-query"
import { describe, expect, it } from "vitest"

import { ApiError } from "@/lib/api-error"
import {
  ACCESS_TOKEN_STORAGE_KEY,
  CURRENT_USER_QUERY_KEY,
  clearAuthSession,
  getAccessToken,
  hasAccessToken,
  resetAuthQueryCache,
  setAccessToken,
  shouldInvalidateSession,
} from "./session"

const makeApiError = (status: number, url: string): ApiError =>
  new ApiError({ body: {}, status, url })

const createMemoryStorage = (initial: Record<string, string> = {}) => {
  const state = new Map(Object.entries(initial))

  return {
    adapter: {
      getItem: (key: string) => state.get(key) ?? null,
      setItem: (key: string, value: string) => {
        state.set(key, value)
      },
      removeItem: (key: string) => {
        state.delete(key)
      },
    },
    get: (key: string) => state.get(key) ?? null,
  }
}

describe("session helpers", () => {
  it("invalidates session for 401 errors", () => {
    expect(
      shouldInvalidateSession(makeApiError(401, "/api/v1/jobs/job-123")),
    ).toBe(true)
  })

  it("invalidates session for stale current-user lookups", () => {
    expect(shouldInvalidateSession(makeApiError(404, "/api/v1/users/me"))).toBe(
      true,
    )
  })

  it("does not invalidate session for non-auth authorization failures", () => {
    expect(shouldInvalidateSession(makeApiError(403, "/api/v1/users/me"))).toBe(
      false,
    )
  })

  it("clears query cache on auth-boundary reset", () => {
    const queryClient = new QueryClient()
    queryClient.setQueryData(CURRENT_USER_QUERY_KEY, { id: "user-1" })

    resetAuthQueryCache(queryClient)

    expect(queryClient.getQueryData(CURRENT_USER_QUERY_KEY)).toBeUndefined()
  })

  it("clears query cache and removes token on session clear", () => {
    const queryClient = new QueryClient()
    queryClient.setQueryData(CURRENT_USER_QUERY_KEY, { id: "user-1" })

    const sessionStorage = createMemoryStorage({
      [ACCESS_TOKEN_STORAGE_KEY]: "session-token",
    })
    const localStorage = createMemoryStorage({
      [ACCESS_TOKEN_STORAGE_KEY]: "local-token",
    })

    clearAuthSession(queryClient, {
      session: sessionStorage.adapter,
      local: localStorage.adapter,
    })

    expect(queryClient.getQueryData(CURRENT_USER_QUERY_KEY)).toBeUndefined()
    expect(sessionStorage.get(ACCESS_TOKEN_STORAGE_KEY)).toBeNull()
    expect(localStorage.get(ACCESS_TOKEN_STORAGE_KEY)).toBeNull()
  })

  it("migrates legacy localStorage token into sessionStorage", () => {
    const sessionStorage = createMemoryStorage()
    const localStorage = createMemoryStorage({
      [ACCESS_TOKEN_STORAGE_KEY]: "legacy-token",
    })

    const token = getAccessToken({
      session: sessionStorage.adapter,
      local: localStorage.adapter,
    })

    expect(token).toBe("legacy-token")
    expect(sessionStorage.get(ACCESS_TOKEN_STORAGE_KEY)).toBe("legacy-token")
    expect(localStorage.get(ACCESS_TOKEN_STORAGE_KEY)).toBeNull()
  })

  it("stores new tokens in sessionStorage only", () => {
    const sessionStorage = createMemoryStorage()
    const localStorage = createMemoryStorage({
      [ACCESS_TOKEN_STORAGE_KEY]: "legacy-token",
    })

    setAccessToken("fresh-token", {
      session: sessionStorage.adapter,
      local: localStorage.adapter,
    })

    expect(
      hasAccessToken({
        session: sessionStorage.adapter,
        local: localStorage.adapter,
      }),
    ).toBe(true)
    expect(sessionStorage.get(ACCESS_TOKEN_STORAGE_KEY)).toBe("fresh-token")
    expect(localStorage.get(ACCESS_TOKEN_STORAGE_KEY)).toBeNull()
  })
})
