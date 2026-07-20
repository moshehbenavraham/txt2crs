# Dashboard Design System

> Single source of truth for the frontend's visual and interaction design.
> Consolidates the former `frontend-ui-design.md` and
> `ongoing-projects/dashboard-frontend-design-upgrade-plan.md` (both removed;
> see git history).
>
> **Direction**: Refined Editorial Luxury applied as an *editorial workspace
> index* -- expressive page identity joined to compact, honest operational
> surfaces.
> **Status**: Phase 04 learner-journey hierarchy is defined. The public
> landing, authenticated `/create`, and owner `/jobs/$jobId` surfaces use the
> generated course-job contract; result delivery follows in Session 02. The
> donor library and `/items` route remain retired. Legacy library blueprints
> below are history only and must not be implemented.
> Last updated: 2026-07-20

## Table of Contents

1. [Design Direction](#1-design-direction)
2. [Typography](#2-typography)
3. [Color & Theming](#3-color--theming)
4. [Spacing, Shape & Layout](#4-spacing-shape--layout)
5. [Shadow & Texture](#5-shadow--texture)
6. [Motion](#6-motion)
7. [Components](#7-components)
8. [Routes & Screen Blueprints](#8-routes--screen-blueprints)
9. [Data Contract](#9-data-contract)
10. [Responsive Design](#10-responsive-design)
11. [Accessibility](#11-accessibility)
12. [File & Contract Guardrails](#12-file--contract-guardrails)
13. [QA & Validation](#13-qa--validation)

---

## 1. Design Direction

Inspiration: high-end editorial design (Monocle, Kinfolk), luxury tech
(Apple, Porsche Digital), contemporary art galleries.

### Thesis

The authenticated interface is an editorial index joined to a precise
operations workspace: users need to understand and manage content, not admire
dashboard decoration. It avoids generic KPI-card grids, ornamental gradients,
glow-heavy actions, and indiscriminate pills. Display type establishes page
identity; a numbered index rail, compact rows, warm neutral surfaces, and
role-aware actions make the workspace feel organized and trustworthy.

Two other directions were considered and rejected: an *editorial gallery*
(too sparse for operational tables and administration) and an *operations
console* (discards brand equity; auth and product would feel unrelated).

### Core principles

1. **Confidence through restraint** -- luxury doesn't shout; every element
   earns its presence.
2. **Typography as architecture** -- type carries 80% of the personality;
   display/body contrast creates rhythm.
3. **Depth without clutter** -- layers, shadows, and subtle texture create
   dimensionality; never busy.
4. **Motion as choreography** -- animation feels inevitable, not decorative;
   orchestrated reveals over scattered micro-interactions.
5. **The detail is the design** -- borders, shadows, spacing; 1px matters.

### Load-bearing decisions

1. **Stable page identity.** The public root names the one-source-to-four-
   publications promise. Authenticated identity begins at `Create a course`;
   an email address is never a page title.
2. **Truthful product structure.** The public root names the four generated
   publications without inventing job counts, recency, or history. Intake and
   progress add operational structure only where the job API supplies it.
3. **Proximity groups default content.** Surface tone and keylines for
   structure; shadows reserved for overlays and true elevation.
4. **Expressive vs. operational type are separate.** The local display serif
   carries page identity and narrative sections, system sans carries controls
   and dense content, and system mono is reserved for IDs, counts, and
   technical values.
5. **Color has one job at a time.** Forest green = action, selection, active
   navigation. Gold = earned emphasis or a completed index state, never every
   decorative edge.
6. **Mobile transforms, it doesn't squeeze.** Page actions stack beneath
   identity; dense tables become feature-specific record lists, not
   horizontally scrolled desktop tables.
7. **Motion serves state and orientation.** No retired donor transition
   remains. New Phase 04 motion must preserve complete reduced-motion states
   and must not imply unsupported progress.

---

## 2. Typography

### Font stack

```css
--font-display: Georgia, "Times New Roman", serif; /* headlines and page identity */
--font-body: system-ui, "Segoe UI", sans-serif;    /* UI text and forms */
--font-mono: ui-monospace, Consolas, monospace;    /* code, IDs, counts */
```

The production stack is local/system-only. It makes first paint deterministic,
keeps the Nginx content-security policy closed to third-party styles/fonts,
and avoids a learner-network dependency.

### Scale

| Role | Font | Weight | Size | Tracking | Use |
|------|------|--------|------|----------|-----|
| Display XL | Georgia/system serif | 600 | 48px | -0.02em | Hero headlines |
| Display L | Georgia/system serif | 500 | 32px | -0.01em | Page titles |
| Display M | Georgia/system serif | 500 | 24px | -0.01em | Section headers |
| Heading | System sans | 600 | 18px | -0.01em | Card titles, nav items |
| Body | System sans | 400 | 15px | 0 | Primary text |
| Body Small | System sans | 400 | 13px | 0.01em | Secondary text |
| Caption | System sans | 500 | 11px | 0.05em | Labels, badges |
| Mono | System mono | 400 | 13px | 0 | Code, data values |

CSS variables in `frontend/src/index.css`: sizes (`--text-display-xl` 3rem ->
`--text-caption` 0.6875rem), line heights (`--leading-tight` 1.1 ->
`--leading-relaxed` 1.625), tracking (`--tracking-tighter` -0.02em ->
`--tracking-wider` 0.05em).

### Usage discipline

- One expressive `h1` per page; responsive size, stable line height.
- Display serif appears only where a section carries narrative weight; system
  sans semibold appears in operational panels.
- No emoji or decorative punctuation in page identity -- warmth comes from
  concise copy and the user's name.

---

## 3. Color & Theming

A warm neutral foundation with deep, confident accents: aged paper and dark
walnut, champagne gold and graphite, forest green and midnight blue.

### Light mode (`frontend/src/index.css`)

| Token | Value | Description |
|-------|-------|-------------|
| `--background` | `oklch(0.985 0.005 85)` | Warm off-white |
| `--background-elevated` | `oklch(0.99 0.003 85)` | Paper white |
| `--foreground` | `oklch(0.18 0.01 60)` | Rich charcoal |
| `--surface-1` | `oklch(0.975 0.006 85)` | Subtle cream |
| `--surface-2` | `oklch(0.965 0.008 85)` | Light parchment |
| `--surface-3` | `oklch(0.95 0.01 80)` | Warm gray |
| `--primary` | `oklch(0.35 0.08 160)` | **Deep forest green** |
| `--primary-hover` | `oklch(0.40 0.09 160)` | Lighter forest |
| `--primary-foreground` | `oklch(0.98 0.005 85)` | Cream white |
| `--accent` | `oklch(0.75 0.12 85)` | **Champagne gold** |
| `--accent-hover` | `oklch(0.70 0.14 85)` | Deeper gold |
| `--accent-muted` | `oklch(0.85 0.06 85)` | Soft gold |
| `--secondary` | `oklch(0.55 0.01 60)` | Graphite |
| `--muted` | `oklch(0.94 0.005 80)` | Light warm gray |
| `--muted-foreground` | `oklch(0.50 0.01 60)` | Medium gray |
| `--border` | `oklch(0.90 0.008 80)` | Subtle warm border |
| `--border-strong` | `oklch(0.82 0.01 75)` | Defined border |
| `--ring` | `oklch(0.35 0.08 160 / 0.3)` | Focus ring |
| `--success` | `oklch(0.55 0.15 155)` | Deep teal green |
| `--warning` | `oklch(0.70 0.15 70)` | Amber |
| `--destructive` | `oklch(0.50 0.18 25)` | Deep burgundy |
| `--info` | `oklch(0.50 0.10 250)` | Slate blue |

### Learner journey roles

Feature composition uses semantic roles rather than route-local raw colors:

| Role | Light | Dark | Use |
|------|-------|------|-----|
| `--publication` | Paper white | Warm charcoal paper | Course/review/test/key publication sheets |
| `--workbench` | Quiet parchment | Deep neutral workbench | Intake and progress grouping surfaces |
| `--stage-track` | Strong warm keyline | 22% light keyline | Inactive progress relationship |
| `--stage-active` | Forest | Luminous forest | Current server-derived stage |
| `--stage-complete` | Restrained gold | Luminous gold | Earned completed stage marker |

Publication and workbench foreground roles always carry normal text. Stage
color accompanies labels and server copy; it never communicates state alone.
Focus rings use an opaque forest role in both themes so they remain visible
against background, workbench, and publication surfaces.

### Dark mode

| Token | Value | Description |
|-------|-------|-------------|
| `--background` | `oklch(0.14 0.01 60)` | Deep charcoal |
| `--background-elevated` | `oklch(0.18 0.01 55)` | Elevated surface |
| `--foreground` | `oklch(0.92 0.01 85)` | Warm off-white |
| `--surface-1` | `oklch(0.17 0.01 60)` | Card surface |
| `--surface-2` | `oklch(0.20 0.01 55)` | Elevated card |
| `--surface-3` | `oklch(0.24 0.01 50)` | Highest elevation |
| `--primary` | `oklch(0.55 0.10 160)` | Brighter forest |
| `--primary-hover` | `oklch(0.60 0.11 160)` | Hover state |
| `--accent` | `oklch(0.78 0.14 85)` | Luminous gold |
| `--accent-hover` | `oklch(0.82 0.15 85)` | Brighter gold |
| `--accent-muted` | `oklch(0.65 0.08 80)` | Subdued gold |
| `--secondary` | `oklch(0.65 0.01 60)` | Light graphite |
| `--muted` | `oklch(0.22 0.01 55)` | Dark muted |
| `--muted-foreground` | `oklch(0.60 0.01 60)` | Muted text |
| `--border` | `oklch(1 0 0 / 0.08)` | Subtle light border |
| `--border-strong` | `oklch(1 0 0 / 0.15)` | Defined border |
| `--ring` | `oklch(0.55 0.10 160 / 0.4)` | Focus ring |
| `--success` | `oklch(0.65 0.15 155)` | Bright teal |
| `--warning` | `oklch(0.75 0.15 70)` | Bright amber |
| `--destructive` | `oklch(0.60 0.18 25)` | Bright burgundy |
| `--info` | `oklch(0.60 0.10 250)` | Bright slate |

### Chart colors

| Token | Light | Dark |
|-------|-------|------|
| `--chart-1` | `oklch(0.35 0.08 160)` forest | `oklch(0.55 0.10 160)` |
| `--chart-2` | `oklch(0.75 0.12 85)` gold | `oklch(0.78 0.14 85)` |
| `--chart-3` | `oklch(0.50 0.10 250)` slate | `oklch(0.60 0.10 250)` |
| `--chart-4` | `oklch(0.60 0.15 30)` terracotta | `oklch(0.65 0.15 30)` |
| `--chart-5` | `oklch(0.55 0.15 155)` teal | `oklch(0.65 0.15 155)` |

### Sidebar colors

| Token | Light | Dark |
|-------|-------|------|
| `--sidebar` | `oklch(0.975 0.006 85)` | `oklch(0.17 0.01 60)` |
| `--sidebar-foreground` | `oklch(0.18 0.01 60)` | `oklch(0.92 0.01 85)` |
| `--sidebar-primary` | `oklch(0.35 0.08 160)` | `oklch(0.55 0.10 160)` |
| `--sidebar-primary-foreground` | `oklch(0.98 0.005 85)` | `oklch(0.98 0.005 85)` |
| `--sidebar-accent` | `oklch(0.94 0.005 80)` | `oklch(0.22 0.01 55)` |
| `--sidebar-accent-foreground` | `oklch(0.18 0.01 60)` | `oklch(0.92 0.01 85)` |
| `--sidebar-border` | `oklch(0.90 0.008 80)` | `oklch(1 0 0 / 0.08)` |
| `--sidebar-ring` | `oklch(0.35 0.08 160 / 0.3)` | `oklch(0.55 0.10 160 / 0.4)` |

`--surface-selected` (primary at restrained alpha) marks the active
navigation item together with a forest index keyline.

### Usage discipline

- Background and border shifts for default grouping; shadow only for dialogs,
  dropdowns, sheets, and temporary elevation.
- Feature code uses semantic `success` / `warning` / `info` / `muted` roles,
  never raw status grays and greens.
- Status color is never the only signal -- status text always accompanies it.
- Light and dark are independent compositions with the same semantic
  hierarchy; validate both in every change.

### Theme behavior

`frontend/src/components/theme-provider.tsx` -- `"dark" | "light" | "system"`.
First-visit default is **`system`** (set in `frontend/src/main.tsx`);
explicit selection persists in localStorage under `vite-ui-theme`. The
provider applies a `light`/`dark` class to `document.documentElement` and
tracks `prefers-color-scheme` changes. Theme switching must not animate the
whole page or leave icons half-transitioned under reduced motion.

---

## 4. Spacing, Shape & Layout

### Spacing tokens

Base unit 4px: `--space-1` (4px) through `--space-20` (80px) on the standard
4/8/12/16/20/24/32/40/48/64/80 progression. Container widths: `--container-sm`
640px -> `--container-2xl` 1400px.

Shell-level layout roles (not route accidents):

```css
--space-page-inline: clamp(1.25rem, 3vw, 3rem); /* page gutter */
--space-section: clamp(2rem, 4vw, 3.5rem);      /* section rhythm */
--space-journey-section: clamp(3.5rem, 8vw, 7rem);
--width-reading: 44rem;
--width-workspace: 72rem;
--size-touch-target: 2.75rem;                   /* 44px */
```

### Border radius

| Token | Value | Applies to |
|-------|-------|-----------|
| `--radius-sm` | 8px | Controls |
| `--radius-md` | 12px | Data rows, compact surfaces |
| `--radius-lg` | 16px | Major workspace surfaces, overlays |
| `--radius-xl` | 20px | Largest containers |

Pills are reserved for compact status or taxonomy -- not navigation,
containers, or actions.

### Layout philosophy

Generous whitespace (space is luxury), asymmetric balance, hierarchy through
size and position, breathing room. Use proximity before adding a border or
container. Section rhythm is larger than internal component spacing. A
12-column grid appears only where content relationships require it. Mobile
gutters start at 20-24px and must work at 320px.

### Protected shell (`frontend/src/routes/_layout.tsx`)

```
+-----------------------------------------------------------------+
|  SIDEBAR (280px)  |  COMMAND STRIP (sticky, 56px)               |
|  Logo             |  [trigger] [brand mark <md] [section label] |
|  Navigation       |---------------------------------------------|
|  * Dashboard      |  CONTENT AREA                               |
|  * Items          |    max-width: max-w-6xl (shell role)        |
|  * ...              |    gutter: --space-page-inline              |
|  Settings         |                                             |
|  User             |  (no footer in the protected workspace;     |
|                   |   social links live on auth surfaces)       |
+-----------------------------------------------------------------+
```

- `SidebarInset` renders the single `main` landmark; route content uses a
  plain `div`.
- The command strip carries the sidebar trigger (44x44 on mobile), a compact
  brand mark below `md`, and the current section label, over
  `bg-background/80 backdrop-blur-sm`.
- Sidebar collapses to icons with immediate tooltips on desktop; on mobile it
  is a Radix sheet with focus containment that closes after route selection,
  with account and appearance controls reachable inside.
- Active navigation uses a quiet surface tint (`--surface-selected`) plus a
  forest index keyline -- no full-width pill; `aria-current` comes from router
  links.
- The persistent shell never animates during route changes; loading a
  protected route keeps the shell stable; forbidden and route-error states
  render within the content frame; auth invalidation keeps the existing
  global redirect.

### Auth layout (`frontend/src/components/Common/AuthLayout.tsx`)

Gradient mesh background with noise texture, 2-column grid (logo left, form
right) on desktop, single column on mobile, decorative accent border on the
logo panel, entrance animation.

### Common layout patterns

| Pattern | Classes / source | Use |
|---------|-----------------|-----|
| Form grid | `grid gap-4 sm:grid-cols-2` (or `-3`) | Form layouts |
| Form item | `grid gap-2` | Field wrapper |
| Page header | `Common/PageHeader.tsx` | See [Section 8](#shared-page-header) |
| Card layout | `flex flex-col gap-6` | Vertical content |
| Table wrapper | `relative w-full overflow-hidden rounded-2xl border` | Responsive tables |
| Button group | `flex w-fit items-stretch` | Grouped buttons |

---

## 5. Shadow & Texture

Layered shadows, defined in `frontend/src/index.css`:

| Token | Light (summary) | Dark (summary) |
|-------|-----------------|----------------|
| `--shadow-xs` | 1px blur @ 4% | 2px @ 20% |
| `--shadow-sm` | 2 layers to 4px | 8px @ 30% |
| `--shadow-md` | 3 layers to 16px | 16px @ 40% |
| `--shadow-lg` | 4 layers to 48px | 32px @ 50% |
| `--shadow-xl` | 4 layers to 96px | 64px @ 60% |
| `--shadow-accent` | forest-tinted CTA glow | brighter forest tint |

Reserved for overlays and truly elevated surfaces (see Section 3 discipline).

Background treatments: `.texture-noise` (SVG noise overlay at 3% opacity,
`mix-blend-mode: overlay`), `.bg-gradient-mesh` (layered radial gradients of
accent/primary/surface -- auth surfaces only), `.separator-elegant` (1px
gradient hairline).

---

## 6. Motion

### Philosophy

Every effect has a semantic role: orientation, hierarchy, continuity,
feedback, or attention. Dense reading and comparison regions stay still.
There is exactly one signature moment: the dashboard's library surface
continuing into the Items workspace.

### Motion role tokens

Durations are semantic roles, not literals. Legacy `--duration-*` names
remain as compatibility aliases.

```css
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
--ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
--ease-in-out-quart: cubic-bezier(0.76, 0, 0.24, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);

--motion-duration-feedback: 120ms;  /* press, selection */
--motion-duration-state: 180ms;     /* hover, small state changes */
--motion-duration-overlay: 260ms;   /* dialogs, menus, reveals */
--motion-duration-route: 320ms;     /* scoped route continuity */
--motion-distance-sm: 4px;
--motion-distance-md: 8px;
```

### Keyframes

Only keyframes with live consumers exist:

| Keyframe | Consumer |
|----------|----------|
| `fadeInUp` | Auth shell entrance (`AuthLayout`) |
| `luxuryShimmer` | `ui/skeleton` shimmer |
| `riseIn` | Dashboard section settle, capped at `--motion-distance-md` |
| `rowHighlight` | Brief emphasis on a newly created preview row |

### Semantic reveal groups

No outlet-level entrance replay and no `nth-child` stagger. The dashboard
settles in explicit reading order -- header, library status, then
preview/actions -- capped at three groups, inside
`prefers-reduced-motion: no-preference`:

```css
.reveal-group   { animation: riseIn var(--motion-duration-overlay) var(--ease-out-quart) both; }
.reveal-delay-1 { animation-delay: 0ms; }
.reveal-delay-2 { animation-delay: 70ms; }
.reveal-delay-3 { animation-delay: 140ms; }
```

Routine query refetches never replay entrances; content updates in place.

### Signature interaction: route continuity

Selecting "Open library" on the dashboard continues the library surface into
the Items workspace via TanStack Router's built-in `viewTransition` link
option -- no motion dependency. The dashboard preview and Items table share
`view-transition-name: library-surface`; the sidebar (`app-sidebar`) and
command strip (`command-strip`) claim their own names so the shell stays
fixed. Unsupported browsers navigate normally;
`usePrefersReducedMotion()` disables the transition in JavaScript. This is
the only route transition -- it must not become a global cross-fade.

### Supporting roles

| Interaction | Role | Layer |
|-------------|------|-------|
| Dashboard sections settle on first data load | Hierarchy | CSS, three semantic groups |
| Sidebar expand/collapse | Orientation | CSS transition, role tokens |
| Button press / selection | Feedback | CSS transform/color, 80-160ms |
| Dialog, menu, select, sheet | Continuity + focus context | Radix state classes + tokens |
| Item created/updated | Feedback + attention | Toast + brief `rowHighlight` |
| Loading -> content | Continuity | Geometry-matched skeleton, no large shift |
| Filter change / refetch | None | Content stays stable |

### Quiet regions

Table and record-list contents, long previews, metadata and IDs, settings
forms during typing/validation, destructive confirmation copy, legal content,
routine refetches.

### Motion state matrix

| State | Required behavior |
|-------|-------------------|
| First paint | Essential content visible and placed without waiting for animation |
| Pending | Honest status, stable skeleton geometry; indefinite work has status copy |
| Settled | No lingering `will-change`, blur, transform, or pointer-blocking layer |
| Hover | Enhancement only; no hover-exclusive information |
| Press | Immediate 80-160ms feedback without delaying the action |
| Focus | Stable visible ring; transforms must not clip or obscure it |
| Touch | Complete behavior, 44x44 practical targets, no hover dependency |
| Exit | Focus returns to a live trigger; disappearing UI cannot retain focus |
| Interruption | Rapid navigation/toggling resolves to the latest correct state |
| Error | Recovery action stays still and prominent |
| Reduced | Movement, zoom, shimmer, and route morphing disabled; content complete |

### Reduced motion

A project-wide safety clamp resolves every animation and transition -- custom
utilities, Radix state animations, `tw-animate-css`, shimmer loops, theme
icons, and view transitions -- instantly to the complete final state:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-delay: 0ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    transition-delay: 0ms !important;
    scroll-behavior: auto !important;
  }
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) { animation: none !important; }
}
```

Test Dialog, Dropdown Menu, Select, Sheet, Tooltip, theme selection, and
route navigation separately -- disabling the page entrance alone is not
sufficient coverage.

### Dependency policy

No `motion`/Motion for React, GSAP, smooth scrolling, canvas, or WebGL.
CSS + Radix data states + the router's View Transition integration cover all
current needs; a new motion runtime requires a separately justified
interaction requirement.

---

## 7. Components

### UI primitives (`frontend/src/components/ui/`, 25 components -- protected, see Section 12)

| Component | Highlights |
|-----------|-----------|
| **Button** | Variants: `default` (forest + accent shadow, hover lift), `secondary`, `outline`, `ghost`, `accent` (gold), `destructive` (burgundy), `link`. Sizes: `sm` h-9 -> `lg` h-13, plus `icon`/`icon-sm`/`icon-lg` (32-44px) |
| **Card** | `default`, `elevated` (hover lift), `feature` (gradient + accent top line), `interactive`, `muted` |
| **Input/Textarea** | h-12, rounded-xl, surface-1, primary focus ring, destructive invalid border, 200ms transitions |
| **Table** | Rounded-2xl container, surface-2 header, uppercase tracked header text, hover row highlight |
| **Badge** | `default`, `secondary`, `outline`, `destructive`, `success`, `warning`, `info`, `accent` |
| **Alert** | `default`, `destructive`, `success`, `warning`, `info`, `accent` |
| **Dialog** | Backdrop blur, display-type titles, `shadow-xl`, refined close button |
| **Skeleton** | `luxuryShimmer` gradient (2s, 200% background-size) |
| **Sonner** | Semantic colors, system sans, theme-aware |

shadcn/ui config (`frontend/components.json`): style `new-york`, base color
`neutral`, CSS variables on, Lucide icons.

### Common (`frontend/src/components/Common/`)

| Component | Description |
|-----------|-------------|
| `Logo` | Theme-aware; `full` / `icon` / `responsive` variants; optional link wrapper |
| `AuthLayout` | Gradient mesh + noise, entrance animation |
| `PageHeader` | Shared page identity -- see [Section 8](#shared-page-header) |
| `Footer` | Auth-surface footer with social links; never rendered in the protected shell |
| `Appearance` | Theme switcher (sidebar + standalone) |
| `DataTable` | TanStack Table with pagination; optional `renderMobileRow` renders a feature-specific record list below `md` from the same paginated row model |
| `ErrorComponent` | Error boundary display |
| `NotFound` | 404 page |

### Sidebar (`frontend/src/components/Sidebar/`)

`AppSidebar` (shell composition), `Main` (navigation with quiet active
treatment and router-driven `aria-current`), `User` (avatar + account
dropdown).

### Learner journey

The public landing, authenticated intake, and owner progress route form one
source-to-publications story. They use publication/workbench/stage roles from
`frontend/src/index.css`, generated `JobsService` contracts, and the same
editorial typography as the protected shell. The UI never renders provider
turns, internal checkpoints, local paths, or model controls.

### System setup (`frontend/src/components/SystemSetup/`, plus `Pending/`)

| Component | Purpose |
|-----------|---------|
| `ReadinessOverview` | One plain-language system verdict backed by the readiness API; never invents a score |
| `AuthenticationPanel` | Starts the device-auth flow, presents only the safe challenge link/code, copies the code, and explains the current state |
| `SystemChecklist` | Renders the API checks in a stable, numbered operator sequence, with human-readable input labels |
| `RecoveryPanel` | Shows safe API warnings/actions and the exact terminal fallback command without exposing secrets or account data |
| `SystemSetupWorkspace` | Loads readiness and authentication in parallel, owns device-auth mutation/cache coordination, and announces combined state changes |
| `Pending/PendingSystemSetup` | Static, geometry-matched placeholders for the three setup regions |
| `presentation.ts` | Finite API-state-to-copy mappings and the explicit readiness-check allowlist/order |
| `queries.ts` | Suspense query options plus waiting-only, one-second authentication polling |

### Assets

Icons: Lucide (primary), React Icons (auth-footer social only: GitHub,
LinkedIn, YouTube). SVGs in `frontend/public/assets/images/`: `apex-logo.svg`
/ `apex-logo-light.svg` (200x40), `apex-icon.svg` / `apex-icon-light.svg`,
`favicon.png`.

---

## 8. Routes & Screen Blueprints

### Route structure

| Route | File | Description |
|-------|------|-------------|
| `/login`, `/signup`, `/recover-password`, `/reset-password` | `routes/*.tsx` | Public auth flow, consistent luxury styling |
| `/` | `routes/index.tsx` | Public one-source-to-four-publications product story |
| `/create` | `routes/_layout/create.tsx` | Authenticated multimode course intake |
| `/jobs/$jobId` | `routes/_layout/jobs.$jobId.tsx` | Owner-scoped revisioned progress and terminal handoff |
| `/settings` | `_layout/settings.tsx` | User settings (tabbed) |
| `/admin` | `_layout/admin.tsx` | Admin panel (superuser only) |
| `/setup` | `_layout/setup.tsx` | System readiness and device authentication (superuser only) |

### Public landing (`/`)

**User job:** understand the transformation, optionally preserve one bounded
topic, and enter the configured access path. **Primary action:** `Save topic
and continue to sign in`; direct sign-in remains available beside it.

Desktop uses an asymmetric narrative: identity, a tab-scoped topic handoff,
and truthful AI/privacy copy occupy the wider column; one bounded source sheet
points to a two-by-two publication ledger named Course, Review materials,
Student assessment, and Instructor answer key. A compact evidence strip
explains research, cross-document alignment, and private owner access without
fabricated metrics or compliance claims. Mobile becomes one reading sequence:
identity, handoff, access, source, four publications, process, privacy. The
visual relationship uses keylines and spacing, not ornamental gradients or
animated connectors.

### Course intake (`/create`)

**User job:** provide one source plus enforced learning intent and submit one
durable request. **Primary action:** `Create my learning package`.

The workbench reads top to bottom: page identity; source-mode control; active
source editor and bounded metadata preview; optional learning intent; age and
literal AI/research consent; one submit action. At wide viewports, the source
editor and a quiet outcome sidecar may form an 8/4 relationship. Below `lg`
they become a single logical column. Inactive source controls unregister, file
content is never parsed for preview, and no model/provider selector appears.
Validation stays next to its field, and submission moves focus to the first
invalid control.

### Course progress (`/jobs/$jobId`)

**User job:** understand durable server state and recover from a safe terminal
outcome. The heading remains `Building your learning package` until the server
returns a terminal status.

The stage rail uses the finite generated statuses: queued, researching,
drafting, validating, rendering, delivering, then ready. Its rows carry stable
text labels, while the adjacent update panel renders the server's safe progress
message. Unknown totals use activity copy rather than a guessed percentage.
Warnings are a separate reading region. Reconnecting keeps the last safe
snapshot visible. Failed and cancelled states replace the active-stage
treatment with stable recovery actions. Completed points to the Session 02
result composition without inventing preview data. On mobile the rail remains
vertical and labels wrap; no horizontal timeline or document scroll is
permitted.

### Shared page header

Protected product routes (Course creation, Admin, Settings, System setup) use
`Common/PageHeader.tsx`:

```tsx
<PageHeader
  eyebrow="Workspace"          // optional section eyebrow
  title="Workspace overview"   // the page's single h1 (display serif)
  description="..."            // concise copy, max-w-prose
  actions={<...>}              // wrapping action group
/>
```

Below `sm`, identity and actions stack with stretched full-width controls;
above `sm` they align at the bottom edge. Fixed-width controls must never
squeeze the description into a word column. Filters keep intrinsic width only
while the primary action still fits; otherwise they fill a two-column grid or
stack.

### Retired donor dashboard history

This subsection records superseded layout history only. Its library counts,
previews, actions, queries, and copy have no current route or component and
must not be restored. Phase 04 replaces this model with the course-job
contract.

**User job:** understand the current library state and take the next useful
action. **Primary action:** `Create item`.

Identity: eyebrow `Workspace`, `h1` `Workspace overview`, supporting copy
`Good to see you, {first name or email}. Here is the current state of your
library.`, actions `Create item` + `Open library`.

```text
+--------------------------------------------------------------------+
| Workspace                                                          |
| Workspace overview                   [Open library] [Create item]  |
| Good to see you, ...                                                 |
+--------------------------------------------------------------------+
| 01  LIBRARY STATUS                                                 |
|     24 items            descriptive status / exact counts only     |
|                                                                    |
| 02  LIBRARY PREVIEW                              Open all items ->  |
|     Title               Type       Source              Actions     |
|     ... compact rows, not nested cards ...                             |
|                                                                    |
| 03  WORKSPACE ACTIONS OR ADMINISTRATION                            |
|     Role-aware shortcuts and exact counts only                     |
+--------------------------------------------------------------------+
```

On mobile the rail becomes a compact section index label (`01 * Library
status`); actions become full-width (or two-column only when both stay >=44px
high with readable labels); preview rows stack title/type, clamped
description, source, and the actions menu.

**States:**

- **Pending** -- header and actions stay usable; static geometry-matched
  placeholders; no full-page shimmer; no entrance replay on refetch.
- **Empty** -- one focused onboarding state: title `Start your workspace`,
  body `Create an item to begin organizing your notes, references, or saved
  content.`, action `Create item`. Settings (and admin, for superusers)
  remain reachable.
- **Populated** -- exact total plus compact preview; long titles wrap to two
  lines; descriptions clamp with a non-hover recovery path; missing optional
  values use neutral copy (`No source`), not warnings.
- **Error** -- page identity stays visible; inline `We could not load your
  library` with `Try again`; Settings and Log out remain reachable; non-auth
  data errors never redirect to Login.
- **Success** -- existing toast contract after creation; refetch without
  entrance replay; a newly visible preview row gets a brief background
  emphasis (`rowHighlight`) and an announcement, no reorder spectacle.
- **Permission** -- the Administration section is absent for regular users,
  not disabled; direct-URL permission failures keep the Forbidden recovery
  path.

### System setup

**User job:** determine whether the local course-generation engine can run,
complete authentication when necessary, and recover from a blocked check.
**Primary action:** `Start authentication` only while authentication is
required.

Identity: eyebrow `Operations`, `h1` `System setup`, supporting copy that
identifies this as the local engine preflight, and a `Refresh status` action.
The screen is intentionally an operator field guide rather than a generic
settings form.

```text
+--------------------------------------------------------------------+
| Operations                                                         |
| System setup                                      [Refresh status] |
| Confirm this installation can generate courses safely.            |
+--------------------------------------------------------------------+
| SYSTEM VERDICT                                                     |
| Ready / Action required / Temporarily unavailable                  |
| One concise explanation; no readiness percentage or score         |
+--------------------------------------+-----------------------------+
| AUTHENTICATION                       | RECOVERY                    |
| Signed out / Waiting / Authenticated | API safe actions/warnings  |
| safe challenge link + code or CTA    | exact CLI fallback         |
+--------------------------------------+-----------------------------+
| READINESS CHECKS                                                  |
| 01 Runtime ... 02 Workspace ... stable API-backed order           |
+--------------------------------------------------------------------+
```

On mobile, verdict, authentication, and recovery appear before the detailed
checklist; card headings, badges, codes, and actions stack without making the
operator scan horizontally. Long challenge URLs and the CLI command wrap
safely. The authentication header switches from a two-column relationship to
a vertical group so status copy cannot create document overflow.

**States:**

- **Pending** - static placeholders preserve the verdict, authentication,
  checklist, and recovery geometry; the shell and page identity stay present.
- **Ready** - one positive verdict, all returned checks remain inspectable,
  and no authentication challenge is shown.
- **Action required** - failed or signed-out authentication exposes one
  `Start authentication` action and the exact CLI fallback.
- **Waiting** - the challenge URL and user code are visible and copyable;
  authentication status polls every one second while the API remains in
  `waiting`, then stops immediately for `authenticated`, `signed_out`, or
  `failed`.
- **Unavailable / failed** - safe API warnings and recovery actions stay
  visible; the live status announces the change without duplicating visible
  headings or leaking exception details.
- **Permission** - regular users are redirected before either system endpoint
  is queried; the sidebar entry is absent for them.

Only the API's safe readiness fields, input names, warnings/actions, device
challenge URL/code, and coarse authentication state may render. Tokens,
credentials, account identity, local paths, and raw exception details never
appear in the browser.

### Retired Items history

The `/items` route and its components are removed. The following desktop and
mobile notes are preserved only as donor-era design history.

**Desktop:** table representation with Title over ID hierarchy and minimal
decorative elevation; filters and `Create item` live in the shared header.

**Mobile:** a feature-level item record list from the same query data -- title
and type first, description clamped to two lines, source when present, ID and
metadata in details/edit dialog, actions menu visible without horizontal
scrolling, pagination and counts understandable. Never bend the table
primitive to serve both layouts; compose the mobile representation and switch
at the desktop table's breakpoint.

### Admin

**Desktop:** table with permission checks, current-user marker, role, status,
action menu. **Mobile:** user record list -- name and email as primary
identity, status/role as text plus semantic treatment, actions immediately
reachable, current-user marker adjacent to the name. Finding a person's role
or actions must never require horizontal scrolling.

### Settings

Profile, password, and danger-zone grouping under the shared page header.
Tabs scroll horizontally with a visible overflow affordance (or collapse to a
compact section selector) before labels collide. The destructive section gets
stronger separation without turning the screen red. Tested form labels,
validation, focus order, and outcome-specific action names are preserved.

### Forms

React Hook Form + Zod throughout:

```typescript
const form = useForm<FormData>({
  resolver: zodResolver(schema),
  mode: "onBlur",
  criteriaMode: "all",
  defaultValues: {...},
})
```

---

## 9. Data Contract

Every displayed value must have a truthful definition backed by the API.

| Dashboard content | API support | Rule |
|-------------------|-------------|------|
| Total job count | No aggregate endpoint | Do not infer it from a paginated or single-job response |
| Job status/result | Owner-scoped `JobStatusPublic` projection | Render only the returned revisioned state and fixed progress copy |
| Artifact availability | Owner-scoped verified manifest | Show only path-free entries returned by the API |
| Total user count | Exact `UsersPublic.count` | Superuser Administration section only |
| Recent activity, trends, last update | No timestamps or ordered feed | Do not design or ship until the backend contract changes |

If richer dashboard data is approved, add a read-only aggregate endpoint
(exact count and explicitly ordered preview) rather than fetching every
record into the browser. Timestamps are a prerequisite for any recency or
trend language.

### System setup contract

| Setup content | API support | Rule |
|---------------|-------------|------|
| Overall verdict | `SystemReadinessResponse.status` | Map the finite API state to one plain-language verdict; never compute a score |
| Readiness checks | `checks[].name`, `status`, `message`, `inputs` | Render only the explicit allowlisted checks in their stable operator order |
| Safe recovery guidance | `warnings` and `actions` | Preserve safe API meaning; do not append exception, token, account, or filesystem data |
| Authentication state | `SystemAuthStatusResponse.state` | Poll only while `waiting`; terminal states stop polling |
| Device challenge | `SystemAuthStartResponse.verification_url` and `user_code` | Show only after an explicit superuser action; make both keyboard-accessible |
| Terminal fallback | Engine CLI contract | Display exactly `uv run --package txt2crs txt2crs-system-auth` |

The browser does not infer engine health from HTTP success alone. It also
does not request authentication during page load: starting device auth is an
explicit operator action.

---

## 10. Responsive Design

Tailwind default breakpoints: `sm` 640, `md` 768, `lg` 1024, `xl` 1280.
`useMobile()` detects viewports under 768px (sidebar sheet).

| Pattern | Mobile | Desktop |
|---------|--------|---------|
| Form grid | Single column | `sm:grid-cols-2` / `-3` |
| Sidebar | Sheet overlay, closes on navigation | Persistent, collapsible |
| Logo | Icon in command strip | Full logo in sidebar |
| Page header | Stacked, stretched actions | Bottom-aligned identity + actions |
| Dense tables | Feature record lists | TanStack tables |
| System setup | Verdict to authentication to checks to recovery; stacked status header | Verdict first; authentication/checks share the workspace when space permits |
| Auth layout | Single column | 2-column grid |

Hard requirements: no document-level horizontal scroll at 320px or 200% zoom;
primary mobile controls >=44px where practical; layouts hold at 320, 375, 768,
and 1440px in both themes.

---

## 11. Accessibility

- One `main` landmark (`SidebarInset`); route content must not add another.
- Logical heading order: page `h1`, sections `h2`, record titles below.
- `aria-current="page"` on active navigation via router link behavior.
- Radix labels, descriptions, focus containment, Escape, and focus return
  preserved on every overlay.
- Visible `focus-visible` rings on all interactive elements; transforms never
  clip them. Hover-revealed actions (e.g. Copy ID) are also visible on
  keyboard focus.
- Status text alongside status color; truncation recoverable by wrap,
  expansion, pointer/focus tooltip, or a details surface.
- Important create, update, delete, and load-failure outcomes are announced;
  motion never carries status alone.
- Full reduced-motion support (Section 6) and keyboard operability throughout.
- Contrast: verify **rendered** text and UI contrast against WCAG 2.2 AA in
  both themes -- measured, not assumed from token math.

---

## 12. File & Contract Guardrails

- **Never edit** `frontend/src/client/` (regenerate via
  `npm run generate-client` after approved backend changes) or
  `frontend/src/routeTree.gen.ts`.
- **`frontend/src/components/ui/` is protected.** Change behavior through
  tokens, supported state classes, and feature-level composition; a global
  primitive reconciliation needs explicit approval as separate scope.
- Preserve TanStack Query keys and invalidation, auth checks and redirects in
  `_layout.tsx`, centralized Zod schemas and branded types, and accessible
  names / `data-testid` hooks unless tests migrate in the same change.
- Keep behavioral refactors separate from visual-system changes where
  practical. New motion dependencies are prohibited (Section 6).

---

## 13. QA & Validation

After any frontend change:

```bash
cd frontend
npm run lint && npm run typecheck && npm run build
npx playwright test          # when the backend/test environment is available
```

Current E2E coverage verifies the public four-publication story, configured
access, retired-route not-found behavior, multimode submission, duplicate
prevention, owner-scoped progress/re-entry, safe failure and ownership
recovery, mobile fit and touch actions, reduced-motion navigation, system
setup states, and the maintained auth/admin/settings surfaces. Result and
artifact workspace coverage expands with Session 02.

### Rendered QA matrix

Check each surface at 1440x900, the 768px boundary, 375x812, and 320px, in
light and dark, with keyboard, and under reduced motion:

- Protected shell (expanded/collapsed) and the mobile navigation sheet
- Public landing, course intake, active progress, and every terminal state
- System setup pending / ready / action required / waiting / authenticated /
  unavailable / failed / permission
- Admin desktop table and mobile record list
- Settings tabs, forms, danger zone
- Dialog, menu, select, sheet, tooltip

Also inspect: first paint, pending, settled, hover, press, focus, touch,
success, validation error, API error, disabled, permission, destructive
confirmation, interrupted navigation; long email, 255-character title, long
description/URL, missing optional fields, 100+ records, empty data; layout
shift, focus loss, clipped rings, pointer blocking, stale overlays, and
permanent `will-change`.

### Acceptance criteria

- The current page identity and four supported publication types are visible
  without implying job history, counts, or recency.
- The direction reads as an editorial workspace index, not a KPI dashboard.
- No displayed metric implies timestamps, trends, completeness, or recency
  the API does not provide.
- Light and dark have equivalent hierarchy and measured WCAG 2.2 AA contrast.
- No document-level horizontal scroll at 320px or 200% zoom; mobile Admin
  exposes identity, status, role, and actions without table scrolling.
- Keyboard focus is visible, overlay focus is contained and returned, and
  hover-only affordances have focus/touch equivalents.
- Reduced motion leaves complete static content and direct navigation; no new
  motion runtime ships without a product-state need.
- Generated files, protected primitives, auth/query/form contracts, and test
  hooks remain intact; lint, typecheck, build, Playwright, and rendered QA
  pass.
- System setup displays one truthful verdict, starts authentication only on
  explicit superuser input, polls only while waiting, stops at terminal
  states, exposes the exact CLI fallback, and never renders a secret, account
  identity, raw exception, or local filesystem path.

---

*The dashboard must feel useful before it feels decorative: one coherent
visual system, truthful information hierarchy, intentional mobile
transformations, complete async and permission states, and purposeful motion
with a correct reduced alternative.*
