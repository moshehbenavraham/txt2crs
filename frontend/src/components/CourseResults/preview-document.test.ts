import { describe, expect, it } from "vitest"

import {
  PREVIEW_CONTENT_SECURITY_POLICY,
  shouldRemovePreviewAttribute,
  shouldRemovePreviewElement,
} from "./preview-document"

describe("HTML preview security policy", () => {
  it("denies scripts, connections, frames, forms, plugins, and navigation", () => {
    expect(PREVIEW_CONTENT_SECURITY_POLICY).toContain("default-src 'none'")
    expect(PREVIEW_CONTENT_SECURITY_POLICY).toContain("script-src 'none'")
    expect(PREVIEW_CONTENT_SECURITY_POLICY).toContain("connect-src 'none'")
    expect(PREVIEW_CONTENT_SECURITY_POLICY).toContain("frame-src 'none'")
    expect(PREVIEW_CONTENT_SECURITY_POLICY).toContain("form-action 'none'")
    expect(PREVIEW_CONTENT_SECURITY_POLICY).toContain("base-uri 'none'")
    expect(PREVIEW_CONTENT_SECURITY_POLICY).toContain("object-src 'none'")
  })

  it.each(["script", "iframe", "object", "embed", "base", "form", "input"])(
    "removes active <%s> elements",
    (tagName) => {
      expect(shouldRemovePreviewElement(tagName)).toBe(true)
    },
  )

  it("removes event handlers, navigable URLs, refresh, and active controls", () => {
    expect(shouldRemovePreviewAttribute("onclick", "alert(1)", "p")).toBe(true)
    expect(
      shouldRemovePreviewAttribute(
        "href",
        "javascript:alert(document.cookie)",
        "a",
      ),
    ).toBe(true)
    expect(
      shouldRemovePreviewAttribute("href", "https://example.test", "a"),
    ).toBe(true)
    expect(
      shouldRemovePreviewAttribute("src", "https://tracker.test/pixel", "img"),
    ).toBe(true)
    expect(shouldRemovePreviewAttribute("style", "color: red", "p")).toBe(false)
    expect(shouldRemovePreviewAttribute("class", "lesson", "section")).toBe(
      false,
    )
  })
})
