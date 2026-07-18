/**
 * User management form schemas.
 *
 * Composed from base field schemas in ./fields.ts
 *
 * @module lib/schemas/user
 */
import { z } from "zod"

import {
  confirmPasswordField,
  confirmPasswordFieldOptional,
  emailField,
  fullNameField,
  fullNameFieldShort,
  isActiveField,
  isActiveFieldOptional,
  isSuperuserField,
  isSuperuserFieldOptional,
  optionalPasswordConfirmationRefinement,
  passwordConfirmationRefinement,
  passwordField,
  passwordFieldOptional,
} from "./fields"

// =============================================================================
// Admin: Add User
// =============================================================================

/**
 * Admin add user form schema.
 * Used in: components/Admin/AddUser.tsx
 */
export const addUserSchema = z
  .object({
    email: emailField,
    full_name: fullNameField,
    password: passwordField,
    confirm_password: confirmPasswordField,
    is_superuser: isSuperuserField,
    is_active: isActiveField,
  })
  .refine(...passwordConfirmationRefinement("password", "confirm_password"))

export type AddUserFormData = z.infer<typeof addUserSchema>

// =============================================================================
// Admin: Edit User
// =============================================================================

/**
 * Admin edit user form schema.
 * Password is optional for updates.
 * Used in: components/Admin/EditUser.tsx
 */
export const editUserSchema = z
  .object({
    email: emailField,
    full_name: fullNameField,
    password: passwordFieldOptional,
    confirm_password: confirmPasswordFieldOptional,
    is_superuser: isSuperuserFieldOptional,
    is_active: isActiveFieldOptional,
  })
  .refine(
    ...optionalPasswordConfirmationRefinement("password", "confirm_password"),
  )

export type EditUserFormData = z.infer<typeof editUserSchema>

// =============================================================================
// User Settings: User Information
// =============================================================================

/**
 * User profile information update schema.
 * Used in: components/UserSettings/UserInformation.tsx
 */
export const userInformationSchema = z.object({
  full_name: fullNameFieldShort,
  email: emailField,
})

export type UserInformationFormData = z.infer<typeof userInformationSchema>

// =============================================================================
// User Settings: Change Password
// =============================================================================

/**
 * Change password form schema.
 * Requires current password verification.
 * Used in: components/UserSettings/ChangePassword.tsx
 */
export const changePasswordSchema = z
  .object({
    current_password: passwordField,
    new_password: passwordField,
    confirm_password: confirmPasswordField,
  })
  .refine(...passwordConfirmationRefinement("new_password", "confirm_password"))

export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>
