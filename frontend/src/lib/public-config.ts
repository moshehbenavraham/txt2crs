/**
 * Public, non-secret frontend build configuration.
 *
 * Visibility is intentionally narrower than authorization: showing signup
 * never makes the backend accept it, and a revoked/disabled backend still
 * returns the authoritative response.
 */
export function parsePublicSignupVisibility(
  rawValue: string | undefined,
): boolean {
  // A build with no explicit setting follows the product's open-registration
  // default. Operators can still hide signup with an exact `false` value; the
  // backend remains the authorization authority in either case.
  return rawValue === undefined || rawValue === "true"
}

export const publicSignupVisible = parsePublicSignupVisibility(
  import.meta.env.VITE_ENABLE_PUBLIC_SIGNUP,
)

export const DEFAULT_HTML_PREVIEW_MAX_BYTES = 5_242_880

/**
 * Parse the public preview-only byte cap without JavaScript coercion.
 *
 * Vite values are untrusted build strings. Requiring canonical base-10 text
 * keeps whitespace, decimals, signs, Infinity, and unsafe integers from
 * silently changing a browser security boundary.
 */
export function parseHtmlPreviewMaxBytes(rawValue: string | undefined): number {
  if (rawValue === undefined || !/^[1-9]\d*$/.test(rawValue)) {
    return DEFAULT_HTML_PREVIEW_MAX_BYTES
  }
  const parsedValue = Number(rawValue)
  return Number.isSafeInteger(parsedValue)
    ? parsedValue
    : DEFAULT_HTML_PREVIEW_MAX_BYTES
}

export const htmlPreviewMaxBytes = parseHtmlPreviewMaxBytes(
  import.meta.env.VITE_HTML_PREVIEW_MAX_BYTES,
)
