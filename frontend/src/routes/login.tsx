import { zodResolver } from "@hookform/resolvers/zod"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
} from "@tanstack/react-router"
import { useForm } from "react-hook-form"

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
import { PasswordInput } from "@/components/ui/password-input"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"
import { buildPageTitle } from "@/lib/branding"
import { readCoursePromptDraft } from "@/lib/course-draft"
import { publicSignupVisible } from "@/lib/public-config"
import { type LoginFormData, loginSchema } from "@/lib/schemas"

export const Route = createFileRoute("/login")({
  component: Login,
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
        title: buildPageTitle("Log in"),
      },
    ],
  }),
})

function Login() {
  const { loginMutation } = useAuth()
  const hasSavedPrompt = readCoursePromptDraft() !== null
  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
    },
  })

  const onSubmit = (data: LoginFormData) => {
    if (loginMutation.isPending) return
    loginMutation.mutate(data)
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
              Welcome back
            </h1>
            <p className="font-body text-[15px] text-muted-foreground">
              Sign in to continue to your learning studio
            </p>
            {hasSavedPrompt ? (
              <p className="text-body-sm text-primary">
                Your saved course topic will be ready after sign in.
              </p>
            ) : null}
          </div>

          {/* Form fields */}
          <div className="grid gap-5">
            <FormField
              control={form.control}
              name="username"
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
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <div className="flex items-center">
                    <FormLabel>Password</FormLabel>
                    <RouterLink
                      to="/recover-password"
                      className={`
                        ml-auto font-body text-[13px] text-muted-foreground
                        transition-colors duration-200
                        hover:text-primary
                      `}
                    >
                      Forgot password?
                    </RouterLink>
                  </div>
                  <FormControl>
                    <PasswordInput
                      data-testid="password-input"
                      placeholder="Password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />

            <LoadingButton
              type="submit"
              loading={loginMutation.isPending}
              className="mt-2"
            >
              Sign In
            </LoadingButton>
          </div>

          {/* Configured access guidance */}
          <div className="text-center font-body text-[14px] text-muted-foreground">
            {publicSignupVisible ? (
              <>
                Don&apos;t have an account?{" "}
                <RouterLink
                  to="/signup"
                  className={`
                    font-medium text-foreground
                    transition-colors duration-200
                    hover:text-primary
                  `}
                >
                  Create account
                </RouterLink>
              </>
            ) : (
              <>
                Need access?{" "}
                <RouterLink
                  to="/signup"
                  className={`
                    font-medium text-foreground
                    transition-colors duration-200
                    hover:text-primary
                  `}
                >
                  View account access
                </RouterLink>
              </>
            )}
          </div>
        </form>
      </Form>
    </AuthLayout>
  )
}
