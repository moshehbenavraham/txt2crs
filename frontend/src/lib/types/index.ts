/**
 * Type Definitions
 *
 * This module exports all custom type definitions used throughout the application.
 *
 * @module types
 *
 * @example
 * ```typescript
 * import { UserId, ItemId, createUserId, asItemId } from "@/lib/types";
 *
 * // With validation (user input)
 * const userId = createUserId(userInput);
 *
 * // Without validation (trusted API response)
 * const itemId = asItemId(apiResponse.id);
 * ```
 */

export {
  asEmail,
  asItemId,
  // Unsafe casts (for trusted sources like API responses)
  asUserId,
  createEmail,
  createItemId,
  // Factory functions (with validation)
  createUserId,
  type Email,
  type ItemId,
  isEmail,
  isItemId,
  // Type guards
  isUserId,
  isValidUuid,
  // Types
  type UserId,
} from "./branded"
