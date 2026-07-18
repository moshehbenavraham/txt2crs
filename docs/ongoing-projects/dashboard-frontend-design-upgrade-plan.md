# Dashboard Frontend Design Upgrade Plan

**Status:** Proposed

**Prepared:** 2026-07-17

**Scope:** Authenticated React dashboard, shell, and core product routes

**Direction:** Editorial workspace index

## 1. Outcome

Upgrade the authenticated frontend from a polished shell with a sparse home route into a calm,
useful workspace for managing items and, for superusers, users. The result should retain the
existing warm editorial identity while making the product easier to understand, scan, and operate
on mobile and desktop.

This is a design and implementation blueprint. It does not authorize changes to generated API
files or protected shadcn/Radix primitives.

### In scope

- The protected application shell: sidebar, top bar, main content frame, and footer behavior.
- The `/` dashboard and all of its loading, empty, populated, error, permission, and
  reduced-motion states.
- Shared page-header composition used by `/items`, `/admin`, and `/settings`.
- Responsive representations for dense item and user data.
- Light and dark theme behavior, semantic tokens, accessibility, and motion.
- Focused browser coverage and design-documentation reconciliation.

### Out of scope

- A logo or brand replacement.
- A redesign of the public authentication flow, except for shared token or reduced-motion fixes.
- New AI claims, analytics, trends, or “recent activity” unsupported by the current API.
- Editing `frontend/src/client/`, `frontend/src/routeTree.gen.ts`, or
  `frontend/src/components/ui/`.
- Adding Motion for React, GSAP, smooth scrolling, canvas, or WebGL without a later,
  separately justified interaction requirement.

## 2. Evidence baseline

The audit used the source at this revision plus a local rendered application backed by the current
FastAPI service. Rendered checks covered 1440×900 and 375×812, light and dark themes, the expanded
and collapsed desktop sidebar, the mobile navigation sheet, empty Items, populated Admin, Settings,
an Add Item dialog, and reduced motion.

### Observed

| Evidence | Source or rendered check | User impact |
| --- | --- | --- |
| The home dashboard renders only a greeting and welcome sentence. | `frontend/src/routes/_layout/index.tsx`; 1440×900 light/dark render | The first authenticated screen does not explain the workspace, summarize its state, or offer a next action. |
| The sticky top bar contains only the sidebar trigger. | `frontend/src/routes/_layout.tsx`; desktop and mobile render | It consumes vertical space without providing page orientation or a useful command. |
| The shell has a capable editorial token system, three fonts, surface tiers, and both themes. | `frontend/src/index.css`, `frontend/index.html` | The upgrade can evolve existing equity instead of introducing a second visual language. |
| The default theme is dark, while the design document describes a system default. | `frontend/src/main.tsx`, `docs/frontend-ui-design.md` | Current behavior and documented intent disagree. |
| The Items header remains a single horizontal flex row at mobile width. At 375px, the description measured about 60.8px wide and 121.9px tall. | Rendered `/items?type=all`; `frontend/src/routes/_layout/items.tsx` | The description becomes a word stack beside fixed-width filters and the primary action. |
| The Admin table contains horizontal overflow on mobile. The page itself does not overflow, but Role, Status, and Actions require sideways scrolling. | Rendered `/admin` at 375×812; `DataTable` and Admin columns | Core identity and actions are not visible together, so scanning and operating the list is costly. |
| Settings fits at 375px in English, but all three tabs depend on short labels. | Rendered `/settings`; `frontend/src/routes/_layout/settings.tsx` | Longer translations or 320px layouts have little resilience. |
| Item data can contain a title, description, source URL, content, content type, and metadata. | `backend/app/models.py`, item routes, generated response types | A library-oriented dashboard can be grounded in real fields rather than invented KPIs. |
| Item and user list responses expose an exact `count`, but item records have no `created_at` or `updated_at`, and list order is not documented as recency. | `backend/app/models.py`, `backend/app/api/routes/items.py` | “Recent items,” trends, activity charts, and time-based claims would be dishonest without an API change. |
| The current page entrance is a generic `fadeInUp` on the entire route outlet. Fixed `nth-child` delays exist globally. | `frontend/src/index.css`, `frontend/src/routes/_layout.tsx` | Motion repeats regardless of information hierarchy and can replay on navigation without communicating meaning. |
| Reduced motion disables `.page-enter`, but not every Radix or `tw-animate-css` animation. A live reduced-motion check measured the Add Item dialog still using animation `enter` for `0.3s`. | `frontend/src/index.css`; Playwright with `reducedMotion: "reduce"` | Users requesting less motion still receive zoom/slide overlay choreography. |
| TanStack Router has built-in View Transition API support with graceful fallback. `motion` and GSAP are not installed. | Installed router source and `frontend/package.json` | One scoped continuity effect is possible without a new runtime dependency. |
| Login and other E2E tests depend on current copy, roles, accessible names, and test IDs. | `frontend/tests/` | Copy and interaction changes must migrate their tests deliberately. |

Development-only TanStack devtool controls visible in local screenshots are excluded from product
design findings.

### Inferred

- The current product is best described, from available behavior, as an authenticated item or
  content workspace with administrative user management. “AI command center,” productivity
  analytics, and activity intelligence are not yet supported product truths.
- The existing “Refined Editorial Luxury” direction is strongest on the auth flow and token layer,
  but the protected product lacks the information architecture needed to make that direction feel
  purposeful.
- A grid of generic KPI cards would fill space without improving the user's mental model.
- The most valuable first-screen belief is: “I can see the state of my library and know what to do
  next.”

### Assumptions

- Primary users are knowledge workers managing their own items; superusers additionally manage
  accounts.
- Creating or opening an item is the primary product action.
- The current logo, forest/cream/charcoal palette, and editorial typography should remain.
- The implementation may add feature components and shared compositions, but it will preserve
  routing, auth, query keys, forms, schemas, branded types, error handling, and accessible
  contracts.
- Product terminology remains “Items” until a product owner approves a more specific noun.

### Unknowns to resolve before implementation slice 2

- Whether an item is best understood as a note, document, source, saved result, or a broader
  workspace object.
- Whether missing source/content/metadata represents incomplete work or simply a valid item type.
- Whether first-visit theme behavior should remain dark for brand reasons. This plan recommends
  system preference.
- Whether the backend roadmap can add timestamps and dashboard aggregates.

None of these unknowns blocks the shell and responsive-foundation work. They do constrain dashboard
copy and which metrics may be shown.

## 3. Direction selection

Three directions were considered:

| Direction | Premise | Decision |
| --- | --- | --- |
| Editorial gallery | Large display type, wide whitespace, and isolated showcase panels make each item feel curated. | Rejected as the primary direction because operational tables, forms, and administration need more density. |
| Operations console | Compact sans-serif UI, dense metrics, and high information throughput prioritize expert speed. | Rejected because it discards useful brand equity and would make the auth and product experiences feel unrelated. |
| Editorial workspace index | A disciplined ledger-like structure combines expressive page identity with compact operational rows and restrained surfaces. | Selected because it supports both content reading and administrative work without becoming a generic dashboard template. |

### Design thesis

The authenticated interface should feel like an editorial index joined to a precise operations
workspace because users need to understand and manage content, not admire dashboard decoration. It
should avoid generic KPI-card grids, ornamental gradients, glow-heavy primary actions, and
indiscriminate pills. Display type will establish page identity; an indexed content rail, compact
rows, warm neutral surfaces, and role-specific actions will help users believe the workspace is
organized and trustworthy before they create or manage an item.

### Load-bearing decisions

1. **Make page identity stable.** Use “Workspace overview” as the dashboard `h1`; move the user's
   name into supporting copy. A long email must never become the page title.
2. **Use one continuous workspace index, not a card grid.** Organize the dashboard as numbered
   sections on a subtle index rail: Library status, Library preview, and role-specific actions.
3. **Let proximity group default content.** Use surface tone and keylines for structure; reserve
   shadows for overlays and truly elevated menus.
4. **Separate expressive and operational type.** Keep Playfair Display for page identity and major
   section statements, Outfit for controls and dense content, and JetBrains Mono only for IDs,
   counts, and technical values.
5. **Give color one job at a time.** Forest green means action, selection, and active navigation.
   Gold marks earned emphasis or a completed index state, not every decorative edge.
6. **Transform mobile layouts.** Page actions stack beneath identity, and dense tables become
   feature-specific record lists rather than desktop tables squeezed into horizontal scroll.
7. **Make one motion moment memorable.** The dashboard Library Index may continue spatially into
   the Items workspace on explicit navigation; everything else serves orientation, feedback, or
   state clarity.

## 4. Information architecture and screen blueprints

### 4.1 Protected shell

**User job:** Know where they are, move between workspace areas, and access account or appearance
controls without losing content context.

**Desktop anatomy:**

- Expanded sidebar around the current width, with full logo, primary navigation, appearance, and
  account controls.
- Collapsed sidebar retains icons and immediate tooltips.
- A 48–56px command strip contains the sidebar trigger and a compact breadcrumb or section label.
- Main content uses one consistent max width and responsive gutter token.
- Social links leave the protected workspace footer. Keep them on public/auth surfaces or an About
  destination.
- The protected footer is removed unless it carries task-relevant status, version, or legal
  information.

**Mobile transformation:**

- The command strip contains a 44×44 navigation trigger, compact brand mark, and current section
  label.
- Navigation remains a Radix sheet with focus containment and closes after route selection.
- Account and appearance controls remain reachable inside the sheet.
- No persistent bottom content competes with page actions.

**Recommended navigation treatment:**

- Replace the large full-width active pill with a quieter surface tint plus a forest index keyline.
- Preserve icon, text, focus ring, tooltip, `aria-current`, and the existing keyboard shortcut.
- Do not animate the persistent shell during route changes.

**States:**

- Loading a protected route keeps the shell stable.
- Auth invalidation still follows the existing global redirect behavior.
- Forbidden and route-error states render within the same content frame.
- Sidebar interruption, rapid toggling, Escape, and focus return must end in the latest correct
  state.

### 4.2 Dashboard

**User job:** Understand the current library state and take the next useful action.

**Primary action:** `Create item`.

**Page identity:**

- Eyebrow: `Workspace`
- `h1`: `Workspace overview`
- Supporting copy: `Good to see you, {first name or email}. Here is the current state of your
  library.`
- Primary action: `Create item`
- Secondary link where useful: `Open library`

**Desktop composition:**

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ Workspace                                                                  │
│ Workspace overview                     [Open library] [Create item]         │
│ Good to see you, …                                                       │
├────────────────────────────────────────────────────────────────────────────┤
│ 01  LIBRARY STATUS                                                         │
│     24 items                  descriptive status / exact supported counts   │
│     ─────────────────────────────────────────────────────────────────────   │
│                                                                            │
│ 02  LIBRARY PREVIEW                                      Open all items →   │
│     Title                     Type       Source                 Actions      │
│     Representative item …     General    example.com               •••      │
│     … compact rows, not nested cards …                                    │
│                                                                            │
│ 03  WORKSPACE ACTIONS OR ADMINISTRATION                                    │
│     Role-aware shortcuts and exact counts only                             │
└────────────────────────────────────────────────────────────────────────────┘
```

The numbered rail is the recognizable visual idea. It encodes reading order and workspace
structure; it is not a decorative timeline.

**Mobile composition:**

```text
[menu] Workspace

Workspace overview
Good to see you, …
[Create item]
[Open library]

01 · Library status
24 items
supported status rows

02 · Library preview
[title / type]
[description]
[source]                         [•••]

03 · Workspace actions
role-aware links
```

The rail becomes a compact section index label. Actions become full-width or a two-column group
only when both remain at least 44px high and retain readable labels.

#### Data contract

| Dashboard content | Current support | Plan |
| --- | --- | --- |
| Total item count | Exact `ItemsPublic.count` | Include in the first frontend-only version. |
| Library preview | `ItemsPublic.data`, up to 100 records, with no documented recency order | Label `Library preview`, never `Recent items`; show a small stable subset. |
| Empty vs populated state | Exact count and data | Include. |
| Total user count for superusers | Exact `UsersPublic.count` | Include only in the role-aware Administration section. |
| Source/content/metadata coverage | Derivable only from the returned page, not necessarily the entire library | Defer until an aggregate endpoint exists, or label the sample explicitly. |
| Recent activity, trends, last update | No timestamps or ordered activity feed | Do not design or ship until the backend contract changes. |
| Item readiness or health | Product meaning is undefined | Resolve semantics before presenting a score or warning. |

If richer dashboard information is approved, add a read-only aggregate endpoint rather than
fetching every record into the browser. A useful response would include exact item count,
content-type distribution, field coverage counts, and an explicitly ordered preview. Timestamps
are required before any recent or trend language.

#### Dashboard states

**Pending**

- Keep the page header and actions usable when possible.
- Skeletons match the final index rail and row geometry.
- Avoid a full-page shimmer; static surface placeholders are enough.
- Do not replay initial entrance motion during routine query refetch.

**Empty**

- Replace zero-value dashboard modules with one focused onboarding state:
  - Title: `Start your workspace`
  - Body: `Create an item to begin organizing your notes, references, or saved content.`
  - Action: `Create item`
- Preserve a direct path to account settings and, for superusers, administration.

**Populated**

- Show the exact total and a compact library preview.
- Long titles wrap to two lines; descriptions clamp with a non-hover recovery path.
- Missing optional values use neutral copy such as `No source`, not warnings.

**Error**

- Keep page identity visible.
- Use an inline problem surface: `We could not load your library` with `Try again`.
- Preserve access to Settings and Log out.
- Do not redirect non-auth data errors to Login.

**Success**

- Reuse the existing toast contract after creation.
- Refetch the dashboard query without replaying the page entrance.
- If the newly created item appears in the preview, use a brief background emphasis and announce
  the result; do not reorder rows with spectacle.

**Permission**

- The Administration section is absent for regular users, not disabled.
- A permission failure reached by direct URL keeps the current Forbidden recovery path.

### 4.3 Shared page header

Create a feature-level `PageHeader` composition and use it on Dashboard, Items, Admin, and
Settings.

**Anatomy:**

- Optional section eyebrow.
- One `h1`.
- One concise description with a readable maximum width.
- A wrapping action group.

**Responsive rule:**

- Below `sm`, stack identity and actions with `align-items: stretch`.
- Filters may remain intrinsic width only when a primary action still fits. Otherwise, make the
  filter and action fill a two-column grid or stack.
- Above `sm`, align identity and actions at the bottom edge.
- Never allow fixed-width controls to reduce explanatory copy to a word column.

### 4.4 Items

**Desktop:** Keep the table representation, but strengthen the hierarchy of Title over ID and
reduce decorative elevation. Filters and `Create item` belong in the shared header.

**Mobile:** Render an item record list from the same query data:

- Title and type form the first row.
- Description clamps to two lines.
- Source is visible when present.
- ID and metadata move into details or the edit dialog.
- The actions menu remains visible without horizontal scrolling.
- Pagination and result counts remain understandable.

Do not modify the table primitive to force it to serve two incompatible layouts. Compose a
feature-level mobile representation and switch at the same breakpoint as the desktop table.

### 4.5 Admin

**Desktop:** Preserve the table, permission checks, current-user marker, role, status, and action
menu.

**Mobile:** Use a user record list:

- Name and email are primary identity.
- Status and role are text plus semantic treatment; color is never the only signal.
- Actions are immediately reachable.
- The current-user marker stays adjacent to the name.

The first viewport should not require horizontal scrolling to find a person's role or available
actions.

### 4.6 Settings

- Keep the existing profile, password, and danger-zone grouping.
- Use the shared page header.
- Make tabs horizontally scrollable with a visible overflow affordance or switch to a compact
  mobile section selector before labels collide.
- Give the destructive section stronger separation without turning the entire screen red.
- Preserve tested form labels, validation, focus order, and outcome-specific action names.

## 5. Visual system

### Typography

| Role | Typeface | Direction |
| --- | --- | --- |
| Page identity | Playfair Display | One expressive `h1` per page; responsive size with a stable line-height. |
| Section statement | Playfair Display or Outfit semibold | Use Playfair only where the section carries narrative weight; use Outfit in operational panels. |
| Body and controls | Outfit | Default for forms, navigation, tables, helper text, and buttons. |
| Technical values | JetBrains Mono | IDs, exact counts, metadata, and code-like content only. |

Remove emoji and excessive punctuation from page identity. Warmth should come from concise copy and
the user's name, not from turning an email address into a large decorative headline.

### Color and surfaces

- Retain warm cream/charcoal foundations and forest primary roles in both themes.
- Use gold for earned emphasis, a completed index marker, or one highlighted value.
- Use background and border shifts for default grouping.
- Reserve shadow for dialogs, dropdowns, sheets, and temporary elevation.
- Replace raw status grays and greens in feature code with semantic success, warning, info, and
  muted roles where existing tokens support them.
- Measure actual rendered contrast in both themes. Do not inherit the design document's unverified
  contrast ratios as fact.

### Shape

- Controls: 8–10px radius.
- Data rows and compact surfaces: 10–12px radius where a container is necessary.
- Major workspace surface: 12–16px.
- Overlays: 16px.
- Pills are reserved for compact status or taxonomy, not navigation, containers, and every action.

### Grid and spacing

- Keep a content maximum near the current `max-w-6xl`, but expose it as a shell role rather than a
  route-specific accident.
- Desktop uses a 12-column grid only where content relationships require it.
- Mobile page gutters begin at 20–24px and must work at 320px.
- Section rhythm should be larger than internal component spacing.
- Use proximity before adding a border or container.

### Proposed semantic token rationalization

Implement in `frontend/src/index.css`; avoid scattered values in JSX.

| Role | Proposed token | Starting value |
| --- | --- | --- |
| Page inline gutter | `--space-page-inline` | `clamp(1.25rem, 3vw, 3rem)` |
| Section rhythm | `--space-section` | `clamp(2rem, 4vw, 3.5rem)` |
| Strong boundary | existing `--border-strong` | Keep, then verify in both themes. |
| Selected surface | `--surface-selected` | Derive from primary with restrained alpha. |
| Feedback motion | `--motion-duration-feedback` | `120ms` |
| Small state motion | `--motion-duration-state` | `180ms` |
| Overlay motion | `--motion-duration-overlay` | `260ms` |
| Route continuity | `--motion-duration-route` | `320ms` |
| Small motion distance | `--motion-distance-sm` | `4px` |
| Reveal motion distance | `--motion-distance-md` | `8px` |

Consolidate duplicate timing variables currently declared in both `@theme inline` and `:root`.
Keep compatibility aliases during migration, then remove dead animation utilities after consumer
searches.

### Theme behavior

- Recommended first-visit default: `system`.
- Persist explicit Light, Dark, or System selection using the current provider and storage key.
- Treat light and dark as independent compositions with the same semantic hierarchy.
- Verify theme selection does not animate the entire page or leave icons in an intermediate state
  under reduced motion.

## 6. Motion brief

### Subject, audience, and job

The subject is a personal item library inside an authenticated workspace. Knowledge workers and
administrators need to orient themselves, understand library state, and move into management tasks
without losing context.

### Signature interaction

When a user selects `Open library` from the dashboard Library Index, that index surface continues
into the Items workspace using a short, scoped same-document view transition. The sidebar and
command strip remain fixed. Unsupported browsers navigate normally, mobile may use a restrained
opacity alternative, and reduced-motion users receive an instant transition.

This is the only signature effect. It is tied to the product's overview-to-library relationship
and should not become a global route cross-fade.

### Supporting roles

| Interaction | Semantic role | Layer |
| --- | --- | --- |
| Dashboard header then index sections settle on first data load | Hierarchy | CSS, explicit semantic order, capped at three groups |
| Sidebar expand/collapse | Orientation | Existing CSS transition, rationalized tokens |
| Button press and selection | Feedback | CSS transform/color, 80–160ms |
| Dialog, menu, select, and mobile sheet | Continuity and focus context | Radix state classes plus centralized tokens |
| Item created or updated | Feedback and attention | Toast plus optional brief row surface emphasis |
| Loading state to content | Continuity | Geometry-matched skeleton to settled content; no large shift |
| Filter change or routine refetch | None | Keep content stable; do not replay page entrance |

### Quiet regions

- Table and record-list contents while users compare values.
- Long content previews, metadata blocks, IDs, and code-like data.
- Settings forms during typing and validation.
- Destructive confirmation copy.
- Footer or legal content.
- Routine query refetches.

### Semantic mapping

- Forward navigation from Dashboard to Items may expand the shared library surface.
- New content may receive a brief local highlight at the changed row.
- Section reveal order follows `01 Library status`, `02 Library preview`, then
  `03 Workspace actions`; it is not based on arbitrary DOM child count.
- Scale is limited to controls and overlays. Data values, tables, and long text do not zoom.
- Stagger is capped at three semantic groups and never cascades through list rows.

### Motion state matrix

| State | Required behavior |
| --- | --- |
| First paint | All essential content is visible and correctly placed without waiting for animation. |
| Pending | Honest status and stable skeleton geometry; indefinite work includes status copy. |
| Settled | No lingering `will-change`, blur, transform, or pointer-blocking layer. |
| Hover/pointer | Optional enhancement only; no information appears exclusively on hover. |
| Press | Immediate 80–160ms causal feedback without delaying the action. |
| Focus | Stable, visible focus ring; transforms must not clip or obscure it. |
| Touch | Complete behavior with 44×44 practical targets and no hover dependency. |
| Exit | Focus returns to a live trigger; disappearing UI cannot retain focus. |
| Interruption | Rapid navigation, open/close, and filter changes resolve to the latest correct state. |
| Error | Recovery action remains still and prominent. |
| Reduced | Spatial movement, zoom, shimmer loops, and route morphing are disabled; final content is complete. |

### Implementation-layer decision

1. Use stillness in dense reading and comparison regions.
2. Use CSS transitions/keyframes and Radix data states for local feedback and overlays.
3. Use TanStack Router's installed View Transition integration only on the Dashboard-to-Items
   link after the static layout is approved.
4. Do not install `motion` for opacity, translate, overlay, or route work already covered here.
5. Do not install GSAP or smooth scrolling.

### Reduced-motion correction

- Add a project-wide CSS safety clamp in `prefers-reduced-motion: reduce`.
- Explicitly neutralize custom page, auth, Radix, `tw-animate-css`, shimmer, spin, and theme-icon
  motion where a complete static state is required.
- Add a dependency-free `usePrefersReducedMotion()` hook only if JavaScript must decide whether to
  opt into the scoped view transition.
- Test Dialog, Dropdown Menu, Select, Sheet, Tooltip, theme selection, and route navigation
  separately. The current `.page-enter` check is insufficient.

## 7. Accessibility and interaction requirements

- Maintain one `main` landmark. The current `SidebarInset` already renders a `main`, so route
  content must not add a second competing main landmark.
- Use logical heading order: page `h1`, major sections `h2`, record titles below that hierarchy.
- Set `aria-current="page"` through router-supported link behavior for active navigation.
- Preserve Radix labels, descriptions, focus containment, Escape, and focus return.
- Keep primary mobile controls at least 44px high where practical.
- Add focus-visible or group-focus-within visibility for actions currently revealed only on hover,
  such as Copy ID.
- Keep status text alongside status color.
- Make truncation recoverable by wrapping, expansion, tooltip for pointer/focus, or a details
  surface as appropriate.
- Verify 200% zoom and 320px reflow without document-level horizontal scroll.
- Announce important create, update, delete, and load failure outcomes; motion cannot carry status.
- Verify rendered text and UI contrast against WCAG 2.2 AA in both themes.

## 8. Implementation plan

Keep each slice reviewable and preserve behavior contracts.

### Slice 0 — Confirm product language and data contract

- [ ] Choose the user-facing noun for `Item`; retain `Item` if no better product term is approved.
- [ ] Confirm whether source/content/metadata coverage is descriptive or represents readiness.
- [ ] Decide whether the backend will provide aggregates and timestamps.
- [ ] Approve System as the first-visit theme default or record the reason to retain Dark.
- [ ] Approve tested-copy migrations from the current greeting and `Add Item` to the final wording.

**Exit criterion:** Dashboard copy and every displayed value have a truthful definition.

### Slice 1 — Foundation, shell, and shared page header

Primary files:

- `frontend/src/index.css`
- `frontend/src/main.tsx`
- `frontend/src/routes/_layout.tsx`
- `frontend/src/components/Common/PageHeader.tsx` (new)
- `frontend/src/components/Sidebar/AppSidebar.tsx`
- `frontend/src/components/Sidebar/Main.tsx`
- `frontend/src/components/Common/Footer.tsx`

Tasks:

- [ ] Consolidate semantic spacing, surface, shape, and motion roles.
- [ ] Add the shared responsive PageHeader composition.
- [ ] Turn the blank top bar into a useful command strip.
- [ ] Apply the quieter indexed active-navigation treatment through feature composition.
- [ ] Remove or relocate protected-workspace social links.
- [ ] Apply the shared header to Items, Admin, and Settings.
- [ ] Fix the 375px Items header collapse before adding dashboard complexity.
- [ ] Reconcile first-visit theme behavior.

**Exit criterion:** Shell and page headers work at 320, 375, 768, and 1440px in both themes with
keyboard and touch.

### Slice 2 — Dashboard index

Primary files:

- `frontend/src/routes/_layout/index.tsx`
- `frontend/src/components/Dashboard/WorkspaceHeader.tsx` (new)
- `frontend/src/components/Dashboard/LibraryIndex.tsx` (new)
- `frontend/src/components/Dashboard/LibraryPreview.tsx` (new)
- `frontend/src/components/Dashboard/DashboardEmpty.tsx` (new)
- `frontend/src/components/Pending/PendingDashboard.tsx` (new)

Tasks:

- [ ] Add suspense query options using existing service and query-key conventions.
- [ ] Implement exact total count, truthful preview, empty state, retryable error, and role-aware
  actions.
- [ ] Reuse the existing create mutation behavior without forking validation or payload shape.
- [ ] Keep regular-user and superuser content distinct.
- [ ] Add aggregate-backed modules only if Slice 0 approves their semantics and API.
- [ ] Preserve session invalidation, auth redirect, and global API error behavior.

**Exit criterion:** A user can identify the workspace, its current library state, and the primary
action within the first mobile and desktop viewport.

### Slice 3 — Responsive operational surfaces

Primary files:

- `frontend/src/routes/_layout/items.tsx`
- `frontend/src/routes/_layout/admin.tsx`
- feature components under `frontend/src/components/Items/` and
  `frontend/src/components/Admin/`
- `frontend/src/components/Common/DataTable.tsx` only for behavior shared by desktop tables

Tasks:

- [ ] Add feature-specific mobile item and user record lists.
- [ ] Keep desktop tables and existing TanStack Table behavior.
- [ ] Preserve pagination, filters, action menus, copy behavior, current-user marker, and
  permissions.
- [ ] Make Copy ID visible on keyboard focus.
- [ ] Validate long titles, descriptions, URLs, names, emails, and localized labels.
- [ ] Complete loading, empty, error, success, disabled, and destructive states.

**Exit criterion:** Core identity and actions remain visible without horizontal scrolling on mobile.

### Slice 4 — Purposeful motion and reduced-motion completeness

Primary files:

- `frontend/src/index.css`
- `frontend/src/main.tsx` or the scoped Dashboard-to-Items navigation composition
- `frontend/src/hooks/usePrefersReducedMotion.ts` only if JavaScript gating is needed
- feature-level overlay consumers where final-state behavior needs explicit classes

Tasks:

- [ ] Replace generic outlet-level entrance replay with explicit semantic dashboard groups.
- [ ] Add the scoped Dashboard-to-Items view transition and unsupported-browser fallback.
- [ ] Keep the persistent shell stable.
- [ ] Add the reduced-motion safety clamp and targeted exceptions.
- [ ] Verify rapid navigation, dialog reopen, sheet interruption, filter refetch, and focus return.
- [ ] Confirm no Motion or GSAP dependency is needed.

**Exit criterion:** Every effect has a semantic role, and reduced motion renders a complete static
state with no overlay zoom/slide or shimmer loop.

### Slice 5 — QA, tests, and documentation

Primary files:

- `frontend/tests/dashboard.spec.ts` (new)
- focused responsive and motion coverage under `frontend/tests/`
- `docs/frontend-ui-design.md`

Tasks:

- [ ] Add dashboard populated, empty, error/retry, and permission coverage.
- [ ] Add mobile header and record-list assertions.
- [ ] Add `page.emulateMedia({ reducedMotion: "reduce" })` coverage for route and overlay final
  states.
- [ ] Update selectors only when copy or accessible-name changes are intentional.
- [ ] Reconcile `docs/frontend-ui-design.md` with actual theme default, shell dimensions, tokens,
  responsive patterns, and reduced-motion behavior.
- [ ] Remove obsolete utility documentation and record the selected direction.

**Exit criterion:** Rendered QA, automated behavior checks, and design documentation describe the
same system.

## 9. File and contract guardrails

- Never edit `frontend/src/client/`; regenerate only after an approved backend contract change.
- Never edit `frontend/src/routeTree.gen.ts`.
- Treat `frontend/src/components/ui/` as protected. Use token changes, supported state classes,
  and feature-level composition. A global primitive reconciliation requires explicit approval as
  a separate scope decision.
- Preserve TanStack Query keys and invalidation behavior.
- Preserve auth checks and redirects in `_layout.tsx`.
- Preserve centralized schemas and branded types.
- Preserve accessible names and `data-testid` hooks unless tests migrate in the same change.
- Keep behavioral refactors separate from visual-system changes where practical.

## 10. Rendered QA matrix

| Surface/state | 1440×900 | 768px boundary | 375×812 | 320px | Light | Dark | Keyboard | Reduced |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Protected shell expanded/collapsed | Required | Required | N/A | N/A | Required | Required | Required | Required |
| Mobile navigation sheet | N/A | Required | Required | Required | Required | Required | Required | Required |
| Dashboard pending/empty/populated/error | Required | Required | Required | Required | Required | Required | Required | Required |
| Items filter and create action | Required | Required | Required | Required | Required | Required | Required | Required |
| Item desktop table/mobile list | Required | Required | Required | Required | Required | Required | Required | As applicable |
| Admin desktop table/mobile list | Required | Required | Required | Required | Required | Required | Required | As applicable |
| Settings tabs/forms/danger zone | Required | Required | Required | Required | Required | Required | Required | Required |
| Dialog/menu/select/sheet/tooltip | Required | Required | Required | Required | Both for token work | Both for token work | Required | Required |

Also inspect:

- First paint, pending, settled, hover, press, focus, touch, success, validation error, API error,
  disabled, permission, destructive confirmation, and interrupted navigation.
- Long email, 255-character title, long description, long URL, missing optional fields, 100+
  records, and empty data.
- Layout shift, focus loss, accidental page scroll, clipped rings, pointer blocking, stale
  overlays, long tasks, and permanent `will-change`.

## 11. Validation

Run after each implementation slice:

```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```

Run focused browser coverage during development, then the relevant Playwright suite when the
backend/test environment is available:

```bash
cd frontend
npx playwright test
```

For the motion slice, record the computed final state under reduced motion in addition to visual
inspection. The test must verify focus destination and enabled controls, not only screenshots.

## 12. Acceptance criteria

- The dashboard communicates page identity, exact supported library state, and `Create item` within
  the first viewport at 375×812 and 1440×900.
- The visual direction is recognizable as an editorial workspace index rather than a generic KPI
  dashboard.
- No displayed metric implies timestamps, trends, completeness, or recency the API does not
  provide.
- Light and dark modes have equivalent hierarchy and measured WCAG 2.2 AA contrast.
- No document-level horizontal scroll appears at 320px or 200% zoom.
- Mobile Items and Admin expose identity, status/type, and actions without requiring horizontal
  table scrolling.
- Keyboard focus is visible, overlay focus is contained and returned correctly, and hover-only
  affordances have focus/touch equivalents.
- The one shared-surface transition works only where it reinforces Dashboard-to-Items continuity;
  unsupported browsers fall back cleanly.
- Reduced motion disables route morphing, overlay zoom/slide, shimmer loops, and non-essential
  transforms while leaving complete content.
- No new motion runtime dependency ships.
- Generated files, protected primitives, auth/query/form contracts, and test hooks remain intact.
- Lint, typecheck, build, relevant Playwright tests, and rendered QA pass.

## 13. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| The generic noun “Item” makes product-specific design difficult. | Resolve terminology in Slice 0; keep copy neutral until then. |
| Dashboard ambition outruns the API. | Ship exact count, preview, and actions first; add aggregates/timestamps before analytics language. |
| Broad visual changes require primitive edits. | Stay in tokens and feature composition; request separate approval before primitive reconciliation. |
| A view transition creates focus or pointer ambiguity. | Opt in only on one link, keep duration near 320ms, keep shell stable, and test rapid navigation and fallback. |
| Dark-first styling leaves weak light or system behavior. | Validate both themes in every slice and adopt System as the recommended first-visit default. |
| Mobile record lists drift from desktop table behavior. | Share query data, domain IDs, menus, and mutation handlers; vary only presentation. |
| Copy changes break E2E tests. | Migrate accessible-name and text assertions in the same reviewable slice. |
| Reduced-motion coverage appears complete because page entrance is disabled. | Test each Radix surface and JavaScript route decision explicitly; retain the global safety clamp. |

## 14. Definition of done

The upgrade is complete when the authenticated frontend presents one coherent visual system,
truthful information hierarchy, intentional mobile transformations, complete async and permission
states, purposeful motion with a correct reduced alternative, and passing rendered and automated
validation. The dashboard must feel useful before it feels decorative.
