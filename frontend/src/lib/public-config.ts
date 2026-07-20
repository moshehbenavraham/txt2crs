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
  return rawValue === "true"
}

export const publicSignupVisible = parsePublicSignupVisibility(
  import.meta.env.VITE_ENABLE_PUBLIC_SIGNUP,
)
