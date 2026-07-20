import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation } from "@tanstack/react-query"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
} from "@tanstack/react-router"
import { useForm } from "react-hook-form"

import { LoginService } from "@/client"
import { AuthLayout } from "@/components/Common/AuthLayout"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import { isLoggedIn } from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { buildPageTitle } from "@/lib/branding"
import {
  type RecoverPasswordFormData,
  recoverPasswordSchema,
} from "@/lib/schemas"
import { handleError } from "@/utils"

export const Route = createFileRoute("/recover-password")({
  component: RecoverPassword,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/create",
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: buildPageTitle("Recover password"),
      },
    ],
  }),
})

function RecoverPassword() {
  const form = useForm<RecoverPasswordFormData>({
    resolver: zodResolver(recoverPasswordSchema),
    defaultValues: {
      email: "",
    },
  })
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const recoverPassword = async (data: RecoverPasswordFormData) => {
    await LoginService.recoverPassword({
      body: { email: data.email },
    })
  }

  const mutation = useMutation({
    mutationFn: recoverPassword,
    onSuccess: () => {
      showSuccessToast("Password recovery email sent successfully")
      form.reset()
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = async (data: RecoverPasswordFormData) => {
    if (mutation.isPending) return
    mutation.mutate(data)
  }

  return (
    <AuthLayout>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-8"
        >
          {/* Header with display typography */}
          <div className="flex flex-col items-center gap-3 text-center">
            <h1 className="font-display text-[28px] font-semibold tracking-tight text-foreground">
              Forgot password?
            </h1>
            <p className="font-body text-[15px] text-muted-foreground max-w-[280px]">
              Enter your email and we'll send you a link to reset your password
            </p>
          </div>

          {/* Form fields */}
          <div className="grid gap-5">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      data-testid="email-input"
                      placeholder="user@example.com"
                      type="email"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <LoadingButton
              type="submit"
              className="w-full mt-2"
              loading={mutation.isPending}
            >
              Send Reset Link
            </LoadingButton>
          </div>

          {/* Footer link */}
          <div className="text-center font-body text-[14px] text-muted-foreground">
            Remember your password?{" "}
            <RouterLink
              to="/login"
              className={`
                font-medium text-foreground
                transition-colors duration-200
                hover:text-primary
              `}
            >
              Sign in
            </RouterLink>
          </div>
        </form>
      </Form>
    </AuthLayout>
  )
}
