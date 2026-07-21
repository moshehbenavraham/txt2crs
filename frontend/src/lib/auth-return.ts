const DEFAULT_AUTHENTICATED_PATH = "/create"
const MAXIMUM_RETURN_PATH_LENGTH = 2_048
const INTERNAL_URL_BASE = "https://txt2crs.invalid"

const protectedExactPaths = new Set([
  "/create",
  "/library",
  "/setup",
  "/settings",
  "/admin",
  "/forbidden",
])

/**
 * Return one known same-origin protected path or the safe learner workspace.
 *
 * The login search parameter is browser-controlled input. Restricting it to
 * the application's real protected routes prevents open redirects, recursive
 * login loops, and backslash URL parsing differences between browsers.
 */
export function normalizeAuthReturnTo(candidate: string | undefined): string {
  if (
    !candidate ||
    candidate.length > MAXIMUM_RETURN_PATH_LENGTH ||
    !candidate.startsWith("/") ||
    candidate.startsWith("//") ||
    candidate.includes("\\") ||
    [...candidate].some((character) => character.charCodeAt(0) < 32)
  ) {
    return DEFAULT_AUTHENTICATED_PATH
  }

  try {
    const parsedReturnUrl = new URL(candidate, INTERNAL_URL_BASE)
    const isKnownProtectedPath =
      protectedExactPaths.has(parsedReturnUrl.pathname) ||
      parsedReturnUrl.pathname.startsWith("/jobs/")
    if (parsedReturnUrl.origin !== INTERNAL_URL_BASE || !isKnownProtectedPath) {
      return DEFAULT_AUTHENTICATED_PATH
    }
    return `${parsedReturnUrl.pathname}${parsedReturnUrl.search}${parsedReturnUrl.hash}`
  } catch {
    return DEFAULT_AUTHENTICATED_PATH
  }
}

/** Build the exact login URL used by route guards and expired-session repair. */
export function buildLoginHref(returnTo: string): string {
  const safeReturnTo = normalizeAuthReturnTo(returnTo)
  return `/login?returnTo=${encodeURIComponent(safeReturnTo)}`
}
