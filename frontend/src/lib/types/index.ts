/**
 * Type Definitions
 *
 * This module exports all custom type definitions used throughout the application.
 *
 * @module types
 *
 * @example
 * ```typescript
 * import { UserId, Email, createUserId, asEmail } from "@/lib/types";
 *
 * // With validation (user input)
 * const userId = createUserId(userInput);
 *
 * // Without validation (trusted API response)
 * const email = asEmail(apiResponse.email);
 * ```
 */

export {
  asEmail,
  // Unsafe casts (for trusted sources like API responses)
  asUserId,
  createEmail,
  // Factory functions (with validation)
  createUserId,
  type Email,
  isEmail,
  // Type guards
  isUserId,
  isValidUuid,
  // Types
  type UserId,
} from "./branded"
