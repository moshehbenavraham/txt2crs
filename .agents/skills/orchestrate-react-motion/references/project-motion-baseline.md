# Project motion baseline

Verify this snapshot against the current worktree before implementation. It reflects the frontend
inspected in July 2026.

## Table of contents

- Existing capabilities
- Current choreography
- Router capability
- Coverage gaps
- High-leverage files
- Protected contracts

## Existing capabilities

The frontend already includes:

- Tailwind CSS 4 through `@tailwindcss/vite`;
- `tw-animate-css`;
- Radix primitives with `data-[state=open|closed]` animation classes;
- global duration and easing custom properties in `frontend/src/index.css`;
- React 19, TanStack Router, TanStack Query, and strict TypeScript;
- Playwright browser tests.

It does not currently declare `motion`, `gsap`, or `lenis` in `frontend/package.json`.

## Current choreography

`frontend/src/index.css` defines:

- `fadeInUp`, `fadeInScale`, `fadeIn`;
- `slideInFromRight`, `slideInFromLeft`;
- `shimmer` and `luxuryShimmer`;
- `pulseSubtle`, `float`, and `scaleIn`;
- `.page-enter` and `.page-enter-child`;
- fixed `nth-child` entrance delays through child 8;
- `.card-hover`, `.button-press`, and skeleton utilities;
- timing/easing variables in both `@theme inline` and `:root`.

Current consumers include:

- a `.page-enter` wrapper around the protected route outlet;
- independent auth-shell entrance animation;
- dialog/menu/sheet state animation through `tw-animate-css`;
- sidebar width, icon, hover, and collapse transitions;
- theme icon rotation/scale;
- logo hover/press and route/component hover transitions.

This is useful infrastructure, but motion language is mostly generic fade/translate/scale and
repeated global entrance behavior. Treat that as a baseline to rationalize, not a mandate to add
more effects.

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

## Coverage gaps

At the inspected revision:

- the reduced-motion block in `index.css` targets `.page-enter`, `.page-enter-child`,
  `.card-hover`, and `.skeleton-luxury`, not every Radix/`tw-animate-css` state animation;
- `AuthLayout` uses direct animation utility strings outside that targeted list;
- page entrance can replay generically regardless of route meaning;
- fixed `nth-child` staggering encodes DOM order rather than intentional information hierarchy;
- CSS variables are duplicated between `@theme inline` and `:root`;
- no dedicated hook exists for JavaScript reduced-motion decisions;
- no Playwright test explicitly emulates reduced motion or captures motion state.

Treat these as audit prompts, not automatic scope. Fix what the user request and rendered evidence
support.

## High-leverage files

- `frontend/src/index.css`
- `frontend/src/main.tsx`
- `frontend/src/routes/_layout.tsx`
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
