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
| Branded types | `src/lib/types/` (UserId, ItemId, Email) |
| Utilities | `src/utils.ts`, `src/lib/utils.ts` |
| UI library | `src/components/ui/` (shadcn/ui) |

## Adding a New Page

1. **Create file** in `src/routes/` matching URL structure
2. **Export route config** with `createFileRoute()`
3. **Use `useSuspenseQuery()`** for data fetching
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
# Backend must be running at http://localhost:8000
npm run generate-client
```

This reads from `http://localhost:8000/api/v1/openapi.json` and generates:
- `src/client/types.gen.ts` - TypeScript types
- `src/client/schemas.gen.ts` - Zod schemas
- `src/client/sdk.gen.ts` - API SDK functions

**WARNING**: Never edit files in `src/client/` manually.

## Data Fetching Pattern

Use TanStack Query with suspense:

```typescript
import { useSuspenseQuery } from "@tanstack/react-query"
import { ItemsService } from "@/client"

function ItemList() {
  const { data } = useSuspenseQuery({
    queryKey: ["items"],
    queryFn: () => ItemsService.readItems(),
  })

  return (
    <ul>
      {data.data.map((item) => (
        <li key={item.id}>{item.title}</li>
      ))}
    </ul>
  )
}
```

## Mutation Pattern

```typescript
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { ItemsService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"

function CreateItemForm() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: (data: ItemCreate) => ItemsService.createItem({ body: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["items"] })
      showSuccessToast("Item created successfully")
    },
    onError: (error) => {
      showErrorToast(error)
    },
  })

  // ...
}
```

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
| `item.ts` | Item CRUD operations |
| `index.ts` | Re-exports all schemas |

## Error Handling

Global auth errors (401, 403) are handled automatically in `src/main.tsx` via TanStack Query's `QueryCache` and `MutationCache` — they redirect to `/login`.

For component-level errors, use `useCustomToast`:

```typescript
import useCustomToast from "@/hooks/useCustomToast"

function MyComponent() {
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: (data) => ItemsService.createItem({ body: data }),
    onSuccess: () => {
      showSuccessToast("Item created successfully")
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
├── Admin/            # Admin-only components
├── Common/           # Shared across features
├── Items/            # Item feature components
├── Sidebar/          # Navigation components
├── UserSettings/     # User settings components
├── ui/               # shadcn/ui primitives (DO NOT EDIT DIRECTLY)
└── theme-provider.tsx
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

export const Route = createFileRoute("/_layout/items")({
  validateSearch: searchSchema,
})
```

## Protected Routes

Routes under `_layout/` require authentication:

```typescript
// src/routes/_layout.tsx handles auth check
// All routes in src/routes/_layout/ are protected
```

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

# Run specific test file
npx playwright test tests/items.spec.ts

# Run with UI mode
npx playwright test --ui

# Generate test report
npx playwright show-report
```

## Build Commands

```bash
npm run dev          # Development server (port 5181)
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
| `useCustomToast()` | Success/error toast notifications |
| `useCopyToClipboard()` | Copy text to clipboard |
| `useMobile()` | Mobile viewport detection |
| `useSaveToItems()` | Save content to items |

## Key Patterns

1. **Always** use TanStack Query for server state
2. **Always** use Zod for form validation
3. **Never** edit files in `src/client/`
4. **Prefer** shadcn/ui components over custom implementations
5. **Use** the `@/` path alias for imports
