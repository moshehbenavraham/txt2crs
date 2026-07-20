import { describe, expect, it } from "vitest"
import { parsePublicSignupVisibility } from "./public-config"

describe("public signup display configuration", () => {
  it.each([
    [undefined, false],
    ["", false],
    ["false", false],
    ["TRUE", false],
    ["true", true],
  ])("maps %s to %s without broad truthy coercion", (rawValue, expected) => {
    expect(parsePublicSignupVisibility(rawValue)).toBe(expected)
  })
})
