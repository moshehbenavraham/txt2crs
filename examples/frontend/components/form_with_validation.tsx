/**
 * EXAMPLE: Profile form with centralized Zod validation
 *
 * PATTERN: Validated form with type-safe submission
 * USE WHEN: A shadcn form must mirror a backend Pydantic request
 * TAGS: form, validation, zod, react-hook-form, components
 *
 * The schema and inferred type come from `src/lib/schemas/`; the component
 * does not duplicate field bounds or maintain a parallel interface.
 */

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
  type UserInformationFormData,
  userInformationSchema,
} from "@/lib/schemas"

interface ProfileFormProps {
  /** Values read from the current-user API response. */
  defaultValues: UserInformationFormData
  /** Receives only data that passed the shared Zod schema. */
  onSubmit: (data: UserInformationFormData) => void | Promise<void>
  /** Prevents duplicate submissions while the mutation is pending. */
  isSubmitting?: boolean
}

/**
 * Edit the current user's display name and email.
 *
 * @example
 * ```tsx
 * <ProfileForm
 *   defaultValues={{ full_name: user.full_name ?? "", email: user.email }}
 *   onSubmit={(data) => updateProfile.mutateAsync(data)}
 *   isSubmitting={updateProfile.isPending}
 * />
 * ```
 */
export function ProfileForm({
  defaultValues,
  onSubmit,
  isSubmitting = false,
}: ProfileFormProps) {
  const form = useForm<UserInformationFormData>({
    resolver: zodResolver(userInformationSchema),
    // Providing every controlled field avoids React's controlled/uncontrolled
    // warning and makes reset behavior deterministic.
    defaultValues: {
      full_name: defaultValues.full_name ?? "",
      email: defaultValues.email,
    },
  })

  const handleValidSubmit = async (data: UserInformationFormData) => {
    await onSubmit(data)
  }

  return (
    <Form {...form}>
      <form
        className="space-y-4"
        onSubmit={form.handleSubmit(handleValidSubmit)}
      >
        <FormField
          control={form.control}
          name="full_name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Full name</FormLabel>
              <FormControl>
                <Input
                  autoComplete="name"
                  disabled={isSubmitting}
                  placeholder="Ada Lovelace"
                  {...field}
                />
              </FormControl>
              <FormDescription>
                This name appears in your private course workspace.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input
                  autoComplete="email"
                  disabled={isSubmitting}
                  type="email"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button className="h-11 sm:h-9" disabled={isSubmitting} type="submit">
          {isSubmitting ? "Saving…" : "Save changes"}
        </Button>
      </form>
    </Form>
  )
}

// Reusable form checklist:
//
// 1. Put field schemas in `src/lib/schemas/` and mirror backend bounds.
// 2. Infer form data from Zod instead of declaring a second interface.
// 3. Supply defaults for every controlled field.
// 4. Render `FormMessage` beside its field for accessible validation feedback.
// 5. Disable submission while pending, but preserve the learner's typed input
//    when the request fails.

export default ProfileForm
