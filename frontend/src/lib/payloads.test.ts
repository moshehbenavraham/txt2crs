import { describe, expect, it } from "vitest"

import {
  mapAddUserFormToUserCreateRequest,
  mapChangePasswordFormToUpdatePasswordRequest,
} from "./payloads"

describe("payload mappers", () => {
  it("strips confirm_password from add-user API payload", () => {
    const payload = mapAddUserFormToUserCreateRequest({
      email: "new-user@example.com",
      full_name: "New User",
      password: "secret-password-123",
      confirm_password: "secret-password-123",
      is_superuser: false,
      is_active: true,
    })

    expect(payload).toEqual({
      email: "new-user@example.com",
      full_name: "New User",
      password: "secret-password-123",
      is_superuser: false,
      is_active: true,
    })
    expect("confirm_password" in payload).toBe(false)
  })

  it("strips confirm_password from change-password API payload", () => {
    const payload = mapChangePasswordFormToUpdatePasswordRequest({
      current_password: "old-password-123",
      new_password: "new-password-123",
      confirm_password: "new-password-123",
    })

    expect(payload).toEqual({
      current_password: "old-password-123",
      new_password: "new-password-123",
    })
    expect("confirm_password" in payload).toBe(false)
  })
})
