/**
 * Branded Types for Domain Concepts
 *
 * Branded types (also called "nominal types" or "opaque types") provide compile-time
 * type safety for primitive values that have semantic meaning in the domain.
 *
 * Without branded types, it's easy to accidentally pass a UserId where an ItemId
 * is expected, since both are just strings at the type level. Branded types prevent
 * this class of bug by making these types incompatible.
 *
 * @example
 * ```typescript
 * function getItem(itemId: ItemId): Item { ... }
 *
 * const userId: UserId = createUserId("user-123");
 * const itemId: ItemId = createItemId("item-456");
 *
 * getItem(itemId);  // OK
 * getItem(userId);  // TypeScript error: UserId is not assignable to ItemId
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
// Item Domain Types
// ============================================================================

/**
 * Branded type for Item IDs.
 *
 * Item IDs are UUIDs represented as strings. This type ensures that
 * item IDs cannot be accidentally used where user IDs are expected.
 */
export type ItemId = Brand<string, "ItemId">

// ============================================================================
// Type Guards
// ============================================================================

/** UUID v4 regex pattern for validation */
const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

/** Email regex pattern (simplified, RFC 5322 compliant subset) */
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

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
 * Type guard for ItemId values.
 *
 * @param value - The string to validate
 * @returns True if the string is a valid ItemId (UUID format)
 */
export function isItemId(value: string): value is ItemId {
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
 * Create a validated ItemId from a string.
 *
 * @param value - A UUID string to convert to ItemId
 * @returns The branded ItemId
 * @throws Error if the value is not a valid UUID
 */
export function createItemId(value: string): ItemId {
  if (!isItemId(value)) {
    throw new Error(`Invalid ItemId: ${value}. Expected UUID format.`)
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
 * Convert a string to ItemId without validation.
 *
 * Use this only when you trust the source (e.g., API responses).
 *
 * @param value - The string to cast to ItemId
 * @returns The branded ItemId (unchecked)
 */
export function asItemId(value: string): ItemId {
  return value as ItemId
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
