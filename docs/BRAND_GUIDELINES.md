# CarbonScope Brand Guidelines

**BKS - CarbonScope**  
*Embodied Carbon Intelligence Platform*

Version 1.0 | Last Updated: March 28, 2026

---

## Table of Contents

1. [Brand Identity](#brand-identity)
2. [Color Palette](#color-palette)
3. [Typography](#typography)
4. [Logo Usage](#logo-usage)
5. [EN 15978 Lifecycle Colors](#en-15978-lifecycle-colors)
6. [Component Usage](#component-usage)
7. [Design Principles](#design-principles)

---

## Brand Identity

### Overview

**CarbonScope** is the embodied carbon intelligence platform developed by BKS. Our brand identity reflects:

- **Scientific Precision**: EN 15978 lifecycle stage alignment
- **Environmental Focus**: Emerald green representing sustainability
- **Engineering Excellence**: Dark navy aesthetic for technical credibility
- **Strata Metaphor**: 3-layer logo representing carbon through building lifecycle

### Brand Name

- **Full Name:** BKS - CarbonScope
- **Short Name:** CarbonScope
- **Tagline:** "Embodied Carbon Intelligence Platform"

---

## Color Palette

### Primary Colors

**Emerald Primary** - Main brand color  
`#10B981` (RGB: 16, 185, 129) - Emerald 500  
*Use for: Primary actions, links, brand accents*

**Emerald Dark** - Hover states  
`#059669` (RGB: 5, 150, 105) - Emerald 600  
*Use for: Button hover, active states*

**Emerald Light** - Accents & glow  
`#34D399` (RGB: 52, 211, 153) - Emerald 400  
*Use for: Highlights, glow effects, subtle accents*

### Background Colors

**Navy Dark** - Primary background  
`#0B1120` (RGB: 11, 17, 32)  
*Use for: Main application background*

**Slate Dark** - Alternative background  
`#0F172A` (RGB: 15, 23, 42) - Slate 900  
*Use for: Secondary backgrounds*

**Slate Medium** - Subtle backgrounds  
`#1E293B` (RGB: 30, 41, 59) - Slate 800  
*Use for: Hover states, subtle differentiation*

### Surface Colors

**Gray 800** - Card backgrounds  
`#1F2937` (RGB: 31, 41, 55)  
*Use for: Cards, panels, elevated surfaces*

**Gray 700** - Hover states  
`#374151` (RGB: 55, 65, 81)  
*Use for: Interactive element hover states*

### Text Colors

**Gray 50** - Primary text  
`#F9FAFB` (RGB: 249, 250, 251)  
*Use for: Headings, primary body text*

**Gray 300** - Secondary text  
`#D1D5DB` (RGB: 209, 213, 219)  
*Use for: Descriptions, secondary information*

**Gray 400** - Muted text  
`#9CA3AF` (RGB: 156, 163, 175)  
*Use for: Hints, placeholders, disabled text*

### Color Accessibility

All color combinations meet **WCAG 2.1 AA** standards:

| Combination | Contrast Ratio | Grade |
|-------------|----------------|-------|
| Navy (#0B1120) + Emerald (#10B981) | 7.2:1 | AAA |
| Navy (#0B1120) + Gray 50 (#F9FAFB) | 18.5:1 | AAA |
| Emerald (#10B981) + White (#FFFFFF) | 3.9:1 | AA |

---

## Typography

### Font Families

**Display - Instrument Serif**  
*Source: Google Fonts*  
Weights: 400 (Regular), 500 (Medium)

```typescript
fontFamily: 'Instrument Serif, serif'
```

**Use for:**
- Hero headings
- Marketing pages
- Large display text
- Strata/geological metaphor reinforcement

---

**Headings & UI - Plus Jakarta Sans**  
*Source: Google Fonts*  
Weights: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)

```typescript
fontFamily: 'Plus Jakarta Sans, sans-serif'
```

**Use for:**
- Page headings (H1-H6)
- Navigation
- Buttons
- Form labels
- UI elements

---

**Monospace - IBM Plex Mono**  
*Source: Google Fonts*  
Weights: 400 (Regular), 500 (Medium), 600 (Semibold)

```typescript
fontFamily: 'IBM Plex Mono, monospace'
```

**Use for:**
- Code snippets
- Data tables
- Carbon calculations
- Technical specifications

### Type Scale

| Size | rem | px | Use Case |
|------|-----|----|-----------
| xs | 0.75rem | 12px | Fine print, captions |
| sm | 0.875rem | 14px | Secondary text |
| base | 1rem | 16px | Body text (default) |
| lg | 1.125rem | 18px | Lead paragraphs |
| xl | 1.25rem | 20px | H5 |
| 2xl | 1.5rem | 24px | H4 |
| 3xl | 1.875rem | 30px | H3 |
| 4xl | 2.25rem | 36px | H2 |
| 5xl | 3rem | 48px | H1 |
| 6xl | 3.75rem | 60px | Hero display |

---

## Logo Usage

### Logo Variants

**1. Full Logo** (Default)  
Icon + Wordmark  
*Use for: Primary brand presence, headers, marketing*

```tsx
<CarbonScopeLogo variant="full" size="md" />
```

**2. Icon Only**  
3-layer strata mark  
*Use for: Favicons, app icons, space-constrained areas*

```tsx
<CarbonScopeLogo variant="icon" size="sm" />
```

**3. Wordmark Only**  
Text logo with accent  
*Use for: Text-heavy contexts, horizontal layouts*

```tsx
<CarbonScopeLogo variant="wordmark" size="lg" />
```

**4. BKS Prefix Logo**  
BKS | CarbonScope full logo  
*Use for: Official documents, reports, certifications*

```tsx
<BKSCarbonScopeLogo variant="full" size="md" />
```

### Logo Sizes

| Size | Height | Use Case |
|------|---------|-----------|
| sm | 24px | Navigation, compact UI |
| md | 32px | Standard headers |
| lg | 48px | Hero sections |
| xl | 64px | Landing pages, marketing |

### Logo Clear Space

Maintain clear space around logo equal to **logo height / 2**.

❌ **Don't:**
- Place logo on busy backgrounds
- Stretch or distort logo
- Change logo colors (except light/dark theme)
- Add effects (drop shadow, glow, etc.)

✅ **Do:**
- Use on solid backgrounds
- Maintain aspect ratio
- Use provided theme variants
- Ensure adequate contrast

---

## EN 15978 Lifecycle Colors

CarbonScope uses a standardized color system aligned with EN 15978 lifecycle stages:

### A1-A3: Product Stage
**Emerald Green** `#10B981`

Represents raw material extraction, transport, and manufacturing. The foundation of embodied carbon.

- **Light:** `#34D399`
- **Dark:** `#059669`

---

### A4-A5: Construction Process Stage
**Blue** `#3B82F6`

Transport to site and construction/installation processes.

- **Light:** `#60A5FA`
- **Dark:** `#2563EB`

---

### B1-B5: Use Stage (Maintenance)
**Violet** `#8B5CF6`

Use, maintenance, repair, replacement, and refurbishment during building lifetime.

- **Light:** `#A78BFA`
- **Dark:** `#7C3AED`

---

### B6-B7: Use Stage (Operational)
**Amber** `#F59E0B`

Operational energy and water use during building occupation.

- **Light:** `#FBBF24`
- **Dark:** `#D97706`

---

### C1-C4: End of Life Stage
**Red** `#EF4444`

Deconstruction, transport, waste processing, and disposal.

- **Light:** `#F87171`
- **Dark:** `#DC2626`

---

### D: Beyond System Boundary
**Indigo** `#6366F1`

Benefits and loads beyond system boundary (recycling, reuse potentials).

- **Light:** `#818CF8`
- **Dark:** `#4F46E5`

### Usage Example

```typescript
import { getLifecycleColor, lifecycleStages } from '@/lib/design-tokens';

// Get stage color
const color = getLifecycleColor('A1-A3'); // #10B981

// Access stage metadata
const stage = lifecycleStages['B1-B5'];
console.log(stage.name); // "Use Stage (Maintenance)"
console.log(stage.description); // "Use, Maintenance, Repair..."
```

---

## Component Usage

### Importing Design Tokens

```typescript
// TypeScript constants
import { carbonScope, lifecycleStages } from '@/lib/design-tokens';

const buttonStyle = {
  backgroundColor: carbonScope.colors.primary,
  color: carbonScope.colors.textOnPrimary,
  borderRadius: carbonScope.radius.lg,
  padding: `${carbonScope.spacing[3]} ${carbonScope.spacing[6]}`,
};
```

```css
/* CSS custom properties */
.my-component {
  background-color: var(--carbonscope-primary);
  color: var(--carbonscope-text-primary);
  border-radius: var(--carbonscope-radius-lg);
}
```

### Logo Component

```tsx
import { CarbonScopeLogo, BKSCarbonScopeLogo } from '@/components/brand';

// Standard logo
<CarbonScopeLogo variant="full" size="md" theme="dark" />

// With animation
<CarbonScopeLogo variant="icon" size="lg" animated />

// With BKS prefix
<BKSCarbonScopeLogo variant="full" size="lg" />
```

### Lifecycle Stage Badge

```tsx
import { getLifecycleColor } from '@/lib/design-tokens';

function StageBadge({ stage }: { stage: 'A1-A3' | 'A4-A5' | ... }) {
  return (
    <span 
      style={{
        backgroundColor: getLifecycleColor(stage, 'light'),
        color: getLifecycleColor(stage, 'dark'),
        padding: '0.25rem 0.75rem',
        borderRadius: '0.375rem',
        fontWeight: 600,
      }}
    >
      {stage}
    </span>
  );
}
```

---

## Design Principles

### 1. Scientific Precision

All carbon calculations and lifecycle stage representations must align with **EN 15978** standards. Use the exact lifecycle colors to maintain consistency with scientific documentation.

### 2. Dark Engineering Aesthetic

Primary interface uses dark backgrounds to:
- Reduce eye strain during extended use
- Emphasize data visualizations
- Create professional engineering environment
- Make emerald accents pop

### 3. Accessibility First

- Maintain WCAG 2.1 AA minimum (AAA preferred)
- Ensure 4.5:1 contrast ratio for text
- Provide text alternatives for color-coded information
- Support keyboard navigation

### 4. Data Clarity

Use typography and color strategically:
- **Display (Instrument Serif):** Emotional impact, brand presence
- **Headings (Plus Jakarta Sans):** Structure, hierarchy
- **Mono (IBM Plex Mono):** Precision, technical data

### 5. Progressive Enhancement

Design system supports:
- Light/dark theme switching
- Responsive breakpoints
- Reduced motion preferences
- High contrast modes

---

## Quick Reference

### Import Tokens

```typescript
import { carbonScope, lifecycleStages, getLifecycleColor } from '@/lib/design-tokens';
import { CarbonScopeLogo } from '@/components/brand';
```

### Common Colors

- **Primary:** `carbonScope.colors.primary` or `var(--carbonscope-primary)`
- **Background:** `carbonScope.colors.background` or `var(--carbonscope-background)`
- **Text:** `carbonScope.colors.textPrimary` or `var(--carbonscope-text-primary)`

### Typography

- **Headings:** Plus Jakarta Sans Bold
- **Body:** Plus Jakarta Sans Regular
- **Data:** IBM Plex Mono

### Lifecycle

Use `getLifecycleColor(stage)` for programmatic color access.

---

## Resources

- **Design Tokens:** `suna-init/apps/frontend/src/lib/design-tokens.ts`
- **Theme CSS:** `suna-init/apps/frontend/src/styles/theme.css`
- **Logo Component:** `suna-init/apps/frontend/src/components/brand/carbonscope-logo.tsx`
- **EN 15978 Standard:** [ISO 15978:2011](https://www.iso.org/standard/38916.html)

---

**For questions or additions to this brand guide, contact the BKS design team.**
