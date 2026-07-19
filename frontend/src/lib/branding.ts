/** Canonical public product name used by document and accessible metadata. */
export const PRODUCT_NAME = "txt2crs" as const

/**
 * Build a consistent browser title without repeating product-name strings.
 *
 * Route labels are trimmed because titles can be assembled from optional
 * configuration later. An empty label intentionally falls back to the product
 * name instead of rendering a dangling separator.
 */
export function buildPageTitle(pageLabel?: string): string {
  const normalizedPageLabel = pageLabel?.trim()

  if (!normalizedPageLabel) {
    return PRODUCT_NAME
  }

  return `${normalizedPageLabel} | ${PRODUCT_NAME}`
}
