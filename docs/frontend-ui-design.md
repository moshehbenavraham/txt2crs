# Frontend UI/UX Design System Documentation

> Comprehensive documentation of all UI/UX/design elements in the frontend application.
> **Aesthetic Direction**: Refined Editorial Luxury
> **Inspiration**: High-end editorial design (Monocle, Kinfolk), luxury tech (Apple, Porsche Digital), contemporary art galleries
> Last updated: 2025-12-22

## Table of Contents

1. [Design Philosophy](#1-design-philosophy)
2. [Tech Stack Overview](#2-tech-stack-overview)
3. [Typography System](#3-typography-system)
4. [Color System](#4-color-system)
5. [Motion & Animation System](#5-motion--animation-system)
6. [Spatial Composition & Layout](#6-spatial-composition--layout)
7. [Shadow & Texture System](#7-shadow--texture-system)
8. [Component Library](#8-component-library)
9. [Assets](#9-assets)
10. [Pages & Routes](#10-pages--routes)
11. [Responsive Design](#11-responsive-design)
12. [Accessibility](#12-accessibility)
13. [Testing Checklist](#13-testing-checklist)
14. [Inventory Summary](#14-inventory-summary)

---

## 1. Design Philosophy

### Core Principles

1. **Confidence Through Restraint**
   - Luxury doesn't shout. Every element must earn its presence.
   - Remove the unnecessary; amplify what remains.

2. **Typography as Architecture**
   - Type carries 80% of the personality. It's not decoration—it's structure.
   - Contrast between display and body creates rhythm.

3. **Depth Without Clutter**
   - Layers, shadows, and subtle textures create dimensionality.
   - Never busy; always rich.

4. **Motion as Choreography**
   - Animation should feel inevitable, not decorative.
   - Orchestrated reveals > scattered micro-interactions.

5. **The Detail is the Design**
   - Micro-details (borders, shadows, spacing) distinguish luxury from ordinary.
   - 1px matters.

---

## 2. Tech Stack Overview

### Core Libraries

| Package | Version | Purpose |
|---------|---------|---------|
| `react` | 19.2.7 | UI framework |
| `react-dom` | 19.2.7 | DOM rendering |
| `@tanstack/react-router` | 1.170.18 | File-based routing |
| `@tanstack/react-query` | 5.101.2 | Server state management |
| `@tanstack/react-table` | 8.21.3 | Table/DataGrid library |
| `@radix-ui/*` | Latest | Unstyled accessible components |
| `react-hook-form` | 7.81.0 | Form state management |
| `@hookform/resolvers` | 5.4.0 | Form validation resolvers |
| `zod` | 4.4.3 | Schema validation |
| `tailwindcss` | 4.3.3 | Utility CSS framework |
| `class-variance-authority` | 0.7.1 | CVA variant system |
| `clsx` | 2.1.1 | Conditional className utility |
| `tailwind-merge` | 3.6.0 | Tailwind class merging |
| `lucide-react` | 1.25.0 | Primary icon library |
| `react-icons` | 5.7.0 | Secondary icon library (social) |
| `sonner` | 2.0.7 | Toast notifications |
| `next-themes` | 0.4.6 | Theme management (sonner) |
| `tw-animate-css` | 1.4.0 | Animation utilities |

### Build Tools

| Tool | Version | Purpose |
|------|---------|---------|
| `vite` | 8.1.5 | Build tool & dev server |
| `typescript` | 7.0.2 | Type checking |
| `@biomejs/biome` | 2.5.4 | Linting & formatting |
| `@vitejs/plugin-react` | 6.0.3 | React compilation |

### Configuration

**File**: `frontend/components.json`

```json
{
  "style": "new-york",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/index.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "iconLibrary": "lucide"
}
```

---

## 3. Typography System

### Font Stack

```css
/* Display Font - Headlines, Navigation, Feature Numbers */
--font-display: "Playfair Display", Georgia, serif;

/* Body Font - UI Text, Paragraphs, Forms */
--font-body: "Outfit", system-ui, sans-serif;

/* Mono Font - Code, Data, Technical Values */
--font-mono: "JetBrains Mono", monospace;
```

### Font Loading Strategy

**File**: `frontend/index.html`

```html
<!-- Google Fonts with display=swap for performance -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Outfit:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### Typography Scale

| Role | Font | Weight | Size | Letter Spacing | Use Case |
|------|------|--------|------|----------------|----------|
| **Display XL** | Playfair Display | 600 | 48px/3rem | -0.02em | Hero headlines |
| **Display L** | Playfair Display | 500 | 32px/2rem | -0.01em | Page titles |
| **Display M** | Playfair Display | 500 | 24px/1.5rem | -0.01em | Section headers |
| **Heading** | Outfit | 600 | 18px/1.125rem | -0.01em | Card titles, nav items |
| **Body** | Outfit | 400 | 15px/0.9375rem | 0 | Primary text |
| **Body Small** | Outfit | 400 | 13px/0.8125rem | 0.01em | Secondary text |
| **Caption** | Outfit | 500 | 11px/0.6875rem | 0.05em | Labels, badges |
| **Mono** | JetBrains Mono | 400 | 13px | 0 | Code, data values |

### Typography CSS Variables

```css
:root {
  /* Font Families */
  --font-display: "Playfair Display", Georgia, serif;
  --font-body: "Outfit", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;

  /* Font Sizes */
  --text-display-xl: 3rem;
  --text-display-lg: 2rem;
  --text-display-md: 1.5rem;
  --text-heading: 1.125rem;
  --text-body: 0.9375rem;
  --text-body-sm: 0.8125rem;
  --text-caption: 0.6875rem;

  /* Line Heights */
  --leading-tight: 1.1;
  --leading-snug: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;

  /* Letter Spacing */
  --tracking-tighter: -0.02em;
  --tracking-tight: -0.01em;
  --tracking-normal: 0;
  --tracking-wide: 0.01em;
  --tracking-wider: 0.05em;
}
```

---

## 4. Color System

### Philosophy

A **warm neutral foundation** with **deep, confident accent colors**. The palette evokes:
- Aged paper and dark walnut wood
- Champagne gold and graphite
- Deep forest greens and midnight blues

### Light Mode Palette

**File**: `frontend/src/index.css`

| Token | Value | Description |
|-------|-------|-------------|
| `--background` | `oklch(0.985 0.005 85)` | Warm off-white |
| `--background-elevated` | `oklch(0.99 0.003 85)` | Paper white |
| `--foreground` | `oklch(0.18 0.01 60)` | Rich charcoal |
| `--surface-1` | `oklch(0.975 0.006 85)` | Subtle cream |
| `--surface-2` | `oklch(0.965 0.008 85)` | Light parchment |
| `--surface-3` | `oklch(0.95 0.01 80)` | Warm gray |
| `--primary` | `oklch(0.35 0.08 160)` | **Deep Forest Green** |
| `--primary-hover` | `oklch(0.40 0.09 160)` | Lighter forest |
| `--primary-foreground` | `oklch(0.98 0.005 85)` | Cream white |
| `--accent` | `oklch(0.75 0.12 85)` | **Champagne Gold** |
| `--accent-hover` | `oklch(0.70 0.14 85)` | Deeper gold |
| `--accent-muted` | `oklch(0.85 0.06 85)` | Soft gold |
| `--secondary` | `oklch(0.55 0.01 60)` | Graphite |
| `--secondary-foreground` | `oklch(0.98 0.005 85)` | Cream |
| `--muted` | `oklch(0.94 0.005 80)` | Light warm gray |
| `--muted-foreground` | `oklch(0.50 0.01 60)` | Medium gray |
| `--border` | `oklch(0.90 0.008 80)` | Subtle warm border |
| `--border-strong` | `oklch(0.82 0.01 75)` | Defined border |
| `--ring` | `oklch(0.35 0.08 160 / 0.3)` | Focus ring |
| `--success` | `oklch(0.55 0.15 155)` | Deep teal green |
| `--warning` | `oklch(0.70 0.15 70)` | Amber |
| `--destructive` | `oklch(0.50 0.18 25)` | Deep burgundy |
| `--info` | `oklch(0.50 0.10 250)` | Slate blue |

### Dark Mode Palette

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
| `--primary-foreground` | `oklch(0.98 0.005 85)` | Cream |
| `--accent` | `oklch(0.78 0.14 85)` | Luminous gold |
| `--accent-hover` | `oklch(0.82 0.15 85)` | Brighter gold |
| `--accent-muted` | `oklch(0.65 0.08 80)` | Subdued gold |
| `--secondary` | `oklch(0.65 0.01 60)` | Light graphite |
| `--secondary-foreground` | `oklch(0.14 0.01 60)` | Dark |
| `--muted` | `oklch(0.22 0.01 55)` | Dark muted |
| `--muted-foreground` | `oklch(0.60 0.01 60)` | Muted text |
| `--border` | `oklch(1 0 0 / 0.08)` | Subtle light border |
| `--border-strong` | `oklch(1 0 0 / 0.15)` | Defined border |
| `--ring` | `oklch(0.55 0.10 160 / 0.4)` | Focus ring |
| `--success` | `oklch(0.65 0.15 155)` | Bright teal |
| `--warning` | `oklch(0.75 0.15 70)` | Bright amber |
| `--destructive` | `oklch(0.60 0.18 25)` | Bright burgundy |
| `--info` | `oklch(0.60 0.10 250)` | Bright slate |

### Chart Colors (Data Visualization)

**Light Mode:**
- `--chart-1`: `oklch(0.35 0.08 160)` - Forest green
- `--chart-2`: `oklch(0.75 0.12 85)` - Champagne gold
- `--chart-3`: `oklch(0.50 0.10 250)` - Slate blue
- `--chart-4`: `oklch(0.60 0.15 30)` - Terracotta
- `--chart-5`: `oklch(0.55 0.15 155)` - Teal

**Dark Mode:**
- `--chart-1`: `oklch(0.55 0.10 160)` - Bright forest
- `--chart-2`: `oklch(0.78 0.14 85)` - Luminous gold
- `--chart-3`: `oklch(0.60 0.10 250)` - Bright slate
- `--chart-4`: `oklch(0.65 0.15 30)` - Bright terracotta
- `--chart-5`: `oklch(0.65 0.15 155)` - Bright teal

### Sidebar Colors

| Token | Light Mode | Dark Mode |
|-------|------------|-----------|
| `--sidebar` | `oklch(0.975 0.006 85)` | `oklch(0.17 0.01 60)` |
| `--sidebar-foreground` | `oklch(0.18 0.01 60)` | `oklch(0.92 0.01 85)` |
| `--sidebar-primary` | `oklch(0.35 0.08 160)` | `oklch(0.55 0.10 160)` |
| `--sidebar-primary-foreground` | `oklch(0.98 0.005 85)` | `oklch(0.98 0.005 85)` |
| `--sidebar-accent` | `oklch(0.94 0.005 80)` | `oklch(0.22 0.01 55)` |
| `--sidebar-accent-foreground` | `oklch(0.18 0.01 60)` | `oklch(0.92 0.01 85)` |
| `--sidebar-border` | `oklch(0.90 0.008 80)` | `oklch(1 0 0 / 0.08)` |
| `--sidebar-ring` | `oklch(0.35 0.08 160 / 0.3)` | `oklch(0.55 0.10 160 / 0.4)` |

### Theme Provider

**File**: `frontend/src/components/theme-provider.tsx`

```typescript
type Theme = "dark" | "light" | "system"

// Features:
// - Default: "system" (follows OS preference)
// - Storage: localStorage with key "vite-ui-theme"
// - Applies "light"/"dark" class to document.documentElement
// - Listens to prefers-color-scheme media query changes

// Usage:
const { theme, resolvedTheme, setTheme } = useTheme()
```

---

## 5. Motion & Animation System

### Philosophy

Every effect has a semantic role: orientation, hierarchy, continuity, feedback,
or attention. Dense reading and comparison regions (tables, record lists, forms,
destructive confirmations) stay still. There is exactly one signature moment:
the dashboard's library surface continues into the Items workspace.

### Motion Role Tokens

Durations are semantic roles, not arbitrary literals. Legacy `--duration-*`
names remain as compatibility aliases.

```css
:root {
  /* Easing Curves */
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
  --ease-in-out-quart: cubic-bezier(0.76, 0, 0.24, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);

  /* Motion Roles */
  --motion-duration-feedback: 120ms;  /* press, selection */
  --motion-duration-state: 180ms;     /* hover, small state changes */
  --motion-duration-overlay: 260ms;   /* dialogs, menus, reveals */
  --motion-duration-route: 320ms;     /* scoped route continuity */
  --motion-distance-sm: 4px;
  --motion-distance-md: 8px;

  /* Legacy aliases */
  --duration-instant: var(--motion-duration-feedback);
  --duration-fast: var(--motion-duration-state);
  --duration-normal: var(--motion-duration-overlay);
  --duration-slow: var(--motion-duration-route);
  --duration-slower: 700ms;
}
```

### Core Animations

Only keyframes with live consumers exist:

```css
@keyframes fadeInUp { /* auth shell entrance (AuthLayout) */ }
@keyframes luxuryShimmer { /* ui/skeleton shimmer */ }
@keyframes riseIn { /* dashboard section settle, capped at --motion-distance-md */ }
@keyframes rowHighlight { /* brief emphasis on a newly created preview row */ }
```

### Semantic Reveal Groups

The old outlet-level `.page-enter` replay and `nth-child` stagger were removed.
The dashboard settles in explicit reading order — header, library status, then
preview/actions — capped at three groups and wrapped in
`prefers-reduced-motion: no-preference`:

```css
@media (prefers-reduced-motion: no-preference) {
  .reveal-group { animation: riseIn var(--motion-duration-overlay) var(--ease-out-quart) both; }
  .reveal-delay-1 { animation-delay: 0ms; }
  .reveal-delay-2 { animation-delay: 70ms; }
  .reveal-delay-3 { animation-delay: 140ms; }
}
```

Routine query refetches never replay entrances; content updates in place.

### Route Continuity (View Transition)

The only route transition is scoped to the Dashboard → Items "Open library"
navigation, using TanStack Router's built-in `viewTransition` link option
(no new motion dependency). The dashboard preview and the Items table share
`view-transition-name: library-surface`; the sidebar and command strip claim
their own names so the shell stays stable. Unsupported browsers navigate
normally. `usePrefersReducedMotion()` disables the transition in JavaScript.

### Reduced Motion Support

A project-wide safety clamp resolves every animation and transition — custom
utilities, Radix state animations, `tw-animate-css`, shimmer loops, and theme
icons — instantly to its complete final state:

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
  ::view-transition-new(*) {
    animation: none !important;
  }
}
```

---

## 6. Spatial Composition & Layout

### Spacing System

```css
:root {
  /* Base spacing unit: 4px */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */

  /* Container widths */
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
  --container-2xl: 1400px;

  /* Layout roles (shell-level, not route accidents) */
  --space-page-inline: clamp(1.25rem, 3vw, 3rem); /* page gutter */
  --space-section: clamp(2rem, 4vw, 3.5rem);      /* section rhythm */
}
```

### Border Radius System

| Token | Value | Pixels |
|-------|-------|--------|
| `--radius-sm` | `0.5rem` | 8px |
| `--radius-md` | `0.75rem` | 12px |
| `--radius-lg` | `1rem` | 16px |
| `--radius-xl` | `1.25rem` | 20px |

### Layout Philosophy

1. **Generous Whitespace**: Space is luxury. Don't fill every pixel.
2. **Asymmetric Balance**: Avoid perfect symmetry; create visual tension.
3. **Clear Hierarchy**: Size and position communicate importance.
4. **Breathing Room**: Elements need space to be appreciated.

### Page Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  SIDEBAR (280px)  │          MAIN CONTENT                       │
│                   │                                              │
│  ┌─────────────┐  │  ┌────────────────────────────────────────┐ │
│  │    LOGO     │  │  │  PAGE HEADER                           │ │
│  └─────────────┘  │  │  ─────────────────                     │ │
│                   │  │  Display Title         [Actions]       │ │
│  Navigation       │  └────────────────────────────────────────┘ │
│  ─────────────    │                                              │
│  • Dashboard      │  ┌────────────────────────────────────────┐ │
│  • Search         │  │                                        │ │
│  • Extract        │  │           CONTENT AREA                 │ │
│  • Crawl          │  │                                        │ │
│                   │  │      max-width: max-w-6xl              │ │
│  ─────────────    │  │      gutter: --space-page-inline       │ │
│  Settings         │  │                                        │ │
│                   │  └────────────────────────────────────────┘ │
│  ┌─────────────┐  │                                              │
│  │   USER      │  │  (no footer in the protected workspace;      │
│  └─────────────┘  │   social links live on auth surfaces)        │
└─────────────────────────────────────────────────────────────────┘
```

### Main Application Layout

**File**: `frontend/src/routes/_layout.tsx`

The sticky 56px command strip carries the sidebar trigger (44×44 on mobile), a
compact brand mark below `md`, and the current section label. `SidebarInset`
renders the single `main` landmark, so route content uses a plain `div`. The
protected workspace has no footer; social links stay on auth surfaces.

```typescript
<SidebarProvider>
  <AppSidebar /> {/* [view-transition-name:app-sidebar] */}
  <SidebarInset>
    <header className="sticky top-0 z-10 flex h-14 shrink-0 items-center gap-2 border-b border-border/50 px-3 md:px-4 bg-background/80 backdrop-blur-sm [view-transition-name:command-strip]">
      <SidebarTrigger className="size-11 md:size-7 -ml-1 ..." />
      <Logo variant="icon" className="md:hidden" />
      <SectionLabel />
    </header>
    <div className="flex-1 px-(--space-page-inline) py-6 md:py-10">
      <div className="mx-auto max-w-6xl">
        <Outlet />
      </div>
    </div>
  </SidebarInset>
</SidebarProvider>
```

### Auth Layout

**File**: `frontend/src/components/Common/AuthLayout.tsx`

Features:
- Gradient mesh background with noise texture overlay
- 2-column grid (logo left, form right) on desktop
- Single column on mobile
- Decorative accent border on logo panel
- Page entrance animations

### Common Layout Patterns

| Pattern | Classes | Use Case |
|---------|---------|----------|
| Form Grid | `grid gap-4 sm:grid-cols-2` or `sm:grid-cols-3` | Form layouts |
| Form Item | `grid gap-2` | Field wrapper |
| Page Header | `Common/PageHeader.tsx` composition | Eyebrow, one `h1`, description, wrapping action group; stacks below `sm` |
| Card Layout | `flex flex-col gap-6` | Vertical content |
| Table Wrapper | `relative w-full overflow-hidden rounded-2xl border` | Responsive tables |
| Button Group | `flex w-fit items-stretch` | Grouped buttons |

---

## 7. Shadow & Texture System

### Shadow System

```css
:root {
  /* Layered shadow system for depth */
  --shadow-xs: 0 1px 2px oklch(0 0 0 / 0.04);

  --shadow-sm:
    0 1px 2px oklch(0 0 0 / 0.02),
    0 2px 4px oklch(0 0 0 / 0.04);

  --shadow-md:
    0 1px 2px oklch(0 0 0 / 0.02),
    0 4px 8px oklch(0 0 0 / 0.04),
    0 8px 16px oklch(0 0 0 / 0.04);

  --shadow-lg:
    0 1px 2px oklch(0 0 0 / 0.02),
    0 4px 8px oklch(0 0 0 / 0.03),
    0 12px 24px oklch(0 0 0 / 0.06),
    0 24px 48px oklch(0 0 0 / 0.06);

  --shadow-xl:
    0 2px 4px oklch(0 0 0 / 0.02),
    0 8px 16px oklch(0 0 0 / 0.04),
    0 24px 48px oklch(0 0 0 / 0.08),
    0 48px 96px oklch(0 0 0 / 0.08);

  /* Accent shadow for CTAs */
  --shadow-accent:
    0 4px 14px oklch(0.35 0.08 160 / 0.25),
    0 8px 24px oklch(0.35 0.08 160 / 0.15);
}

.dark {
  --shadow-xs: 0 1px 2px oklch(0 0 0 / 0.2);
  --shadow-sm: 0 2px 8px oklch(0 0 0 / 0.3);
  --shadow-md: 0 4px 16px oklch(0 0 0 / 0.4);
  --shadow-lg: 0 8px 32px oklch(0 0 0 / 0.5);
  --shadow-xl: 0 16px 64px oklch(0 0 0 / 0.6);
  --shadow-accent:
    0 4px 14px oklch(0.55 0.10 160 / 0.3),
    0 8px 24px oklch(0.55 0.10 160 / 0.2);
}
```

### Background Treatments

```css
/* Subtle noise texture overlay */
.texture-noise::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,...");
  opacity: 0.03;
  pointer-events: none;
  mix-blend-mode: overlay;
}

/* Gradient mesh background (used in AuthLayout) */
.bg-gradient-mesh {
  background:
    radial-gradient(at 40% 20%, var(--accent-muted) 0px, transparent 50%),
    radial-gradient(at 80% 0%, var(--primary) 0px, transparent 40%),
    radial-gradient(at 0% 50%, var(--surface-2) 0px, transparent 50%),
    var(--background);
}

/* Elegant separator line */
.separator-elegant {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-strong), transparent);
  border: none;
}
```

---

## 8. Component Library

### UI Components (25 total)

**Location**: `frontend/src/components/ui/`

#### Button Component

**File**: `frontend/src/components/ui/button.tsx`

**Variants**:
- `default` (primary): Deep forest green with accent shadow, hover lift
- `secondary`: Surface background with border
- `outline`: Border only with transparent background
- `ghost`: No background, text only
- `accent`: Champagne gold background
- `destructive`: Deep burgundy for dangerous actions
- `link`: Underlined text link style

**Sizes**:
- `sm`: h-9, px-4, rounded-lg
- `default`: h-11, px-6, rounded-xl
- `lg`: h-13, px-8, rounded-xl
- `icon`: 40x40, rounded-xl
- `icon-sm`: 32x32
- `icon-lg`: 44x44

#### Card Component

**File**: `frontend/src/components/ui/card.tsx`

**Variants**:
- `default`: Surface-1 background, subtle border, small shadow
- `elevated`: Surface-2, stronger shadow, hover lift effect
- `feature`: Gradient background, decorative accent line at top
- `interactive`: Cursor pointer, hover animations
- `muted`: Subdued styling for secondary content

#### Input/Textarea Components

Features:
- Height: 48px (h-12)
- Border radius: rounded-xl (16px)
- Surface-1 background
- Primary border on focus with ring
- Destructive border on invalid
- Smooth transitions (200ms)

#### Table Component

**File**: `frontend/src/components/ui/table.tsx`

Features:
- Rounded-2xl container with border
- Surface-2 header background
- Uppercase, tracked header text
- Hover row highlighting
- Proper vertical alignment

#### Badge Component

**File**: `frontend/src/components/ui/badge.tsx`

**Variants**:
- `default`: Primary background
- `secondary`: Muted background
- `outline`: Border only
- `destructive`: Burgundy/red
- `success`: Teal green
- `warning`: Amber
- `info`: Slate blue
- `accent`: Champagne gold

#### Alert Component

**File**: `frontend/src/components/ui/alert.tsx`

**Variants**:
- `default`: Standard info styling
- `destructive`: Error/danger
- `success`: Success messaging
- `warning`: Warning/caution
- `info`: Informational
- `accent`: Highlighted info

#### Dialog Component

**File**: `frontend/src/components/ui/dialog.tsx`

Features:
- Backdrop blur overlay
- Display typography for titles
- Large shadow (shadow-xl)
- Refined close button with hover state
- Smooth entrance/exit animations

#### Skeleton Component

**File**: `frontend/src/components/ui/skeleton.tsx`

Features:
- Luxury shimmer animation (2s ease-in-out)
- Gradient from muted through surface-2
- 200% background-size for smooth movement

#### Sonner (Toast) Component

**File**: `frontend/src/components/ui/sonner.tsx`

Features:
- Semantic color support (success, warning, error, info)
- Outfit font family
- Proper shadow depth
- Theme-aware styling

### Common Components

**Location**: `frontend/src/components/Common/`

| Component | File | Description |
|-----------|------|-------------|
| **Logo** | `Logo.tsx` | Theme-aware logo with full/icon/responsive variants, smooth transitions |
| **AuthLayout** | `AuthLayout.tsx` | Gradient mesh background, noise texture, entrance animations |
| **PageHeader** | `PageHeader.tsx` | Shared page identity: eyebrow, `h1`, description, responsive action group |
| **Footer** | `Footer.tsx` | Auth-surface footer with social links (not rendered in the protected shell) |
| **Appearance** | `Appearance.tsx` | Theme switcher (sidebar and standalone) |
| **DataTable** | `DataTable.tsx` | TanStack React Table with pagination; optional `renderMobileRow` renders a feature-specific record list below `md` from the same paginated row model |
| **ErrorComponent** | `ErrorComponent.tsx` | Error boundary display |
| **NotFound** | `NotFound.tsx` | 404 page |

### Sidebar Components

**Location**: `frontend/src/components/Sidebar/`

| Component | File | Description |
|-----------|------|-------------|
| **AppSidebar** | `AppSidebar.tsx` | Wider sidebar, refined group labels, luxury styling |
| **Main** | `Main.tsx` | Navigation items; quiet active treatment (surface tint + forest index keyline via `--surface-selected`), `aria-current` from router links |
| **User** | `User.tsx` | Refined avatar, better dropdown typography |

---

## 9. Assets

### Icon Libraries

**Primary**: Lucide React (`lucide-react@1.25.0`)

Common icons used:
- Navigation: `Home`, `Briefcase`, `Search`, `FileText`, `Globe`, `Network`, `Users`
- UI: `ChevronDown`, `ChevronUp`, `ChevronLeft`, `ChevronRight`, `X`
- Actions: `ExternalLink`, `Eye`, `EyeOff`, `Sun`, `Moon`, `Monitor`, `Copy`
- Status: `Check`, `AlertTriangle`, `Info`, `Loader2`

**Secondary**: React Icons (`react-icons@5.7.0`)

Used in Footer for social links:
- `FaGithub`
- `FaLinkedinIn`
- `FaYoutube`

### SVG Assets

**Location**: `frontend/public/assets/images/`

| File | Description | Dimensions |
|------|-------------|------------|
| `apex-logo.svg` | Dark mode full logo | 200x40 viewBox |
| `apex-logo-light.svg` | Light mode full logo | 200x40 viewBox |
| `apex-icon.svg` | Dark mode icon | Square |
| `apex-icon-light.svg` | Light mode icon | Square |
| `favicon.png` | Browser favicon | - |

### Logo Component

**File**: `frontend/src/components/Common/Logo.tsx`

```typescript
interface LogoProps {
  variant?: "full" | "icon" | "responsive"
  className?: string
  asLink?: boolean  // Wraps in Link to "/" when true
}

// Features:
// - Theme-aware (switches between light/dark logos)
// - Smooth transitions on hover
// - Responsive variant for sidebar collapse detection
```

---

## 10. Pages & Routes

### Route Structure

**Authentication Routes** (public):

| Route | File | Description |
|-------|------|-------------|
| `/login` | `login.tsx` | Display typography, refined spacing, elegant links |
| `/signup` | `signup.tsx` | Consistent luxury styling with login |
| `/recover-password` | `recover-password.tsx` | Refined messaging and typography |
| `/reset-password` | `reset-password.tsx` | Consistent styling across auth flows |

**Protected Routes** (`/_layout` - requires auth):

| Route | File | Description |
|-------|------|-------------|
| `/` | `_layout/index.tsx` | Workspace overview: numbered library index (status, preview, role-aware actions) |
| `/items` | `_layout/items.tsx` | Items management with DataTable |
| `/settings` | `_layout/settings.tsx` | User settings (tabbed interface) |
| `/admin` | `_layout/admin.tsx` | Admin panel (superuser only) |

### Page Header Pattern

All product routes (Dashboard, Items, Admin, Settings) use the shared
`Common/PageHeader.tsx` composition:

```tsx
<PageHeader
  eyebrow="Workspace"          // optional section eyebrow
  title="Workspace overview"   // the page's single h1 (Playfair Display)
  description="..."            // concise supporting copy, max-w-prose
  actions={<...>}              // wrapping action group
/>
```

Below `sm` the identity and actions stack with stretched full-width controls;
above `sm` they align at the bottom edge. Fixed-width controls must never
squeeze the description into a word column.

### Dashboard Composition

The dashboard (`_layout/index.tsx`) is an editorial workspace index, not a KPI
grid. Components live in `frontend/src/components/Dashboard/`:

| Component | Purpose |
|-----------|---------|
| `WorkspaceHeader` | Page identity + `Create item` / `Open library` actions; the user's name appears in supporting copy, never as the title |
| `LibraryIndex` | Numbered sections: 01 Library status (exact `count`), 02 Library preview, 03 Workspace actions or Administration (role-aware) |
| `LibraryPreview` | Compact record rows labeled a preview — the API documents no recency order, so no "recent" or trend language |
| `DashboardEmpty` | "Start your workspace" onboarding replacing zero-value modules |
| `Pending/PendingDashboard` | Static, geometry-matched placeholders (no shimmer) |

Data errors render an inline "We could not load your library" surface with
`Try again`; non-auth errors never redirect to Login.

### Form Handling

**Pattern**: React Hook Form + Zod

```typescript
const form = useForm<FormData>({
  resolver: zodResolver(schema),
  mode: "onBlur",
  criteriaMode: "all",
  defaultValues: {...}
})
```

---

## 11. Responsive Design

### Breakpoints (Tailwind Default)

| Breakpoint | Width | Use Case |
|------------|-------|----------|
| `sm:` | 640px | Small devices |
| `md:` | 768px | Medium devices (tablets) |
| `lg:` | 1024px | Large devices (desktop) |
| `xl:` | 1280px | Extra large displays |

### Responsive Patterns

| Pattern | Mobile | Desktop |
|---------|--------|---------|
| Form Grid | Single column | 2-3 columns (`sm:grid-cols-2`) |
| Flex Direction | `flex-col` | `sm:flex-row` |
| Sidebar | Sheet overlay | Persistent sidebar |
| Logo | Icon only | Full logo |
| Page Padding | `p-6` | `md:p-8 lg:p-12` |
| Table | Horizontal scroll | Full width |
| Auth Layout | Single column | 2-column grid |

### Mobile-Specific Features

**Sidebar:**
- Uses Sheet component as overlay on mobile
- Closes on navigation
- Trigger button in header

**Hook**: `useMobile()` / `useIsMobile()`
- Detects mobile viewport (< 768px)
- Used by Sidebar component

---

## 12. Accessibility

### Implemented Features

| Feature | Status | Notes |
|---------|--------|-------|
| **Reduced Motion** | ✅ | `@media (prefers-reduced-motion)` support |
| **Focus States** | ✅ | All buttons/inputs have visible `focus-visible` rings |
| **Aria Labels** | ✅ | Interactive elements have proper labels |
| **Alt Text** | ✅ | All images have alt attributes |
| **Color Contrast** | ✅ | Primary text meets WCAG AA (7:1 ratio) |
| **Keyboard Navigation** | ✅ | All interactive elements are keyboard accessible |

### Color Contrast Ratios

- **Primary text** (L=0.18) on **background** (L=0.985): **7:1** (WCAG AAA)
- **Muted foreground** (L=0.50) on **background** (L=0.985): **4.5:1** (WCAG AA)
- **Primary button text** (L=0.98) on **primary** (L=0.35): **5.5:1** (WCAG AA)

---

## 13. Testing Checklist

### Automated Tests (Passing)

- ✅ Production build succeeds (Vite 8.1.5, 2194 modules)
- ✅ Biome lint check passes (109 files)
- ✅ TypeScript type check passes (`tsc --noEmit`)

### Manual Testing Required

#### Visual Testing
- [ ] Light mode: Verify all pages display correctly
- [ ] Dark mode: Toggle and verify all pages display correctly
- [ ] Responsive: Test at mobile (375px), tablet (768px), desktop (1280px)
- [ ] Typography: Verify fonts load (Playfair Display, Outfit, JetBrains Mono)
- [ ] Animations: Verify page entrance animations are smooth

#### Functional Testing
- [ ] Items page: Create, edit, delete items, filtering
- [ ] Settings page: Update profile, change password
- [ ] Admin page: User management (superuser only)
- [ ] Auth pages: Login, signup, password recovery flows

#### Accessibility Testing
- [ ] Keyboard navigation: Tab through all interactive elements
- [ ] Screen reader: Test with VoiceOver/NVDA on key pages
- [ ] Color contrast: Verify muted-foreground text is readable
- [ ] Reduced motion: Enable "reduce motion" in OS, verify animations disabled

#### Browser Testing
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

---

## 14. Inventory Summary

| Category | Count | Details |
|----------|-------|---------|
| **UI Components** | 25 | Button, Input, Form, Table, Dialog, Card, etc. |
| **Common Components** | 7 | Logo, Footer, AuthLayout, DataTable, etc. |
| **Sidebar Components** | 3 | AppSidebar, Main, User |
| **Routes/Pages** | 8 | Auth (4), Protected (4) |
| **Icons** | 50+ | Lucide (primary), React Icons (social) |
| **SVG Assets** | 5 | Logos, icons, favicon |
| **Color Tokens** | 50+ | Foundation, semantic, chart, sidebar |
| **Typography Styles** | 8 | Display XL/L/M, Heading, Body, Caption, Mono |
| **Animation Keyframes** | 6 | fadeInUp, fadeInScale, slideInFromRight, etc. |
| **Shadow Levels** | 6 | xs, sm, md, lg, xl, accent |

---

## File Structure Overview

```
frontend/
├── public/
│   └── assets/
│       └── images/
│           ├── apex-logo.svg
│           ├── apex-logo-light.svg
│           ├── apex-icon.svg
│           ├── apex-icon-light.svg
│           └── favicon.png
├── src/
│   ├── components/
│   │   ├── ui/                    # 25 UI components
│   │   ├── Common/                # Shared components
│   │   ├── Sidebar/               # Navigation components
│   │   ├── Admin/                 # Admin page components
│   │   ├── Items/                 # Items page components
│   │   └── UserSettings/          # Settings components
│   ├── routes/
│   │   ├── __root.tsx             # Root layout
│   │   ├── _layout.tsx            # Protected layout
│   │   ├── _layout/               # Protected pages
│   │   ├── login.tsx
│   │   ├── signup.tsx
│   │   ├── recover-password.tsx
│   │   └── reset-password.tsx
│   ├── hooks/                     # Custom hooks
│   ├── lib/                       # Utilities and schemas
│   └── index.css                  # Global styles & theme
├── index.html                     # Font loading, meta tags
├── components.json                # shadcn/ui config
└── package.json                   # Dependencies
```

---

## Design Tokens Quick Reference

```css
:root {
  /* Typography */
  --font-display: "Playfair Display", Georgia, serif;
  --font-body: "Outfit", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;

  /* Primary Colors */
  --primary: oklch(0.35 0.08 160);        /* Deep Forest Green */
  --accent: oklch(0.75 0.12 85);          /* Champagne Gold */

  /* Key Spacing */
  --space-page: 3rem;                      /* 48px page padding */
  --space-section: 2.5rem;                 /* 40px between sections */
  --space-card: 1.5rem;                    /* 24px card padding */

  /* Border Radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;

  /* Animation */
  --ease-luxury: cubic-bezier(0.16, 1, 0.3, 1);
  --duration-normal: 350ms;
}
```

---

*This design system transforms a generic SaaS dashboard into a distinctive, luxury-grade interface that communicates sophistication, precision, and premium quality through intentional typography, refined color choices, meaningful motion, and meticulous attention to detail.*
