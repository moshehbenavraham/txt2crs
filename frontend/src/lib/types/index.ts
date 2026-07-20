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
  type ArtifactId,
  asArtifactId,
  asEmail,
  asIdempotencyKey,
  asJobId,
  // Unsafe casts (for trusted sources like API responses)
  asUserId,
  createArtifactId,
  createEmail,
  createIdempotencyKey,
  createJobId,
  // Factory functions (with validation)
  createUserId,
  type Email,
  type IdempotencyKey,
  isArtifactId,
  isEmail,
  isIdempotencyKey,
  isJobId,
  // Type guards
  isUserId,
  isValidUuid,
  type JobId,
  // Types
  type UserId,
} from "./branded"
