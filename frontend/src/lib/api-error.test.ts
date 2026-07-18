import { describe, expect, it } from "vitest"

import { ApiError, createApiError, getApiErrorMessage } from "./api-error"

describe("API error helpers", () => {
  it("extracts RFC 9457 detail messages", () => {
    expect(getApiErrorMessage({ detail: "Invalid credentials" })).toBe(
      "Invalid credentials",
    )
  })

  it("extracts the first validation issue", () => {
    expect(
      getApiErrorMessage({
        detail: [{ msg: "Password must contain at least 8 characters" }],
      }),
    ).toBe("Password must contain at least 8 characters")
  })

  it("preserves response and request context", () => {
    const error = createApiError(
      { detail: "Not authenticated" },
      new Response(null, { status: 401 }),
      new Request("https://example.test/api/v1/users/me"),
    )

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(401)
    expect(error.url).toBe("https://example.test/api/v1/users/me")
    expect(error.message).toBe("Not authenticated")
  })

  it("preserves network error messages without a response", () => {
    const error = createApiError(new Error("Network unavailable"))

    expect(error.status).toBe(0)
    expect(error.message).toBe("Network unavailable")
  })

  it("preserves plain-text API errors", () => {
    expect(getApiErrorMessage("Service unavailable")).toBe(
      "Service unavailable",
    )
  })
})
