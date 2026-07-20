const REMOVED_PREVIEW_ELEMENTS = new Set([
  "base",
  "button",
  "embed",
  "form",
  "iframe",
  "input",
  "link",
  "meta",
  "object",
  "script",
  "select",
  "svg",
  "textarea",
])

const REMOVED_URL_ATTRIBUTES = new Set([
  "action",
  "cite",
  "data",
  "download",
  "formaction",
  "href",
  "ping",
  "poster",
  "srcset",
  "target",
  "xlink:href",
])

const REMOVED_INTERACTION_ATTRIBUTES = new Set([
  "autofocus",
  "contenteditable",
  "draggable",
  "form",
  "popover",
  "tabindex",
])

// `sandbox` is deliberately enforced by the iframe attribute, not this meta
// policy. Browsers ignore CSP sandbox when delivered by a meta element and
// would otherwise emit a misleading console warning.
export const PREVIEW_CONTENT_SECURITY_POLICY = [
  "default-src 'none'",
  "script-src 'none'",
  "connect-src 'none'",
  "frame-src 'none'",
  "child-src 'none'",
  "object-src 'none'",
  "base-uri 'none'",
  "form-action 'none'",
  "img-src data:",
  "style-src 'unsafe-inline'",
  "font-src 'none'",
  "media-src 'none'",
  "worker-src 'none'",
  "manifest-src 'none'",
].join("; ")

export class PreviewDocumentError extends Error {
  constructor() {
    super("The HTML preview could not be prepared.")
    this.name = "PreviewDocumentError"
  }
}

export function shouldRemovePreviewElement(tagName: string): boolean {
  return REMOVED_PREVIEW_ELEMENTS.has(tagName.toLowerCase())
}

/**
 * Decide attribute safety without reading private content into application
 * state. The DOM transformer below applies this rule to every parsed element.
 */
export function shouldRemovePreviewAttribute(
  attributeName: string,
  attributeValue: string,
  tagName: string,
): boolean {
  const normalizedName = attributeName.toLowerCase()
  const normalizedTagName = tagName.toLowerCase()
  if (
    normalizedName.startsWith("on") ||
    REMOVED_URL_ATTRIBUTES.has(normalizedName) ||
    REMOVED_INTERACTION_ATTRIBUTES.has(normalizedName)
  ) {
    return true
  }
  if (normalizedName === "src") {
    // A small embedded raster can remain visual without creating a network
    // request. SVG data is excluded because it has its own active-content
    // semantics in browser engines.
    return !(
      normalizedTagName === "img" &&
      /^data:image\/(?:avif|gif|jpeg|png|webp);base64,/i.test(attributeValue)
    )
  }
  if (normalizedName === "style" && /@import|url\s*\(/i.test(attributeValue)) {
    return true
  }
  return false
}

function removeActivePreviewContent(documentNode: Document): void {
  for (const element of [...documentNode.querySelectorAll("*")]) {
    const tagName = element.tagName.toLowerCase()
    if (shouldRemovePreviewElement(tagName)) {
      element.remove()
      continue
    }

    if (
      tagName === "style" &&
      /@import|url\s*\(/i.test(element.textContent ?? "")
    ) {
      element.remove()
      continue
    }

    for (const attribute of [...element.attributes]) {
      if (
        shouldRemovePreviewAttribute(attribute.name, attribute.value, tagName)
      ) {
        element.removeAttribute(attribute.name)
      }
    }
  }
}

/**
 * Build a separate preview-only document using the browser's HTML parser.
 *
 * This output is destined only for an empty-capability sandboxed iframe. It is
 * never assigned to the parent document or React's `dangerouslySetInnerHTML`.
 */
export function createSecuredPreviewDocument(
  rawHtml: string,
  maximumBytes: number,
): string {
  if (
    typeof rawHtml !== "string" ||
    rawHtml.length === 0 ||
    !Number.isSafeInteger(maximumBytes) ||
    maximumBytes <= 0 ||
    new TextEncoder().encode(rawHtml).byteLength > maximumBytes ||
    typeof DOMParser === "undefined"
  ) {
    throw new PreviewDocumentError()
  }

  const parsedDocument = new DOMParser().parseFromString(rawHtml, "text/html")
  if (
    parsedDocument.documentElement === null ||
    parsedDocument.head === null ||
    parsedDocument.body === null
  ) {
    throw new PreviewDocumentError()
  }

  removeActivePreviewContent(parsedDocument)
  const contentSecurityPolicy = parsedDocument.createElement("meta")
  contentSecurityPolicy.setAttribute("http-equiv", "Content-Security-Policy")
  contentSecurityPolicy.setAttribute("content", PREVIEW_CONTENT_SECURITY_POLICY)
  parsedDocument.head.prepend(contentSecurityPolicy)

  if (!parsedDocument.documentElement.hasAttribute("lang")) {
    parsedDocument.documentElement.setAttribute("lang", "en")
  }
  return `<!doctype html>\n${parsedDocument.documentElement.outerHTML}`
}
