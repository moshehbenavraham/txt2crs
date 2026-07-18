# Project motion baseline

Verify this snapshot against the current worktree before implementation. It reflects the frontend
inspected in July 2026.

## Table of contents

- Existing capabilities
- Current choreography
- Router capability
- Resolved gaps and watch items
- High-leverage files
- Protected contracts

## Existing capabilities

The frontend already includes:

- Tailwind CSS 4 through `@tailwindcss/vite`;
- `tw-animate-css`;
- Radix primitives with `data-[state=open|closed]` animation classes;
- semantic motion role tokens and easing custom properties in `frontend/src/index.css`;
- a dependency-free `usePrefersReducedMotion()` hook in
  `frontend/src/hooks/usePrefersReducedMotion.ts`;
- React 19, TanStack Router, TanStack Query, and strict TypeScript;
- Playwright browser tests, including reduced-motion emulation in
  `frontend/tests/dashboard.spec.ts`.

It does not currently declare `motion`, `gsap`, or `lenis` in `frontend/package.json`.

## Current choreography

`frontend/src/index.css` defines:

- semantic motion role tokens in `:root`: `--motion-duration-feedback` (120ms), `-state` (180ms),
  `-overlay` (260ms), `-route` (320ms), `--motion-distance-sm/md`, and easing curves
  (`--ease-out-expo`, `--ease-out-quart`, `--ease-in-out-quart`, `--ease-spring`); legacy
  `--duration-*` names remain as compatibility aliases;
- exactly four keyframes, all with live consumers: `fadeInUp` (auth-shell entrance),
  `luxuryShimmer` (skeleton), `riseIn` (dashboard section settle), and `rowHighlight` (brief
  emphasis on a newly created preview row);
- `.reveal-group` / `.reveal-delay-1..3` utilities inside
  `@media (prefers-reduced-motion: no-preference)` — the dashboard settles in explicit reading
  order, capped at three groups; there is no `nth-child` stagger and no outlet-level entrance;
- scoped view-transition styling for the `library-surface`, `app-sidebar`, and `command-strip`
  names.

Current consumers include:

- auth-shell entrance in `AuthLayout`;
- dashboard reveal groups and `rowHighlight` in `frontend/src/components/Dashboard/`;
- dialog/menu/sheet state animation through Radix + `tw-animate-css`;
- sidebar width, icon, hover, and collapse transitions, plus theme-icon transitions;
- the signature Dashboard→Items "Open library" view transition (TanStack Router `viewTransition`,
  gated in JavaScript by `usePrefersReducedMotion()`).

Routine query refetches do not replay entrances. Treat this as a rationalized baseline in which
every effect has a semantic role and the one signature moment is already claimed — not an
invitation to add more effects.

## Router capability

The installed TanStack Router source exposes:

- `defaultViewTransition?: boolean | ViewTransitionOptions` on router options;
- `viewTransition?: boolean | ViewTransitionOptions` on navigation/link options;
- a `document.startViewTransition()` implementation with unsupported-browser fallback.

Inspect current installed definitions before using:

```bash
rg -n "defaultViewTransition|viewTransition" \
  frontend/node_modules/@tanstack/router-core/src
```

The stable React type entrypoint in this project does not expose React's canary
`<ViewTransition>`. Do not add canary types or experimental imports as a shortcut.

## Resolved gaps and watch items

The July 2026 motion rationalization closed the gaps this file previously recorded:

- a project-wide clamp under `prefers-reduced-motion: reduce` resolves every animation,
  transition, and `::view-transition-*` pseudo-element to its complete final state;
- the outlet-level `.page-enter` replay, `nth-child` staggering, and unused keyframes
  (`fadeInScale`, `slideInFrom*`, `shimmer`, `pulseSubtle`, `float`, `scaleIn`) were removed;
- timing variables are consolidated in `:root` (no `@theme inline` duplication);
- `usePrefersReducedMotion()` exists for JavaScript gating;
- `frontend/tests/dashboard.spec.ts` emulates reduced motion.

Watch items when adding motion:

- keep the legacy `--duration-*` aliases working until their consumers migrate;
- new overlays and effects must render a complete final state under the clamp — verify, don't
  assume;
- do not dilute the single signature Dashboard→Items transition into a global route cross-fade.

## High-leverage files

- `frontend/src/index.css`
- `frontend/src/main.tsx`
- `frontend/src/routes/_layout.tsx`
- `frontend/src/hooks/usePrefersReducedMotion.ts`
- `frontend/src/components/Dashboard/` (reveal groups, row highlight, view-transition trigger)
- `frontend/src/components/Common/AuthLayout.tsx`
- `frontend/src/components/Common/Appearance.tsx`
- `frontend/src/components/Sidebar/`
- `frontend/src/components/ui/dialog.tsx`
- `frontend/src/components/ui/dropdown-menu.tsx`
- `frontend/src/components/ui/sheet.tsx`
- `frontend/src/components/ui/skeleton.tsx`
- the target route, its pending state, and its mutation components
- `frontend/playwright.config.ts` and relevant `frontend/tests/*.spec.ts`

## Protected contracts

- Never edit `frontend/src/client/` or `frontend/src/routeTree.gen.ts`.
- Preserve route/auth/query/form behavior while changing motion.
- Preserve accessible names, focus containment, and existing test selectors.
- Treat `frontend/src/components/ui/` as protected primitives unless the task explicitly
  authorizes primitive-layer changes.
- Keep light/dark themes and mobile sidebar/sheet behavior complete.
