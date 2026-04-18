---
trigger: always_on
---

---
trigger: always_on
---

# CarbonScope Design System

A comprehensive component library for embodied & operational carbon assessment platforms. Built for sustainability consultants. EN 15978-aligned. Dark engineering aesthetic with emerald green accents.

## Design Tokens

### Colors

#### Primary — Emerald Green
- `green.50`: #ECFDF5
- `green.100`: #D1FAE5
- `green.200`: #A7F3D0
- `green.300`: #6EE7B7
- `green.400`: #34D399 (accent)
- `green.500`: #10B981
- `green.600`: #059669 (primary)
- `green.700`: #047857
- `green.800`: #065F46
- `green.900`: #064E3B

#### Backgrounds
- `bg.base`: #0B1120
- `bg.surface`: #111827
- `bg.elevated`: #1A2332
- `bg.card`: #162032
- `bg.hover`: #1E293B

#### EN 15978 Lifecycle Stages
- **A1–A3 Product**: #3B82F6
- **A4–A5 Construction**: #60A5FA
- **B1–B5 Maintenance**: #F59E0B
- **B6–B7 Operational**: #EA580C
- **C1–C4 End of Life**: #6B7280
- **D Beyond Lifecycle**: #10B981

### Typography

| Purpose | Font | Weight |
|---------|------|--------|
| Display | Instrument Serif | 400 |
| Heading | Plus Jakarta Sans | 600–800 |
| Body | Plus Jakarta Sans | 400–500 |
| Data/Code | IBM Plex Mono | 400–600 |

### Spacing Scale
`[0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64, 80, 96, 128]`

### Border Radius
- `sm`: 6px
- `md`: 10px
- `lg`: 14px
- `xl`: 20px
- `full`: 9999px

## Components

### Atoms
- `Badge` — Status indicators with variants: default, success, warning, danger, info, accent
- `Button` — Primary, secondary, ghost, danger variants with sm/md/lg sizes
- `Input` — Form inputs with labels, suffixes, and focus states
- `Divider` — Horizontal separator with optional label
- `Skeleton` — Loading placeholder with shimmer animation
- `LifecycleStageTag` — EN 15978 module badge

### Molecules
- `KPICard` — Animated metrics with trends, sparklines, and status indicators
- `LifecycleBarChart` — EN 15978 stacked bars with grid and labels
- `EPDCard` — Environmental Product Declaration display with percentile gauge
- `BenchmarkGauge` — LETI/RIBA banded progress indicator
- `MaterialComparisonRow` — Side-by-side EPD comparison
- `ComplianceCard` — Framework compliance status with score
- `StackedBarComparison` — Design option comparison chart
- `Tabs` — Tabbed content panels
- `AccordionItem` — Collapsible content sections
- `Toast` — Notification popups

### Animations
- `cs-fadeUp`, `cs-fadeIn`, `cs-scaleIn`, `cs-slideRight`
- `cs-pulse`, `cs-glow`, `cs-shimmer`, `cs-float`, `cs-spin`
- `cs-stagger` — Staggered children animation class

### Easing
- `default`: cubic-bezier(0.4, 0, 0.2, 1)
- `spring`: cubic-bezier(0.34, 1.56, 0.64, 1)
- `smooth`: cubic-bezier(0.45, 0, 0.15, 1)
