/**
 * Authentication form schemas.
 *
 * Composed from base field schemas in ./fields.ts
 *
 * @module lib/schemas/auth
 */
import { z } from "zod"

import {
  confirmPasswordField,
  emailField,
  fullNameFieldRequired,
  passwordConfirmationRefinement,
  passwordField,
} from "./fields"

// =============================================================================
// Login
// =============================================================================

/**
 * Login form schema.
 * Used in: routes/login.tsx
 */
export const loginSchema = z.object({
  username: emailField,
  password: passwordField,
})

export type LoginFormData = z.infer<typeof loginSchema>

// =============================================================================
// Signup / Registration
// =============================================================================

/**
 * Signup form schema.
 * Used in: routes/signup.tsx
 */
export const signupSchema = z
  .object({
    email: emailField,
    full_name: fullNameFieldRequired,
    password: passwordField,
    confirm_password: confirmPasswordField,
  })
  .refine(...passwordConfirmationRefinement("password", "confirm_password"))

export type SignupFormData = z.infer<typeof signupSchema>

// =============================================================================
// Password Recovery
// =============================================================================

/**
 * Password recovery initiation schema.
 * Used in: routes/recover-password.tsx
 */
export const recoverPasswordSchema = z.object({
  email: emailField,
})

export type RecoverPasswordFormData = z.infer<typeof recoverPasswordSchema>

// =============================================================================
// Password Reset
// =============================================================================

/**
 * Password reset URL token validation schema.
 * Used in: routes/reset-password.tsx (validateSearch)
 */
export const resetPasswordSearchSchema = z.object({
  token: z.string().min(1, { message: "Token is required" }),
})

export type ResetPasswordSearchParams = z.infer<
  typeof resetPasswordSearchSchema
>

/**
 * Password reset form schema.
 * Used in: routes/reset-password.tsx
 */
export const resetPasswordSchema = z
  .object({
    new_password: passwordField,
    confirm_password: confirmPasswordField,
  })
  .refine(...passwordConfirmationRefinement("new_password", "confirm_password"))

export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>
