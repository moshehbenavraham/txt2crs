import { describe, expect, it } from "vitest"

import { buildPageTitle, PRODUCT_NAME } from "./branding"

describe("txt2crs branding", () => {
  it("uses one canonical product name", () => {
    expect(PRODUCT_NAME).toBe("txt2crs")
  })

  it("builds a product-scoped page title", () => {
    expect(buildPageTitle("Sign in")).toBe("Sign in | txt2crs")
  })

  it("uses only the product name when the page label is omitted", () => {
    expect(buildPageTitle()).toBe("txt2crs")
    expect(buildPageTitle("   ")).toBe("txt2crs")
  })
})
