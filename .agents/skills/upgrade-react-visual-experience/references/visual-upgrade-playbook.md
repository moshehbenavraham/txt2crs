# Visual upgrade playbook

Use this guide for substantial screen, flow, or system work. Keep the final implementation and
handoff proportional to the user's requested scope.

## Table of contents

- Evidence model
- Visual brief
- Audit frame
- Direction selection
- Screen blueprint
- System design
- Content and UX writing
- Responsive strategy
- Accessibility
- Implementation sequence
- Rendered QA matrix
- Anti-patterns
- Definition of done

## Evidence model

Separate:

- **Observed:** verified in source, rendered UI, supplied brand assets, tests, or current external
  evidence.
- **Inferred:** a reasoned interpretation, such as why hierarchy feels flat or why a flow appears
  high-risk.
- **Recommended:** the design or implementation decision.
- **Assumed:** missing input filled to keep work moving.
- **Unknown:** information that cannot be verified and would be dishonest to invent.

When studying competitors or references, preserve order and state. A CTA, proof element, or
interaction means something different depending on when it appears. Analyze real product screens
and flows, then translate patterns into an original system.

## Visual brief

Capture:

| Field | Question |
| --- | --- |
| Product | What does it help people accomplish? |
| Audience | Who uses it, and how sophisticated are they? |
| Screen job | What must this screen or flow make possible? |
| Primary action | What outcome should the user reach next? |
| Risk | What can go wrong or feel unsafe/confusing? |
| Content | What labels, values, tables, prose, and edge lengths are realistic? |
| Personality | Which 3–5 traits fit the product? |
| Existing equity | Which logo, colors, type, patterns, or user expectations should remain? |
| Constraints | What behavior, accessibility, performance, and technical rules apply? |
| Ambition | Refinement, focused redesign, or new direction? |

Turn the brief into a one-paragraph thesis:

> The interface should feel like **[quality] meets [quality]** because **[audience/job]**. It
> should avoid **[category trope]** and use **[type/grid/color/surface/content mechanism]** so users
> believe **[core belief]** before they **[primary action]**.

## Audit frame

Inspect five layers:

1. **Comprehension:** Can a user identify the page, status, primary action, and next step quickly?
2. **Hierarchy:** Do type, spacing, placement, contrast, and grouping agree about importance?
3. **System:** Are tokens and components consistent without making every surface identical?
4. **State:** Are loading, empty, error, success, permission, disabled, selected, and destructive
   states designed?
5. **Craft:** Are rhythm, alignment, optical balance, icon treatment, copy lengths, and motion
   intentional in both themes and across viewports?

For each issue, record evidence, user impact, scope, and the smallest system-level correction.
Avoid compiling a taste-based list of isolated class preferences.

## Direction selection

Define 3–7 load-bearing decisions. Strong decisions specify a mechanism and consequence:

- “Use an editorial display face only for page identity; keep controls and table headers in a
  compact grotesk so dense workflows remain legible.”
- “Reserve gold for earned emphasis and highlights; use forest green for action and selection so
  color roles do not compete.”
- “Use borders and tone shifts for default grouping; introduce shadow only for overlays and
  genuinely elevated surfaces.”
- “On mobile, transform header action rows into a clear primary button plus overflow menu instead
  of squeezing controls onto one line.”

When comparing concepts, vary a meaningful axis:

- editorial vs operational density;
- immersive brand shell vs quiet product shell;
- strong spatial asymmetry vs disciplined modular grid.

Do not present color swaps as distinct concepts.

## Screen blueprint

For each screen or component, write:

```text
Name:
User job:
Primary action:
Hierarchy:
Anatomy:
Representative content:
Desktop composition:
Mobile transformation:
Loading:
Empty:
Error and recovery:
Success:
Disabled/permission/destructive:
Keyboard/focus:
Motion role:
Evidence/rationale:
```

For multi-step flows, blueprint continuity between steps. Keep control names stable from intent to
confirmation (`Delete account` → `Deleting account…` → `Account deleted`).

## System design

### Typography

Assign roles before values:

- display/page identity;
- section/card heading;
- body and helper text;
- compact UI labels;
- technical/monospace values.

Justify why the roles belong together and to this product. Validate uppercase labels, numerals,
long emails, table values, code-like content, and 200% zoom. Avoid using display typography inside
dense controls merely to spread the brand everywhere.

### Color

Define semantic roles in both modes:

- background and elevated background;
- surface tiers;
- foreground and muted foreground;
- border and strong border;
- primary action and primary foreground;
- selection/accent;
- success, warning, danger, and information;
- chart series when applicable.

Check contrast in the actual paired colors and states. Do not claim WCAG conformance from OKLCH
lightness alone; measure or verify rendered combinations.

### Space, grid, and shape

Define:

- content width and page gutters;
- section rhythm and component density;
- grid behavior at breakpoints;
- radius hierarchy by component role;
- border vs shadow rules;
- overlay and sticky-layer z-index;
- mobile transformations, not only smaller spacing.

Use proximity before containers. A card must communicate grouping or interaction; it is not the
default wrapper for every block.

### Components and states

For each reusable pattern, define anatomy, variants, sizes, interactive states, async states,
responsive behavior, accessibility, and content limits. Compose the existing project primitives
instead of forking their semantics.

### Imagery and graphics

Use imagery only when it carries product meaning, brand atmosphere, demonstration, or proof.
Specify subject, crop, lighting, palette, and mobile art direction. Use project SVG/icon systems
for interface symbols. Generate bitmap art only when a custom raster asset is genuinely needed;
do not use generated art as filler.

## Content and UX writing

- Use nouns the user recognizes, not backend or implementation terminology.
- Label actions by outcome; avoid generic `Submit`, `Continue`, or `OK` where the result is known.
- Let labels label, examples demonstrate, helper text help, and status messages report state.
- Explain what belongs in an empty state and offer the next useful action.
- State what failed and how to recover; avoid vague apologies.
- Use representative long names, URLs, IDs, metadata, and validation errors while designing.
- Preserve tested copy unless changing the contract and tests is in scope.

## Responsive strategy

For each breakpoint, decide what:

- reflows;
- stacks;
- collapses into disclosure or overflow;
- becomes sticky;
- changes order;
- scrolls intentionally;
- truncates with a recovery path;
- becomes touch-first.

Test at 320–375px, around the sidebar/mobile boundary, and wide desktop. Avoid desktop card grids
that simply become an endless one-column list without reconsidering hierarchy.

For tables, choose deliberately among horizontal scroll, priority columns, stacked records, detail
drawers, or a hybrid. Preserve access to actions and identity fields.

## Accessibility

Validate:

- semantic heading order and landmarks;
- logical DOM/focus order after responsive reordering;
- keyboard access and visible focus;
- Radix overlay labels and focus containment;
- 44×44 practical touch targets for primary controls;
- text/UI contrast in both modes;
- errors associated with fields and recovery instructions;
- status updates announced when needed;
- zoom and reflow at 200%;
- reduced-motion completeness;
- icons with accessible names or `aria-hidden` as appropriate.

## Implementation sequence

1. Capture baseline renders and behavior.
2. Patch semantic tokens and global roles.
3. Build feature-level compositions from protected primitives.
4. Upgrade one representative route and all of its states.
5. Verify the direction in both themes and at mobile/desktop.
6. Propagate shared patterns through the remaining scope.
7. Remove dead one-off styles and duplicate raw values.
8. Update design documentation.
9. Run code validation and rendered QA.

Keep diffs reviewable. Avoid mixing an API/data refactor into a visual-system patch.

## Rendered QA matrix

| Surface | Desktop | Mobile | Light | Dark | Keyboard | Reduced motion |
| --- | --- | --- | --- | --- | --- | --- |
| Public/auth shell | required | required | required | required | required | if animated |
| Protected shell/sidebar | required | required | required | required | required | if animated |
| Target populated state | required | required | required | required | required | if animated |
| Loading/empty/error | required | required where distinct | required | required | as applicable | if animated |
| Dialog/menu/sheet | required | required | one mode minimum, both if token work | same | required | if animated |

Also inspect first paint, settled state, hover/pointer, touch, disabled, selected, success, and
destructive confirmation when applicable.

## Anti-patterns

- Generic “SaaS dashboard” composition unrelated to the product job.
- One giant restyle that leaves loading/error/empty states behind.
- Accent gradients, glass panels, glow, or noise used without a brand role.
- Cards inside cards, excessive pills, uniform large radii, or shadows at every level.
- Placeholder content that hides overflow and density problems.
- Light mode tuned carefully while dark mode merely inverts values.
- Mobile treated as desktop squeezed narrower.
- Muted text used below readable contrast.
- Pointer-only hover effects with no focus/touch equivalent.
- Renaming tested controls or changing behavior during a visual pass.
- Source-only sign-off without rendering the result.

## Definition of done

- The design thesis is visible in the rendered result.
- Hierarchy, content, tokens, and states form one coherent system.
- The direction is original and product-specific.
- Light/dark and mobile/desktop have intentional composition.
- Long, empty, loading, failure, permission, and destructive cases remain understandable.
- Accessibility and reduced-motion requirements are met.
- Generated/protected contracts are preserved.
- Rendered QA and the repository's lint, typecheck, build, and relevant flow tests pass.
