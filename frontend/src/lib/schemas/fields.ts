/**
 * Reusable Zod field schemas.
 *
 * These schemas mirror backend Pydantic validation rules exactly.
 * See: backend/app/models.py for source of truth.
 *
 * @module lib/schemas/fields
 */
import { z } from "zod"

// =============================================================================
// Email Fields
// =============================================================================

/**
 * Standard email field validation.
 * Backend: EmailStr with max_length=255
 */
export const emailField = z
  .string()
  .min(1, { message: "Email is required" })
  .max(255, { message: "Email must be at most 255 characters" })
  .email({ message: "Invalid email address" })

/**
 * Optional email field for update forms.
 */
export const emailFieldOptional = z
  .string()
  .max(255, { message: "Email must be at most 255 characters" })
  .email({ message: "Invalid email address" })
  .optional()
  .or(z.literal(""))

// =============================================================================
// Password Fields
// =============================================================================

/**
 * Standard password field validation.
 * Backend: min_length=8, max_length=128
 */
export const passwordField = z
  .string()
  .min(1, { message: "Password is required" })
  .min(8, { message: "Password must be at least 8 characters" })
  .max(128, { message: "Password must be at most 128 characters" })

/**
 * Password confirmation field (required).
 * Used with passwordConfirmationRefinement for cross-field validation.
 */
export const confirmPasswordField = z
  .string()
  .min(1, { message: "Password confirmation is required" })

/**
 * Optional password field for update forms.
 * Backend: optional, but if provided must meet min/max constraints.
 */
export const passwordFieldOptional = z
  .string()
  .min(8, { message: "Password must be at least 8 characters" })
  .max(128, { message: "Password must be at most 128 characters" })
  .optional()
  .or(z.literal(""))

/**
 * Optional password confirmation for update forms.
 */
export const confirmPasswordFieldOptional = z
  .string()
  .optional()
  .or(z.literal(""))

// =============================================================================
// User Fields
// =============================================================================

/**
 * Full name field validation.
 * Backend: optional, max_length=255
 */
export const fullNameField = z
  .string()
  .max(255, { message: "Full name must be at most 255 characters" })
  .optional()
  .or(z.literal(""))

/**
 * Full name field (required) for signup.
 * Backend allows optional, but signup form requires it.
 */
export const fullNameFieldRequired = z
  .string()
  .min(1, { message: "Full Name is required" })
  .max(255, { message: "Full name must be at most 255 characters" })

/**
 * Full name field with shorter limit for display purposes.
 * Used in user settings forms.
 */
export const fullNameFieldShort = z
  .string()
  .max(30, { message: "Full name must be at most 30 characters" })
  .optional()
  .or(z.literal(""))

/**
 * Admin boolean flags.
 */
export const isSuperuserField = z.boolean()
export const isActiveField = z.boolean()
export const isSuperuserFieldOptional = z.boolean().optional()
export const isActiveFieldOptional = z.boolean().optional()

// =============================================================================
// Item Fields
// =============================================================================

/**
 * Item title field validation.
 * Backend: min_length=1, max_length=255
 */
export const itemTitleField = z
  .string()
  .min(1, { message: "Title is required" })
  .max(255, { message: "Title must be at most 255 characters" })

/**
 * Item description field validation.
 * Backend: optional, max_length=255
 */
export const itemDescriptionField = z
  .string()
  .max(255, { message: "Description must be at most 255 characters" })
  .optional()
  .or(z.literal(""))

/**
 * Item content field validation.
 * Backend: optional, TEXT type (no length limit in DB)
 */
export const itemContentField = z.string().optional().or(z.literal(""))

/**
 * Item content type field.
 * Backend: Literal["general"]
 */
export const itemContentTypeField = z.enum(["general", "all"]).default("all")

/**
 * Item source URL field.
 * Backend: optional, max_length=2048
 */
export const itemSourceUrlField = z
  .string()
  .max(2048, { message: "Source URL must be at most 2048 characters" })
  .url({ message: "Invalid URL format" })
  .optional()
  .or(z.literal(""))

// =============================================================================
// Validation Helpers
// =============================================================================

/**
 * Password confirmation refinement for cross-field validation.
 * Use with .refine() on schemas that have password and confirm_password fields.
 *
 * @example
 * const schema = z.object({
 *   password: passwordField,
 *   confirm_password: confirmPasswordField,
 * }).refine(...passwordConfirmationRefinement("password", "confirm_password"))
 */
export const passwordConfirmationRefinement = (
  passwordKey: string,
  confirmKey: string,
): [
  (data: Record<string, unknown>) => boolean,
  { message: string; path: string[] },
] => [
  (data) => data[passwordKey] === data[confirmKey],
  {
    message: "The passwords don't match",
    path: [confirmKey],
  },
]

/**
 * Optional password confirmation refinement.
 * Only validates if password field is provided.
 */
export const optionalPasswordConfirmationRefinement = (
  passwordKey: string,
  confirmKey: string,
): [
  (data: Record<string, unknown>) => boolean,
  { message: string; path: string[] },
] => [
  (data) => {
    const password = data[passwordKey]
    const confirm = data[confirmKey]
    // If no password provided, skip validation
    if (!password || password === "") return true
    return password === confirm
  },
  {
    message: "The passwords don't match",
    path: [confirmKey],
  },
]
