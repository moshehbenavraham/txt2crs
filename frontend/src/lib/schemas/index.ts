/**
 * Centralized Zod validation schemas.
 *
 * This module provides type-safe form validation schemas that mirror
 * backend Pydantic models exactly. Use these schemas with React Hook Form
 * and zodResolver for consistent validation across the application.
 *
 * @module lib/schemas
 *
 * @example
 * // Import specific schemas
 * import { loginSchema, type LoginFormData } from "@/lib/schemas"
 *
 * const form = useForm<LoginFormData>({
 *   resolver: zodResolver(loginSchema),
 * })
 *
 * @example
 * // Import field schemas for custom compositions
 * import { emailField, passwordField } from "@/lib/schemas"
 *
 * const customSchema = z.object({
 *   email: emailField,
 *   password: passwordField,
 *   customField: z.string(),
 * })
 */

// =============================================================================
// Field Schemas (Building Blocks)
// =============================================================================

export {
  confirmPasswordField,
  confirmPasswordFieldOptional,
  courseAudienceField,
  courseConsentField,
  courseLearnerAgeGroupField,
  courseLearningGoalField,
  courseLearningLevelField,
  coursePriorKnowledgeField,
  coursePromptField,
  courseSourceFileField,
  courseSourceTextField,
  courseSourceUrlField,
  // Email fields
  emailField,
  emailFieldOptional,
  // User fields
  fullNameField,
  fullNameFieldRequired,
  fullNameFieldShort,
  isActiveField,
  isActiveFieldOptional,
  isSuperuserField,
  isSuperuserFieldOptional,
  optionalPasswordConfirmationRefinement,
  // Validation helpers
  passwordConfirmationRefinement,
  // Password fields
  passwordField,
  passwordFieldOptional,
} from "./fields"

// =============================================================================
// Course Job Schemas
// =============================================================================

export {
  buildJobSubmissionPayload,
  type CourseIntakeFormValues,
  type CourseIntakeValues,
  type CourseSubmissionPayload,
  courseIntakeSchema,
  createDefaultCourseIntakeValues,
} from "./job"

// =============================================================================
// Authentication Schemas
// =============================================================================

export {
  type LoginFormData,
  loginSchema,
  type RecoverPasswordFormData,
  type ResetPasswordFormData,
  type ResetPasswordSearchParams,
  recoverPasswordSchema,
  resetPasswordSchema,
  resetPasswordSearchSchema,
  type SignupFormData,
  signupSchema,
} from "./auth"

// =============================================================================
// User Management Schemas
// =============================================================================

export {
  type AddUserFormData,
  addUserSchema,
  type ChangePasswordFormData,
  changePasswordSchema,
  type EditUserFormData,
  editUserSchema,
  type UserInformationFormData,
  userInformationSchema,
} from "./user"
