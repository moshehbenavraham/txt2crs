# React motion recipes

These patterns are starting points, not a visual language. Derive distances, timing, and direction
from the approved motion brief. Verify installed package and router APIs before copying.

## Table of contents

- CSS-first entrance
- Radix state motion
- Reduced-motion hook
- TanStack Router view transitions
- Motion for React
- Off-screen pause
- Playwright reduced-motion coverage
- Cleanup checklist

## CSS-first entrance

Keep content visible by default. Add animation only for users who have not requested reduced
motion:

```css
@keyframes content-enter {
  from {
    opacity: 0;
    transform: translateY(var(--motion-distance-sm));
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.content-enter {
  opacity: 1;
}

@media (prefers-reduced-motion: no-preference) {
  .content-enter {
    animation: content-enter var(--motion-duration-overlay)
      var(--ease-out-quart) both;
  }
}
```

This project already implements this pattern as `.reveal-group` / `.reveal-delay-1..3` in
`frontend/src/index.css` (used by the dashboard); reuse those utilities before minting new ones.

Do not apply a stagger to arbitrary DOM children. Mark semantic groups explicitly:

```tsx
<header className="content-enter" style={{ "--motion-order": 0 } as React.CSSProperties} />
<section className="content-enter" style={{ "--motion-order": 1 } as React.CSSProperties} />
```

If order matters, derive a small capped delay from `--motion-order` inside the no-preference media
query. Do not create a 20-item cascade.

## Radix state motion

Radix state classes can remain CSS-first:

```tsx
className={cn(
  "data-[state=open]:animate-in data-[state=closed]:animate-out",
  "data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0",
  "motion-reduce:data-[state=open]:animate-none",
  "motion-reduce:data-[state=closed]:animate-none",
)}
```

Verify that disabling the exit animation does not interfere with focus return or portal unmount.
Test dialog, dropdown, sheet, select, and tooltip separately; they have different interaction
contracts.

This project already ships a project-wide reduced-motion clamp in `frontend/src/index.css` — it
resolves every animation, transition, and `::view-transition-*` pseudo-element to its final
state. Do not add a second clamp.

Do not assume the clamp is sufficient. JavaScript motion, video, canvas, autoplay, parallax, and
smooth-scroll code still require explicit gating. Verify complete final states.

## Reduced-motion hook

The project already ships a dependency-free `useSyncExternalStore`-based hook — import it instead
of re-creating it:

```tsx
import { usePrefersReducedMotion } from "@/hooks/usePrefersReducedMotion"

const prefersReducedMotion = usePrefersReducedMotion()
```

See `frontend/src/hooks/usePrefersReducedMotion.ts` for the implementation. Use it only where
JavaScript must decide (e.g. opting into a view transition); CSS handles everything else through
the global clamp.

## TanStack Router view transitions

The installed router supports a global default:

```tsx
const router = createRouter({
  routeTree,
  context: { queryClient },
  defaultViewTransition: true,
})
```

It also supports per-navigation opt-in:

```tsx
navigate({
  to: "/items",
  viewTransition: true,
})
```

Prefer per-navigation or carefully scoped defaults until the direction proves that every route
transition benefits. Keep persistent shell regions stable and assign view-transition names only to
unique, meaningful shared surfaces.

This project already implements the scoped pattern: the Dashboard→Items "Open library" link opts
in with `viewTransition`, the dashboard preview and Items table share
`view-transition-name: library-surface`, the shell claims `app-sidebar` and `command-strip`, and
`usePrefersReducedMotion()` gates the transition in JavaScript. Follow that shape for new
continuity work instead of enabling a global default.

```css
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: var(--motion-duration-route);
  animation-timing-function: var(--ease-out-quart);
}

@media (prefers-reduced-motion: reduce) {
  ::view-transition-old(root),
  ::view-transition-new(root) {
    animation: none;
  }
}
```

The API falls back when unsupported. Test focus, rapid navigation, back/forward, scroll reset, and
old/new route overlap. Do not use Astro `<ClientRouter />`, and do not add React canary types for
`<ViewTransition>`.

## Motion for React

Install only after the brief requires springs, layout projection, presence, shared layout, or
gestures:

```bash
cd frontend
npm install motion
```

Use the current package/import:

```tsx
import { AnimatePresence, motion, useReducedMotion } from "motion/react"

function StatusPanel({ id, children }: { id: string; children: React.ReactNode }) {
  const reduce = useReducedMotion()

  return (
    <AnimatePresence initial={false} mode="wait">
      <motion.section
        key={id}
        initial={reduce ? false : { opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={reduce ? undefined : { opacity: 0, y: -4 }}
        transition={reduce ? { duration: 0 } : { duration: 0.22 }}
      >
        {children}
      </motion.section>
    </AnimatePresence>
  )
}
```

For list changes, use stable domain IDs and `layout` only where tracking movement helps the user:

```tsx
<motion.tr layout="position" key={item.id}>
  {/* cells */}
</motion.tr>
```

Test table semantics before using animated table elements; a wrapper or card-list mobile
representation may be safer. Do not install or import legacy `framer-motion` for new work.

## Off-screen pause

Pause repeating work once it leaves the viewport:

```ts
const observer = new IntersectionObserver(([entry]) => {
  if (entry?.isIntersecting) {
    start()
  } else {
    stop()
  }
})

observer.observe(element)

// Cleanup:
observer.disconnect()
stop()
```

Apply the same rule to video (`play()`/`pause()`), canvas/WebGL render loops, timers, and
requestAnimationFrame work. Also gate startup with the reduced-motion preference.

## Playwright reduced-motion coverage

`frontend/tests/dashboard.spec.ts` already emulates reduced motion — extend it or follow its
shape. Use a focused test:

```ts
import { expect, test } from "@playwright/test"

test("renders the complete interaction with reduced motion", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" })
  await page.goto("/login")

  await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible()
  await expect(page.getByRole("button", { name: "Sign In" })).toBeEnabled()
})
```

For route or overlay work, assert the final behavior and focus destination. A screenshot can
supplement those assertions but should not replace them.

## Cleanup checklist

- Remove listeners, observers, timeouts, animation handles, and RAF loops on unmount.
- Cancel or resolve interrupted sequences into the latest correct state.
- Remove temporary `will-change`.
- Avoid stale closures around React state.
- Keep focus on a live, visible element through exit/unmount.
- Do not let test timers, StrictMode double effects, or rapid toggles create duplicate loops.
- Confirm no motion dependency is shipped when the implementation no longer needs it.
