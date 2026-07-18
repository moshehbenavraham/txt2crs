# Project frontend map

Use this reference as the starting map, then verify it against the current worktree. It reflects
the repository inspected in July 2026; `package.json`, source, and rendered behavior are
authoritative when they differ.

## Table of contents

- Stack and entry points
- Current visual language
- Route and component surfaces
- Protected and generated areas
- Behavior contracts
- Documentation drift
- High-leverage inspection targets
- Useful audit commands

## Stack and entry points

- Runtime: React 19 SPA built with Vite and strict TypeScript.
- Routing: TanStack Router with generated file routes and automatic route code splitting.
- Server state: TanStack Query, including suspense queries on data pages.
- Styling: Tailwind CSS 4 through `@tailwindcss/vite`; global tokens in
  `frontend/src/index.css`.
- UI: shadcn configuration in `frontend/components.json`, Radix primitives, CVA variants,
  Lucide icons, and Sonner toasts.
- Forms: React Hook Form plus centralized Zod schemas.
- Themes: custom provider in `frontend/src/components/theme-provider.tsx`; `main.tsx` supplies
  `defaultTheme="system"`.
- Fonts: Playfair Display, Outfit, and JetBrains Mono loaded from Google Fonts in
  `frontend/index.html`.
- Browser tests: Playwright in `frontend/tests/`; unit tests use Vitest.

Always inspect the installed versions in `frontend/package.json` before adding packages or using a
new library API.

## Current visual language

The existing system calls itself **Refined Editorial Luxury**, applied to the product as an
*editorial workspace index* (canonical description: `docs/dashboard-design.md`):

- warm cream and charcoal foundations;
- deep forest green primary and champagne-gold accent;
- OKLCH light/dark tokens with three surface levels;
- Playfair Display for display type, Outfit for UI/body, JetBrains Mono for technical values;
- large rounded corners, restrained borders, layered shadows, and occasional mesh/noise;
- semantic motion role tokens (`--motion-duration-*`, easing curves) with four live keyframes
  (`fadeInUp`, `luxuryShimmer`, `riseIn`, `rowHighlight`) and one scoped Dashboard→Items view
  transition;
- a two-panel atmospheric auth layout;
- a collapsible application sidebar, sticky command strip, and centered content shell;
- an editorial workspace-index dashboard: numbered library sections, exact counts, and role-aware
  actions.

Treat this as an existing direction to evaluate, not an immutable house style. Preserve it when it
fits the product brief; evolve or replace it coherently when the user requests a new direction.
Avoid mixing a new visual language into a few routes while leaving the shell and states behind.

## Route and component surfaces

### Shells

- `frontend/src/main.tsx`: providers, theme default, global query errors.
- `frontend/src/routes/__root.tsx`: root outlet, errors, not-found, devtools.
- `frontend/src/routes/_layout.tsx`: protected shell — sticky command strip (sidebar trigger,
  compact brand mark below `md`, section label), sidebar, content width, and shell
  `view-transition-name`s. No footer and no outlet entrance animation.
- `frontend/src/components/Common/AuthLayout.tsx`: public auth shell.
- `frontend/src/components/Sidebar/`: navigation and user controls.

### Public flow

- `frontend/src/routes/login.tsx`
- `frontend/src/routes/signup.tsx`
- `frontend/src/routes/recover-password.tsx`
- `frontend/src/routes/reset-password.tsx`

Treat these as one visual and writing system. Validate the full flow rather than polishing only
the first page.

### Protected product screens

- `frontend/src/routes/_layout/index.tsx`: workspace-overview dashboard composed from
  `frontend/src/components/Dashboard/` (numbered library index, preview, empty/error states,
  role-aware actions).
- `frontend/src/routes/_layout/items.tsx`: filter, add action, suspense state, empty state,
  TanStack table.
- `frontend/src/routes/_layout/admin.tsx`: permission-gated user table and create action.
- `frontend/src/routes/_layout/settings.tsx`: tabbed account settings and destructive flow.
- `frontend/src/routes/_layout/forbidden.tsx`: permission failure.

### Shared patterns

- `frontend/src/components/Common/PageHeader.tsx`: shared page identity (eyebrow, `h1`,
  description, wrapping actions) used by all product routes.
- `frontend/src/components/Common/DataTable.tsx`: dense tabular layout and pagination; optional
  `renderMobileRow` renders a feature-specific mobile record list from the same row model.
- `frontend/src/components/Pending/`: page-level skeleton states.
- `frontend/src/components/Items/`, `Admin/`, and `UserSettings/`: dialogs, forms, menus, rich
  cells, empty states, and destructive actions.
- `frontend/src/components/Common/ErrorComponent.tsx` and `NotFound.tsx`: exceptional states.
- `frontend/src/components/Common/Appearance.tsx`: theme selection with tested hooks.

## Protected and generated areas

- Never edit `frontend/src/client/`; regenerate it with `npm run generate-client`.
- Never edit `frontend/src/routeTree.gen.ts`; TanStack Router generates it.
- Project guidance marks `frontend/src/components/ui/` as primitives not to edit directly.
  Inspect them to understand available variants and states. Prefer global tokens, composition,
  feature-level wrappers, and shadcn CLI additions.
- Preserve existing brand SVGs in `frontend/public/assets/images/` unless the user explicitly asks
  for a brand/logo change.

## Behavior contracts

Visual work must preserve:

- auth protection and redirect behavior in `_layout.tsx`;
- global session invalidation and API error behavior in `main.tsx`;
- TanStack Query keys, suspense boundaries, and invalidation after mutations;
- centralized form schemas and payload shaping;
- branded IDs and safe API handling;
- accessible Radix dialog, menu, tabs, sheet, select, and tooltip behavior;
- form labels/messages and outcome-specific accessible names;
- Playwright hooks such as `email-input`, `password-input`, `theme-button`, and `user-menu`;
- existing text selectors used by E2E tests unless intentionally migrated with their tests.

Search tests before renaming UI copy:

```bash
rg -n "getByRole|getByText|getByTestId|toHaveURL" frontend/tests
```

## Documentation drift

`docs/dashboard-design.md` is the consolidated design system and design-intent document (it
replaced `docs/frontend-ui-design.md` and the dashboard upgrade plan in July 2026). It was
reconciled against source at that time, but inventory counts, package versions, and token values
can still drift. Use source and rendered UI as truth. If a visual-system change is implemented,
update the doc so it stays trustworthy.

## High-leverage inspection targets

Before a broad upgrade, inspect these together:

1. `frontend/src/index.css`
2. `frontend/index.html`
3. `frontend/src/routes/_layout.tsx`
4. `frontend/src/components/Common/AuthLayout.tsx`
5. `frontend/src/components/Sidebar/`
6. representative primitives in `frontend/src/components/ui/`
7. the target route and all of its feature components
8. pending, empty, error, success, disabled, and destructive states
9. `docs/dashboard-design.md`
10. relevant Playwright tests

The July 2026 dashboard upgrade already landed the opportunities this map previously listed: the
workspace-index dashboard, the shared responsive page header, mobile record lists for dense
tables, semantic reveal choreography, the global reduced-motion clamp, and design-doc
reconciliation. Do not redo them by default — derive new opportunities from the requested task and
fresh rendered evidence.

## Useful audit commands

Run from the repository root:

```bash
rg --files frontend/src -g '!frontend/src/client/**' -g '!frontend/src/routeTree.gen.ts'
rg -n "className=|@theme|--[a-z-]+:|animate-|transition-|duration-|rounded-|shadow-" \
  frontend/src -g '!frontend/src/client/**' -g '!frontend/src/routeTree.gen.ts'
rg -n "data-testid|getByRole|getByText|getByTestId" frontend/src frontend/tests \
  -g '!frontend/src/client/**'
rg -n "prefers-reduced-motion|animate-in|animate-out|data-\\[state" frontend/src
```
