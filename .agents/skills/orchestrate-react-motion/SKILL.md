---
name: orchestrate-react-motion
description: Art-direct, implement, and validate purposeful motion for this repository's React 19, Vite, TanStack Router, Tailwind CSS 4, and Radix/shadcn frontend while protecting accessibility, responsiveness, and interaction performance. Use when adding or reworking page or route transitions, list/layout changes, dialog/menu/sheet animation, loading feedback, hover/press/focus choreography, scroll-linked effects, gesture or shared-element motion, animation tokens, reduced-motion behavior, or when choosing between CSS, the Web Animations/View Transition APIs, Motion for React, and GSAP. Pair with $upgrade-react-visual-experience for broader screen, brand, token, or component-system redesign. Do not use Astro islands, Astro View Transitions, or Astro hydration guidance in this project.
---

# Orchestrate React Motion

Make motion communicate hierarchy, continuity, cause and effect, feedback, or atmosphere. Choose
the lightest mechanism that clears the visual bar, but do not reduce an ambitious approved
direction to generic fades merely to avoid JavaScript.

## Load the project context

Read [`references/project-motion-baseline.md`](references/project-motion-baseline.md) before
editing motion. It records the current CSS choreography, installed stack, router capability,
coverage gaps, and project constraints.

Use [`references/motion-decision-cheatsheet.md`](references/motion-decision-cheatsheet.md) while
choosing an implementation layer. Read the relevant sections of
[`references/react-motion-recipes.md`](references/react-motion-recipes.md) before wiring reduced
motion, CSS/Radix state animation, TanStack Router view transitions, Motion for React, loop
pausing, or Playwright coverage.

When motion is part of a wider redesign, invoke `$upgrade-react-visual-experience` first so the
motion language follows an approved screen and visual direction.

## Project constraints

- Work in the existing React SPA. Do not add Astro, `<ClientRouter />`, `client:*` directives,
  islands, or Astro integrations.
- Inspect `frontend/package.json` and the installed type/source definitions before relying on a
  library API. Match current pins unless the user asks for an upgrade.
- The project already ships CSS keyframes, timing tokens, `tw-animate-css`, and Radix state
  animations. Reuse or rationalize them before adding a dependency.
- TanStack Router in the inspected worktree supports `defaultViewTransition` and per-navigation
  `viewTransition`, backed by `document.startViewTransition()` with graceful fallback.
- Stable project types do not expose React's canary `<ViewTransition>` API. Do not import canary or
  experimental React types to obtain it.
- `motion` is not currently installed. Add it only when springs, layout/shared-element animation,
  presence/exit choreography, or gestures justify the dependency. For new work, use the current
  `motion` package and `motion/react` import, not the legacy `framer-motion` package.
- GSAP is not installed. Reserve it for a genuinely custom multi-step timeline or scrollytelling
  interaction that CSS, browser APIs, and Motion cannot express clearly. Smooth-scroll libraries
  are not a default for this data-oriented application.
- Never edit `frontend/src/client/` or `frontend/src/routeTree.gen.ts`. Preserve route, query,
  form, auth, accessible-name, and test-selector contracts.
- Treat `frontend/src/components/ui/` as protected primitives. Prefer token changes, feature
  composition, and supported state classes unless the user explicitly authorizes changing the
  primitive layer.

## Art-direct motion before choosing a tool

Write a compact motion brief:

- **Subject, audience, job:** name the product subject, who is acting, and what this screen or flow
  helps them accomplish.
- **Signature interaction:** choose at most one memorable, product-specific moment for the scoped
  flow.
- **Supporting roles:** assign every other effect a job: orientation, hierarchy, continuity,
  feedback, attention, or atmosphere.
- **Quiet regions:** name dense or high-risk areas that should remain still.
- **Semantic mapping:** map direction, order, stagger, scale, and continuity to real information
  structure or user causality.
- **States:** define first paint, pending, settled, hover/pointer, press, focus, touch, exit,
  interruption, error, and reduced-motion behavior.

Reject the brief if its signature effect could move unchanged to an unrelated product, if every
section animates with equal weight, or if the static/reduced render is incomplete.

## Choose the lightest sufficient layer

Evaluate top-down per interaction:

1. **No motion:** use when stillness improves speed, trust, comparison, or reading.
2. **CSS transitions/keyframes and Radix data states:** use for hover, press, focus, short
   entrances, overlays, skeletons, and deterministic state changes.
3. **Browser APIs:** use the Web Animations API for small imperative sequences and
   IntersectionObserver for visibility/off-screen control.
4. **TanStack Router + View Transition API:** use for same-document route continuity or a
   justified shared surface. Scope names carefully; a global cross-fade on every navigation is
   not automatically good motion.
5. **Motion for React (`motion/react`):** use for springs, layout projection, presence/exit,
   reordering, shared layout, and gestures tied to React state.
6. **GSAP:** use for a custom, synchronized timeline or scrollytelling sequence that earns its
   payload and authoring complexity.
7. **Video, canvas, WebGL, or image sequences:** treat as a dedicated media/runtime project with
   its own performance and accessibility plan.

Stop at the first layer that can fully deliver the brief. Do not add Motion or GSAP only to perform
opacity/translate entrances already covered by CSS.

## Implementation rules

### Motion tokens

Centralize durations, easings, distances, and semantic names in `src/index.css`. Use a small set of
roles such as feedback, reveal, overlay, and route continuity. Avoid arbitrary duration literals
scattered through JSX.

Keep common UI feedback roughly within these bands unless the brief proves otherwise:

- press/focus feedback: 80–160ms;
- hover and small state changes: 140–240ms;
- overlays and local entrances: 200–360ms;
- route/layout continuity: 250–500ms.

Duration is not the only variable; distance, easing, opacity range, and stagger must fit the
content. Longer is not more luxurious.

### Semantic choreography

- Animate the element that changed or caused the change.
- Preserve spatial continuity between trigger and result.
- Stagger only when order communicates priority or sequence; cap groups rather than cascading
  through arbitrary child counts.
- Prefer transform and opacity. Treat blur, filters, large shadows, masks, and backdrop effects as
  performance risks to measure.
- Do not animate layout properties in high-frequency paths when a transform can express the same
  result.
- Apply `will-change` only near an active animation and remove it afterward.
- Keep controls responsive during animation. Never delay essential state or block input for
  spectacle.
- Make hover enhancement optional; provide focus and touch behavior that remains complete.

### Async and data motion

- Keep skeleton geometry close to final content to prevent layout shift.
- Use progress or status copy when duration is uncertain; do not substitute an endless shimmer for
  meaningful feedback.
- Animate list insertion/removal only when it helps users track what changed.
- Avoid replaying a page entrance on routine query refetches.
- Preserve table readability and scroll position during updates.
- Announce important async outcomes accessibly; animation alone cannot convey status.

### Route motion

Use route transitions to reinforce navigation hierarchy or shared context. Keep the persistent
sidebar/header stable unless their change is meaningful. Avoid animating an old interactive route
over a new one long enough to create focus or pointer ambiguity.

Prefer the TanStack Router integration already available over a hand-rolled wrapper around
`document.startViewTransition()`. Gate or neutralize route animation for reduced-motion users and
verify browser fallback.

### Reduced motion

Honor `prefers-reduced-motion` in CSS and every JavaScript layer. Reduced motion is a complete,
correct render—not a blank element, frozen midway, or missing status.

- Start content visible by default; add motion inside `prefers-reduced-motion: no-preference` when
  possible.
- Disable non-essential transforms, parallax, smooth scrolling, large zooms, and repeated loops.
- Replace spatial continuity with an instant update or restrained opacity change only when that is
  comfortable and useful.
- Test Radix/`tw-animate-css` overlays as well as custom `.page-enter` utilities.
- Use Motion's `useReducedMotion()` or GSAP media-query scoping when those tools are present.

## Verification workflow

1. Capture the existing interaction at first paint, mid-motion when practical, and settled state.
2. Test keyboard, pointer, and touch-sized viewport behavior.
3. Test rapid repeated input, navigation interruption, dialog close/reopen, and data refetch.
4. Emulate reduced motion and verify a complete final state.
5. Inspect mobile and desktop in light and dark themes.
6. Check for layout shift, dropped frames, long tasks, detached loops, stale focus, and accidental
   horizontal scroll.
7. Run lint, typecheck, build, and relevant Playwright flows.

Use browser performance tooling for heavier work. For loops, canvas, or scroll effects, prove that
work pauses off-screen and cleans up on unmount.

## Quality gates

Do not sign off until:

- the motion brief ties movement to the screen's subject, audience, and job;
- one signature interaction carries emphasis and quiet regions remain quiet;
- every effect has a semantic role;
- each interaction uses the lightest layer that fully clears its visual bar;
- reduced motion, touch, focus, interruption, and async states are complete;
- no effect causes layout instability, stale focus, pointer blocking, or main-thread jank;
- off-screen/repeated work pauses and all effects clean up;
- the result fits the frontend's visual system in both themes and at mobile/desktop sizes;
- `npm run lint`, `npm run typecheck`, `npm run build`, and relevant flow tests pass.

## Handoff

Lead with what the motion now communicates. Name the chosen layer and why it earned the job, the
states and viewports checked, reduced-motion behavior, validation results, and any measured
performance risk. Do not summarize the animation as a list of library calls.
