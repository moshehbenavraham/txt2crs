---
name: upgrade-react-visual-experience
description: Audit, art-direct, implement, and visually validate substantial UI upgrades in this repository's React 19, Vite, TanStack Router/Query, Tailwind CSS 4, and shadcn/Radix frontend. Use when redesigning or restyling pages, auth flows, dashboards, data tables, navigation, responsive layouts, themes, visual tokens, component compositions, empty/loading/error states, or a new visually driven frontend feature; when translating references into an original product-specific design; or when the user asks to make the frontend polished, premium, cohesive, distinctive, or production-ready. Preserve product behavior and project conventions. Pair with $orchestrate-react-motion when the work includes non-trivial route, layout, list, gesture, scroll, or shared-element motion. Do not use for Astro projects or copy-only changes with no visual impact.
---

# Upgrade the React Visual Experience

Create a coherent, product-specific interface and implement it in the existing frontend. Treat
visual quality as a system spanning content, hierarchy, tokens, components, responsive behavior,
states, accessibility, and rendered QA—not as a collection of decorative class changes.

## Load the project context

Read [`references/project-frontend-map.md`](references/project-frontend-map.md) before changing
frontend code. It identifies the current visual system, high-leverage files, protected/generated
areas, functional invariants, and known documentation drift.

For any redesign, new screen, cross-component restyle, or visual audit, also read the complete
[`references/visual-upgrade-playbook.md`](references/visual-upgrade-playbook.md). For a narrow
single-component polish task, load the sections that cover that component, its states, and QA.

If the task includes more than small CSS transitions, invoke `$orchestrate-react-motion` and
follow its motion brief, complexity ladder, and reduced-motion gates.

## Non-negotiable project rules

- Work in `frontend/`; do not introduce Astro, Astro islands, or Astro packages.
- Treat the current source as behavior truth. Treat `docs/frontend-ui-design.md` as design intent
  that may be stale, and update it when the implemented design system materially changes.
- Never edit `frontend/src/client/` or `frontend/src/routeTree.gen.ts`.
- Treat `frontend/src/components/ui/` as protected project primitives. Prefer token changes,
  composition, feature-level wrappers, and supported variants. Add shadcn components through the
  CLI. Modify a primitive directly only when the user explicitly authorizes reconciling that
  project rule.
- Preserve TanStack Router route structure, auth redirects, TanStack Query keys/invalidation,
  React Hook Form behavior, centralized Zod schemas, branded types, API error handling, accessible
  names, and existing `data-testid` hooks unless the task explicitly changes their contract.
- Use the established `cn()` utility, Tailwind CSS 4 token mappings, shadcn/Radix semantics,
  Lucide for product icons, and the existing theme provider.
- Design both light and dark modes as first-class states. Do not derive one as an afterthought.
- Meet WCAG 2.2 AA at minimum. Preserve keyboard operation and visible focus.
- Use realistic product copy and data shapes. Never validate a layout only with lorem ipsum,
  idealized one-line labels, or empty cards.
- Translate inspiration; never copy marks, proprietary imagery, copy, exact layouts, or a
  competitor's distinctive trade dress.

## Match the requested scope

Choose the smallest workflow that still proves the requested outcome:

- **Component polish:** inspect the component, every state, its consumers, both themes, and its
  smallest and largest realistic container.
- **Screen or flow upgrade:** inspect the route, shell, shared components, async/form states,
  navigation context, mobile behavior, and adjacent steps in the flow.
- **System redesign:** inspect all routes and primitives, define a design thesis and token changes,
  migrate representative screens first, then propagate the system and update design docs.
- **Strategy only:** provide an evidence-backed blueprint without changing code only when the user
  explicitly asks for direction, review, or a plan.

For implementation requests, implement the upgrade. Do not stop after producing a design memo.

## Workflow

### 1. Establish the visual brief

Extract or infer:

- product, audience, and the screen or flow's job;
- primary user action and the belief or information required before it;
- product personality, existing brand assets, and constraints;
- content density, domain vocabulary, realistic long/empty/error data, and localization risk;
- target viewports, input modes, themes, and accessibility needs;
- requested ambition: refinement, focused redesign, or new visual direction.

Ask only when a missing choice would materially change the result. Otherwise proceed with labeled
assumptions.

Write a one-paragraph design thesis and 3–7 load-bearing decisions. Define adjectives through
mechanisms: type contrast, density, grid, surface behavior, color roles, image treatment, and
interaction—not words such as “modern” or “premium” alone.

### 2. Inspect evidence before designing

Inspect the current route, shell, shared components, tokens, docs, assets, tests, and relevant API
data shape. Search consumers before changing shared styles.

Render the current UI when the environment can run. Capture or inspect:

- mobile, tablet, and desktop;
- light and dark themes;
- first paint, settled, hover/pointer, focus, touch, disabled, loading, empty, success, and error;
- short and long content;
- open overlays, menus, sheets, dialogs, and table overflow.

Record findings as:

- `Observed` for source or rendered facts;
- `Inferred` for reasoned judgments;
- `Recommended` for proposed changes.

If competitive or current-market evidence is necessary, browse real products in the same category.
Analyze structure, hierarchy, density, proof, and interaction; do not gather style-gallery
screenshots without product context.

### 3. Select one coherent direction

When a major layout or art-direction axis is unresolved, compare 2–3 compact concepts. Give each a
one-sentence premise and a small wireframe only when spatial comparison helps. Select one against
the brief, evidence, content, and responsive constraints.

Define:

- information hierarchy and screen order;
- typography roles and why they belong to this product;
- color, surface, border, shadow, and radius hierarchy;
- page grid, density, whitespace rhythm, and responsive transformations;
- imagery, illustration, icon, and data-visualization language;
- component anatomy and state behavior;
- UX-writing contract and action-name consistency;
- the one visual idea that makes the experience recognizable.

Avoid a generic dashboard template, indiscriminate cards, ornamental gradients, excessive pills,
uniform rounding, and an accent color applied everywhere.

### 4. Blueprint behavior and states

For each changed screen or component, specify:

- user job and primary action;
- anatomy and content priority;
- desktop and mobile composition;
- loading, empty, error, success, disabled, selected, and destructive states as applicable;
- focus order, keyboard behavior, accessible name, and recovery path;
- realistic copy/data constraints;
- motion role or an explicit decision to remain still.

Use outcome-specific actions (`Save changes`, `Create item`, `Send reset link`) and keep the same
action name through control, pending, success, and error states.

### 5. Implement from system to screen

Work in this order:

1. Correct or extend semantic tokens in `src/index.css`.
2. Reuse the current theme provider and Tailwind mappings.
3. Compose protected primitives into feature-level patterns.
4. Update the shell, route composition, and responsive structure.
5. Apply the new system to all in-scope states and adjacent flow steps.
6. Add purpose-built assets only when they serve the direction.
7. Update `docs/frontend-ui-design.md` when the system changes materially.

Prefer semantic token classes (`bg-background`, `text-muted-foreground`, `border-border`) over
repeated raw OKLCH values. Allow route-specific art direction, but keep shared roles centralized.

Do not let a broad restyle rewrite data fetching, validation, auth, or generated API contracts.
Separate behavioral changes from visual changes when practical so regressions are easy to isolate.

### 6. Run a rendered QA loop

Use a browser and iterate; source inspection alone cannot prove visual quality.

At minimum, inspect:

- 375×812 mobile and a desktop viewport around 1440×900;
- light and dark modes;
- keyboard focus and overlay focus containment;
- one populated state plus loading, empty, and error where the feature supports them;
- responsive header actions, tables, forms, dialogs, sidebar/sheet, and long text;
- animation-disabled or reduced-motion rendering for any moving UI.

Fix clipping, accidental scroll, weak hierarchy, inconsistent spacing, unreadable muted text,
layout shift, pointer-only affordances, touch targets below 44×44 where practical, and missing
state feedback. Keep screenshots or precise observations for material claims.

### 7. Validate the code

Run:

```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```

Run `npx playwright test` for changed user flows when the required backend/test environment is
available. Add focused visual or interaction assertions when they will prevent a real regression;
do not replace behavioral assertions with screenshots.

## Quality gates

Do not sign off until:

- the result is specific to the product, audience, and screen job;
- one coherent system governs type, color, surfaces, spacing, shape, and iconography;
- light/dark and mobile/desktop are designed, not merely functional;
- every in-scope async, form, permission, and destructive state is complete;
- realistic content does not break hierarchy or layout;
- controls remain semantic, keyboard-accessible, visibly focused, and WCAG 2.2 AA;
- shared styles use semantic tokens and do not create unexplained one-off values;
- the rendered result has been inspected at the required states and viewports;
- lint, typecheck, and build pass;
- functional contracts and generated files remain intact.

## Handoff

Lead with the implemented outcome. Briefly state the chosen design direction, the important files
or systems changed, rendered states/viewports checked, validation results, and any genuine
remaining risk. Do not narrate every class edit.
