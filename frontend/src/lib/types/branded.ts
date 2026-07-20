/**
 * Branded Types for Domain Concepts
 *
 * Branded types (also called "nominal types" or "opaque types") provide compile-time
 * type safety for primitive values that have semantic meaning in the domain.
 *
 * Without branded types, it is easy to pass an arbitrary string where a
 * validated user identifier or email is expected. Branded types prevent that
 * class of bug while preserving the underlying string representation.
 *
 * @example
 * ```typescript
 * const userId: UserId = createUserId("user-123");
 * const email: Email = createEmail("learner@example.com");
 * ```
 *
 * @see https://egghead.io/blog/using-branded-types-in-typescript
 */

// ============================================================================
// Brand Infrastructure
// ============================================================================

/**
 * Brand utility type for creating nominal/branded types.
 *
 * Creates a new type that is structurally identical to K but carries
 * a phantom type T that makes it incompatible with other branded types.
 *
 * @typeParam K - The underlying primitive type (string, number, etc.)
 * @typeParam T - A unique type literal that brands this type
 */
type Brand<K, T> = K & { readonly __brand: T }

// ============================================================================
// User Domain Types
// ============================================================================

/**
 * Branded type for User IDs.
 *
 * User IDs are UUIDs represented as strings. This type ensures that
 * user IDs cannot be accidentally used where other ID types are expected.
 *
 * @example
 * ```typescript
 * const userId = createUserId("550e8400-e29b-41d4-a716-446655440000");
 * ```
 */
export type UserId = Brand<string, "UserId">

/**
 * Branded type for validated email addresses.
 *
 * Represents an email that has been validated to be in correct format.
 * Note: This does not guarantee the email exists, only that it's syntactically valid.
 */
export type Email = Brand<string, "Email">

// ============================================================================
// Course Job Domain Types
// ============================================================================

/**
 * Public engine job identifiers are finite package identifiers, not UUIDs.
 * Keeping a separate brand prevents a user ID from becoming a job route.
 */
export type JobId = Brand<string, "JobId">

/** Artifact identifiers share the package grammar but remain a distinct role. */
export type ArtifactId = Brand<string, "ArtifactId">

/**
 * Owner-scoped retry identity.
 *
 * Its grammar permits a separator as the first character, unlike job and
 * artifact identifiers, so it must never reuse their validation function.
 */
export type IdempotencyKey = Brand<string, "IdempotencyKey">

// ============================================================================
// Type Guards
// ============================================================================

/** UUID v4 regex pattern for validation */
const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

/** Email regex pattern (simplified, RFC 5322 compliant subset) */
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

/** Mirrored backend ``JobIdentifier`` and ``ArtifactIdentifier`` grammar. */
const COURSE_IDENTIFIER_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/

/** Mirrored backend owner-scoped ``IdempotencyKey`` grammar. */
const IDEMPOTENCY_KEY_PATTERN = /^[A-Za-z0-9._:-]{1,128}$/

/**
 * Type guard to check if a string is a valid UUID format.
 *
 * @param value - The string to validate
 * @returns True if the string matches UUID v4 format
 */
export function isValidUuid(value: string): boolean {
  return UUID_PATTERN.test(value)
}

/**
 * Type guard for UserId values.
 *
 * @param value - The string to validate
 * @returns True if the string is a valid UserId (UUID format)
 */
export function isUserId(value: string): value is UserId {
  return isValidUuid(value)
}

/**
 * Type guard for Email values.
 *
 * @param value - The string to validate
 * @returns True if the string is a valid email format
 */
export function isEmail(value: string): value is Email {
  return EMAIL_PATTERN.test(value)
}

/** Return whether a string is a finite public job identifier. */
export function isJobId(value: string): value is JobId {
  return COURSE_IDENTIFIER_PATTERN.test(value)
}

/** Return whether a string is a finite public artifact identifier. */
export function isArtifactId(value: string): value is ArtifactId {
  return COURSE_IDENTIFIER_PATTERN.test(value)
}

/** Return whether a string is a finite owner-scoped retry key. */
export function isIdempotencyKey(value: string): value is IdempotencyKey {
  return IDEMPOTENCY_KEY_PATTERN.test(value)
}

// ============================================================================
// Factory Functions
// ============================================================================

/**
 * Create a validated UserId from a string.
 *
 * @param value - A UUID string to convert to UserId
 * @returns The branded UserId
 * @throws Error if the value is not a valid UUID
 *
 * @example
 * ```typescript
 * const id = createUserId("550e8400-e29b-41d4-a716-446655440000");
 * ```
 */
export function createUserId(value: string): UserId {
  if (!isUserId(value)) {
    throw new Error(`Invalid UserId: ${value}. Expected UUID format.`)
  }
  return value
}

/**
 * Create a validated Email from a string.
 *
 * @param value - An email string to validate
 * @returns The branded Email
 * @throws Error if the value is not a valid email format
 */
export function createEmail(value: string): Email {
  if (!isEmail(value)) {
    throw new Error(`Invalid Email: ${value}. Expected email format.`)
  }
  return value
}

/** Validate untrusted route or form input before branding it as a job ID. */
export function createJobId(value: string): JobId {
  if (!isJobId(value)) {
    throw new Error(
      "Invalid JobId: expected 1-128 letters, numbers, dots, underscores, colons, or hyphens.",
    )
  }
  return value
}

/** Validate untrusted input before branding it as an artifact ID. */
export function createArtifactId(value: string): ArtifactId {
  if (!isArtifactId(value)) {
    throw new Error("Invalid ArtifactId: expected a finite package identifier.")
  }
  return value
}

/** Validate untrusted retry identity before storing or sending it. */
export function createIdempotencyKey(value: string): IdempotencyKey {
  if (!isIdempotencyKey(value)) {
    throw new Error(
      "Invalid IdempotencyKey: expected 1-128 reviewed identifier characters.",
    )
  }
  return value
}

// ============================================================================
// Unsafe Conversion (for API responses)
// ============================================================================

/**
 * Convert a string to UserId without validation.
 *
 * Use this only when you trust the source (e.g., API responses that have
 * already been validated by the backend). Prefer createUserId() for
 * user input or untrusted sources.
 *
 * @param value - The string to cast to UserId
 * @returns The branded UserId (unchecked)
 */
export function asUserId(value: string): UserId {
  return value as UserId
}

/**
 * Convert a string to Email without validation.
 *
 * Use this only when you trust the source (e.g., API responses).
 *
 * @param value - The string to cast to Email
 * @returns The branded Email (unchecked)
 */
export function asEmail(value: string): Email {
  return value as Email
}

/** Cast a generated, backend-validated response identity to ``JobId``. */
export function asJobId(value: string): JobId {
  return value as JobId
}

/** Cast a generated, backend-validated response identity to ``ArtifactId``. */
export function asArtifactId(value: string): ArtifactId {
  return value as ArtifactId
}

/** Cast a trusted locally generated retry identity to ``IdempotencyKey``. */
export function asIdempotencyKey(value: string): IdempotencyKey {
  return value as IdempotencyKey
}
