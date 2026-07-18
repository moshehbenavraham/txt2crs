# Motion decision cheatsheet

Start with the motion brief, then stop at the first layer that fully expresses it.

## Motion brief

Name:

1. subject, audience, and screen job;
2. one signature interaction;
3. supporting roles and quiet regions;
4. semantic direction/order/continuity;
5. first paint, pending, settled, focus, pointer, touch, exit, interruption, error, and reduced
   states.

## Decision ladder

| Layer | Use when | Cost/risk |
| --- | --- | --- |
| Stillness | Reading, trust, comparison, or density benefits from no movement | None |
| CSS + Radix data states | Hover, press, focus, overlays, skeletons, small deterministic state changes | Lowest |
| Browser APIs | Small imperative sequences or off-screen/visibility control | Low; manual cleanup |
| TanStack Router view transition | Route continuity or a justified same-document shared surface | Browser-dependent; focus/old-new overlap |
| `motion/react` | Springs, layout projection, presence/exit, reorder, shared layout, gestures | New runtime dependency |
| GSAP | Custom synchronized timeline or scrollytelling that lighter layers cannot express | Highest authoring/payload risk |
| Media/WebGL | Cinematic media is itself the experience | Dedicated performance/accessibility project |

## Semantic role test

Keep an effect only if it provides at least one:

- **Orientation:** where the user is or where content came from.
- **Hierarchy:** what matters first.
- **Continuity:** how one state relates spatially to another.
- **Feedback:** that an action was accepted or completed.
- **Attention:** a time-sensitive change requiring notice.
- **Atmosphere:** a restrained product-specific mood in a designated region.

## State matrix

| State | Required decision |
| --- | --- |
| First paint | Content visible and stable without relying on animation completion |
| Pending | Honest progress/status without large layout shift |
| Settled | Crisp final pixels, no lingering `will-change` |
| Hover/pointer | Enhancement only; no exclusive information |
| Press | Immediate causal feedback |
| Focus | Visible, stable, and not obscured by transforms |
| Touch | Complete without hover and without delayed response |
| Exit | Preserve context; do not trap focus on disappearing UI |
| Interruption | Rapid repeat/navigation leaves a correct state |
| Error | Recovery remains obvious; motion does not distract |
| Reduced | Complete static or restrained alternative |

## Performance guardrails

- Prefer `transform` and `opacity`.
- Keep skeleton dimensions close to final content.
- Measure filters, blur, backdrop effects, masks, large shadows, and scroll handlers.
- Avoid permanent `will-change`.
- Pause off-screen loops/media and clean up observers, animation handles, and listeners.
- Do not animate routine query refetches like first-time page entrances.

## Project picks

- Existing default: CSS tokens, keyframes, `tw-animate-css`, and Radix data states.
- Route transitions: installed TanStack Router integration, not Astro or experimental React APIs.
- Rich React choreography: add `motion` only when the brief needs its strengths.
- Smooth scroll: avoid by default in this dashboard/data application.
- Complex cinematic timeline: GSAP only with an explicit performance and reduced-motion plan.
