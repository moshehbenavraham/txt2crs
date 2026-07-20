import { describe, expect, it } from "vitest"
import {
  DEFAULT_HTML_PREVIEW_MAX_BYTES,
  parseHtmlPreviewMaxBytes,
  parsePublicSignupVisibility,
} from "./public-config"

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

describe("HTML preview byte configuration", () => {
  it.each([undefined, "", "0", "-1", "5.5", "NaN", "Infinity", " 5242880"])(
    "falls back safely for %s",
    (rawValue) => {
      expect(parseHtmlPreviewMaxBytes(rawValue)).toBe(
        DEFAULT_HTML_PREVIEW_MAX_BYTES,
      )
    },
  )

  it("accepts a positive base-10 integer without broad coercion", () => {
    expect(parseHtmlPreviewMaxBytes("5242880")).toBe(5_242_880)
    expect(parseHtmlPreviewMaxBytes("1")).toBe(1)
  })
})
