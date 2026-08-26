# Frontend AGENTS.md

## Quick Reference

| Purpose | Location |
|---------|----------|
| Entry point | `src/main.tsx` |
| Routes | `src/routes/` (file-based) |
| API client | `src/client/` (auto-generated, **DO NOT EDIT**) |
| Components | `src/components/` |
| Hooks | `src/hooks/` |
| Zod schemas | `src/lib/schemas/` (centralized validation) |
| Branded types | `src/lib/types/` (UserId, JobId, IdempotencyKey, Email) |
| Utilities | `src/utils.ts`, `src/lib/utils.ts` |
| UI library | `src/components/ui/` (shadcn/ui) |

## Adding a New Page

1. **Create file** in `src/routes/` matching URL structure
2. **Export route config** with `createFileRoute()`
3. **Use TanStack Query** for server state; choose Suspense or explicit states
   to match the owning route
4. **Add to navigation** in `src/components/Sidebar/`

```typescript
// src/routes/_layout/my-page.tsx
import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/my-page")({
  component: MyPage,
})

function MyPage() {
  return <div>My Page Content</div>
}
```

## API Client Regeneration

When backend API changes, regenerate the client:

```bash
# Backend must be running at http://localhost:8016
npm run generate-client
```

This reads from `http://localhost:8016/api/v1/openapi.json` and generates:
- `src/client/types.gen.ts` - TypeScript types
- `src/client/schemas.gen.ts` - Zod schemas
- `src/client/sdk.gen.ts` - API SDK functions

**WARNING**: Never edit files in `src/client/` manually.

## Data Fetching Pattern

Use the reviewed job query options for course progress. They own the generated
client call, exhaustive status policy, visibility cadence, transient backoff,
terminal stop, and revision guard:

```typescript
import { useJobProgressQuery } from "@/components/CourseProgress/queries"
import type { JobId } from "@/lib/types"

function JobStatus({ jobId }: { jobId: JobId }) {
  const jobQuery = useJobProgressQuery(jobId)

  if (!jobQuery.data) return <p>Loading course progress...</p>
  return <p>{jobQuery.data.progress.message}</p>
}
```

## Mutation Pattern

Course intake must use the existing submission hook. It already owns secure
idempotency-key lifecycle, exact failed retries, JSON/upload delegation,
single-flight protection, safe Problem Details, and typed job navigation:

```typescript
import { useCourseSubmission } from "@/hooks/useCourseSubmission"
import type { CourseIntakeValues } from "@/lib/schemas"

function CourseSubmissionForm() {
  const { submitCourse, isSubmitting } = useCourseSubmission()
  const onValidSubmit = (values: CourseIntakeValues) => submitCourse(values)
  // Pass onValidSubmit and isSubmitting to the form composition.
}
```

Do not call `crypto.randomUUID()` in a course form or persist an idempotency
key. A changed canonical draft and an exact failed retry intentionally have
different key-lifecycle rules.

## Form Handling Pattern

Use React Hook Form with centralized Zod schemas from `src/lib/schemas/`:

```typescript
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { loginSchema, type LoginFormData } from "@/lib/schemas"

function LoginForm() {
  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: "", password: "" },
  })

  const onSubmit = (data: LoginFormData) => {
    // Handle submission
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  )
}
```

**Schema files** in `src/lib/schemas/`:
| File | Purpose |
|------|---------|
| `fields.ts` | Reusable field schemas (email, password, etc.) |
| `auth.ts` | Login, signup, password reset |
| `user.ts` | User management (admin + settings) |
| `job.ts` | Strict five-mode course intake and generated payload shaping |
| `index.ts` | Re-exports all schemas |

Keep course-input bounds synchronized with backend Pydantic request models.
Inactive source fields must be removed rather than sent empty.

## Error Handling

Global auth errors (401, 403) are handled automatically in `src/main.tsx` via TanStack Query's `QueryCache` and `MutationCache`; they redirect to `/login`.

For component-level errors, use `useCustomToast`:

```typescript
import useCustomToast from "@/hooks/useCustomToast"

function MyComponent() {
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: ({ request, idempotencyKey }: SubmitCourseVariables) =>
      JobsService.submitJob({
        body: request,
        headers: { "Idempotency-Key": idempotencyKey },
      }),
    onSuccess: () => {
      showSuccessToast("Course request accepted")
    },
    onError: (error) => {
      showErrorToast(error)
    },
  })
}
```

## Component Organization

```
src/components/
|-- Admin/            # Admin-only components
|-- Common/           # Shared across features
|-- CourseIntake/     # Five-mode source and learning-intent workbench
|-- CourseProgress/   # Owner-scoped polling, presentation, and stage rail
|-- Landing/          # Public one-source-to-publications story
|-- Sidebar/          # Navigation components
|-- SystemSetup/      # Codex and research readiness/setup
|-- UserSettings/     # User settings components
|-- ui/               # shadcn/ui primitives (DO NOT EDIT DIRECTLY)
`-- theme-provider.tsx
```

## UI Components (shadcn/ui)

Use shadcn/ui components from `src/components/ui/`:

```typescript
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardHeader, CardContent } from "@/components/ui/card"

// Add new shadcn components via CLI:
// npx shadcn@latest add [component-name]
```

## Route Search Params

Validate search params with Zod:

```typescript
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"

const searchSchema = z.object({
  page: z.coerce.number().positive().default(1),
  limit: z.coerce.number().positive().max(100).default(20),
  search: z.string().optional(),
})

export const Route = createFileRoute("/_layout/my-page")({
  validateSearch: searchSchema,
})
```

## Protected Routes

Routes under `_layout/` require authentication:

```typescript
// src/routes/_layout.tsx handles auth check
// All routes in src/routes/_layout/ are protected
```

The public root is `/`. The protected learner entry is `/create`, and durable
progress lives at `/jobs/$jobId`. Validate dynamic IDs at the route boundary
and preserve identical recovery copy for missing and foreign-owned jobs.

## Public Signup Visibility

`VITE_ENABLE_PUBLIC_SIGNUP` is a non-secret, build-time display choice and
defaults true. The backend `ENABLE_PUBLIC_SIGNUP` check is authoritative.
Never infer authorization from frontend visibility or describe the setting as
a security boundary.

`VITE_HTML_PREVIEW_MAX_BYTES` is also non-secret and presentation-only. Keep
its strict positive-integer frontend parser, 5 MiB fallback, Docker/Compose
propagation, and backend-authoritative artifact limits synchronized.

## Styling

Use Tailwind CSS classes:

```tsx
<div className="flex items-center gap-4 p-4 bg-background rounded-lg shadow">
  <h1 className="text-2xl font-bold text-foreground">Title</h1>
</div>
```

## Testing

```bash
# E2E tests with Playwright
npx playwright test

# Provider-free complete and failed course journeys
npx playwright test --config playwright.jobs.config.ts
TXT2CRS_BROWSER_SCENARIO=failed \
  npx playwright test --config playwright.jobs.config.ts

# Run specific test file
npx playwright test tests/dashboard.spec.ts

# Run with UI mode
npx playwright test --ui

# Generate test report
npx playwright show-report
```

## Build Commands

```bash
npm run dev          # Development server (registered port 5196)
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # Lint with Biome
npm run typecheck    # TypeScript type check
npm run generate-client  # Regenerate API client
```

## Common Hooks

| Hook | Purpose |
|------|---------|
| `useAuth()` | Authentication state and actions |
| `useCourseSubmission()` | Canonical submit/retry and job navigation |
| `useCustomToast()` | Success/error toast notifications |
| `useCopyToClipboard()` | Copy text to clipboard |
| `useMobile()` | Mobile viewport detection |
| `usePrefersReducedMotion()` | Reduced-motion preference |

## Key Patterns

1. **Always** use TanStack Query for server state
2. **Always** use Zod for form validation
3. **Never** edit files in `src/client/`
4. **Prefer** shadcn/ui components over custom implementations
5. **Use** the `@/` path alias for imports
6. **Compose** course submission and progress boundaries; do not duplicate them
7. **Do not claim** retention, provider privacy, or compliance guarantees the
   product contract does not make
