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
// Course Job Fields
// =============================================================================

/** Backend ``PromptText``: a short topic or course instruction. */
export const coursePromptField = z
  .string()
  .trim()
  .min(3, { message: "Describe the course in at least 3 characters" })
  .max(10_000, { message: "Keep the course topic under 10,000 characters" })

/** Backend ``PastedText`` after its whitespace-stripping request boundary. */
export const courseSourceTextField = z
  .string()
  .trim()
  .min(1, { message: "Paste some source text" })
  .max(200_000, { message: "Pasted text must be at most 200,000 characters" })

/**
 * Shape-only HTTPS validation mirrored from ``_HttpsJobInput``.
 *
 * Host safety, redirects, DNS resolution, and YouTube routing remain inside
 * the txt2crs package. The browser only rejects syntax the shell rejects.
 */
export const courseSourceUrlField = z
  .string()
  .trim()
  .min(9, { message: "Enter a complete HTTPS URL" })
  .max(2_048, { message: "The URL must be at most 2,048 characters" })
  .superRefine((value, refinementContext) => {
    let parsedUrl: URL
    try {
      parsedUrl = new URL(value)
    } catch {
      refinementContext.addIssue({
        code: "custom",
        message: "Enter a valid absolute HTTPS URL",
      })
      return
    }

    if (
      parsedUrl.protocol !== "https:" ||
      !parsedUrl.hostname ||
      parsedUrl.username ||
      parsedUrl.password ||
      parsedUrl.hash
    ) {
      refinementContext.addIssue({
        code: "custom",
        message: "Use HTTPS without credentials or a fragment",
      })
    }
  })

/** Optional learner audience, represented as an empty form field before submit. */
export const courseAudienceField = z
  .string()
  .trim()
  .max(500, { message: "Audience must be at most 500 characters" })

/** Optional prior-knowledge description. */
export const coursePriorKnowledgeField = z.string().trim().max(2_000, {
  message: "Prior knowledge must be at most 2,000 characters",
})

/** One bounded learner-selected objective. */
export const courseLearningGoalField = z
  .string()
  .trim()
  .min(3, { message: "Learning goals need at least 3 characters" })
  .max(500, { message: "Each learning goal must be at most 500 characters" })

/** Reviewed depth options from the generated ``JobLearningLevel`` contract. */
export const courseLearningLevelField = z.enum([
  "auto",
  "beginner",
  "intermediate",
  "advanced",
  "mixed",
])

/** Privacy-minimized age context from the generated shell contract. */
export const courseLearnerAgeGroupField = z.enum([
  "minor",
  "adult",
  "not_provided",
])

/** The backend accepts the literal boolean ``true`` and no truthy substitute. */
export const courseConsentField = z.literal(true, {
  error: "Allow AI and research processing to create the course",
})

export const MAXIMUM_COURSE_UPLOAD_BYTES = 20_971_520

const reviewedCourseUploadTypes = {
  ".pdf": "application/pdf",
  ".docx":
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ".pptx":
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
} as const

/** Validate local upload facts only; document parsing remains server-owned. */
export const courseSourceFileField = z
  .custom<File>(
    (value) => typeof File !== "undefined" && value instanceof File,
    { message: "Choose a PDF, DOCX, or PPTX file" },
  )
  .superRefine((file, refinementContext) => {
    if (file.size === 0) {
      refinementContext.addIssue({
        code: "custom",
        message: "The selected file is empty",
      })
    }
    if (file.size > MAXIMUM_COURSE_UPLOAD_BYTES) {
      refinementContext.addIssue({
        code: "custom",
        message: "The selected file must be 20 MB or smaller",
      })
    }
    if (
      file.name.length > 255 ||
      file.name !== file.name.trim() ||
      file.name === "." ||
      file.name === ".." ||
      file.name.includes("/") ||
      file.name.includes("\\") ||
      [...file.name].some((character) => {
        const codePoint = character.codePointAt(0) ?? 0
        return codePoint < 32 || codePoint === 127
      })
    ) {
      refinementContext.addIssue({
        code: "custom",
        message: "The file name is not supported",
      })
      return
    }

    const extensionIndex = file.name.lastIndexOf(".")
    const extension =
      extensionIndex >= 0 ? file.name.slice(extensionIndex).toLowerCase() : ""
    const expectedMediaType =
      reviewedCourseUploadTypes[
        extension as keyof typeof reviewedCourseUploadTypes
      ]
    if (!expectedMediaType || file.type !== expectedMediaType) {
      refinementContext.addIssue({
        code: "custom",
        message: "Choose a PDF, DOCX, or PPTX file with the matching file type",
      })
    }
  })

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
