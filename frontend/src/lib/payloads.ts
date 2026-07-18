import type { UpdatePassword, UserCreate } from "@/client"
import type { AddUserFormData, ChangePasswordFormData } from "@/lib/schemas"

export const mapAddUserFormToUserCreateRequest = (
  formData: AddUserFormData,
): UserCreate => {
  const { confirm_password: _confirmPassword, ...requestBody } = formData
  return requestBody
}

export const mapChangePasswordFormToUpdatePasswordRequest = (
  formData: ChangePasswordFormData,
): UpdatePassword => {
  const { confirm_password: _confirmPassword, ...requestBody } = formData
  return requestBody
}
