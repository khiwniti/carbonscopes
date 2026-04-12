# CarbonScope Design System Migration Plan

## Overview
Complete theme migration from CarbonScope brand to CarbonScope design system across all carbonscope-init applications. Client has approved the CarbonScope design (dark engineering theme with emerald green accents, EN 15978 lifecycle-aligned).

## Goal
Every single line of style across frontend, mobile, and backend templates must align with the CarbonScope design system tokens and components.

## Completed Work
✅ Task #7: Analyzed carbonscope-init codebase structure
✅ Task #8: Created centralized design tokens in `/packages/shared/design-system/`

## Implementation Tasks

### Task #1: Create Reusable Component Library

**Objective**: Port all CarbonScope components from `design_system.jsx` into a shared React component library that can be used across frontend and potentially adapted for mobile.

**Scope**:
- Create `/packages/shared/design-system/components/` directory
- Port atomic components: Badge, Button, Input, Divider, Skeleton, LifecycleStageTag
- Port molecule components: KPICard, LifecycleBarChart, EPDCard, BenchmarkGauge, MaterialComparisonRow, ComplianceCard, Tabs, AccordionItem, Toast, StackedBarComparison
- Port hooks: useInView, useCountUp
- All components must use tokens from `/packages/shared/design-system/tokens.ts`
- Components should be TypeScript with proper prop types
- Export all components from `/packages/shared/design-system/components/index.ts`

**Files to create**:
- `/packages/shared/design-system/components/atoms/Badge.tsx`
- `/packages/shared/design-system/components/atoms/Button.tsx`
- `/packages/shared/design-system/components/atoms/Input.tsx`
- `/packages/shared/design-system/components/atoms/Divider.tsx`
- `/packages/shared/design-system/components/atoms/Skeleton.tsx`
- `/packages/shared/design-system/components/atoms/LifecycleStageTag.tsx`
- `/packages/shared/design-system/components/molecules/KPICard.tsx`
- `/packages/shared/design-system/components/molecules/LifecycleBarChart.tsx`
- `/packages/shared/design-system/components/molecules/EPDCard.tsx`
- `/packages/shared/design-system/components/molecules/BenchmarkGauge.tsx`
- `/packages/shared/design-system/components/molecules/MaterialComparisonRow.tsx`
- `/packages/shared/design-system/components/molecules/ComplianceCard.tsx`
- `/packages/shared/design-system/components/molecules/Tabs.tsx`
- `/packages/shared/design-system/components/molecules/AccordionItem.tsx`
- `/packages/shared/design-system/components/molecules/Toast.tsx`
- `/packages/shared/design-system/components/molecules/StackedBarComparison.tsx`
- `/packages/shared/design-system/components/hooks/useInView.ts`
- `/packages/shared/design-system/components/hooks/useCountUp.ts`
- `/packages/shared/design-system/components/index.ts` (barrel export)

**Success criteria**:
- All components compile without errors
- Components use CarbonScope tokens exclusively
- TypeScript types are complete
- Components match design_system.jsx behavior exactly

---

### Task #2: Migrate Frontend App to CarbonScope Design System

**Objective**: Update all frontend React components to use CarbonScope design system tokens and components.

**Context**:
- Frontend uses Next.js 15 with Tailwind CSS v4
- Current theme: CarbonScope brand (light gray and black)
- Target: CarbonScope dark theme
- Partially completed: globals.css updated with CarbonScope CSS variables and animations

**Scope**:
- Create Tailwind config plugin for CarbonScope tokens
- Update all component files in `/apps/frontend/src/components/` to use CarbonScope colors
- Replace hardcoded colors with CSS variables (--cs-* variables)
- Update shadcn/ui component overrides to use CarbonScope theme
- Ensure dark mode uses CarbonScope dark engineering theme
- Replace Roobert font references with Plus Jakarta Sans and IBM Plex Mono

**Files to modify**:
- All files in `/apps/frontend/src/components/`
- `/apps/frontend/tailwind.config.ts` (if exists) or create Tailwind v4 config
- Update any inline styles or Tailwind classes using old CarbonScope colors

**Key color mappings**:
- Old primary (`#121215` black) → New primary (`#10B981` emerald green)
- Old background (`#F6F6F6` light gray) → New background (`#0B1120` dark blue-black)
- Old card (`#F9FAFB` white) → New card (`#162032` dark elevated)
- Old border (`#DCDDDE` light gray) → New border (`#1E293B` dark)
- Old text (`#121215` black) → New text (`#E2E8F0` light gray)

**Success criteria**:
- All components render with CarbonScope colors
- No CarbonScope brand colors remain
- Dark mode works correctly
- Typography uses CarbonScope fonts

---

### Task #3: Update HTML Templates with CarbonScope Styling

**Objective**: Apply CarbonScope design system to all backend-generated HTML templates and presentation slides.

**Scope**:
- Update all HTML files in `/apps/frontend/src/components/thread/tool-views/`
- Update presentation templates in `/backend/core/templates/presentations/`
- Update document viewer template in `/backend/core/tools/templates/doc_viewer.html`
- Apply CarbonScope colors, fonts, and styling
- Ensure consistency with React components

**Files to modify**:
- `/backend/core/tools/templates/doc_viewer.html`
- All slide HTML files in `/backend/core/templates/presentations/*/slide_*.html`
- Any other HTML template files found in backend

**Key updates**:
- Replace inline styles with CarbonScope tokens
- Add CarbonScope font imports
- Update background colors to dark theme
- Update text colors to light on dark
- Update border and accent colors to emerald green

**Success criteria**:
- All HTML templates use CarbonScope styling
- Fonts match (Instrument Serif, Plus Jakarta Sans, IBM Plex Mono)
- Color scheme is consistent with React components
- Templates render correctly in browsers

---

### Task #4: Migrate Mobile App to CarbonScope Design System

**Objective**: Adapt CarbonScope design tokens for React Native and update all mobile components.

**Context**:
- Mobile uses Expo/React Native with NativeWind (Tailwind for React Native)
- Current theme: CarbonScope brand in Tailwind config
- Partially completed: global.css updated with CarbonScope HSL values
- Target: CarbonScope dark theme adapted for mobile

**Scope**:
- Update `/apps/mobile/tailwind.config.js` to use CarbonScope color tokens
- Create React Native compatible components from shared design system
- Update all component files in `/apps/mobile/components/` to use CarbonScope colors
- Ensure font family changes (Roobert → Plus Jakarta Sans)
- Test dark mode on mobile

**Files to modify**:
- `/apps/mobile/tailwind.config.js` - Update color definitions
- All component files in `/apps/mobile/components/`
- Any inline styles using old CarbonScope colors

**React Native considerations**:
- Some CSS properties may need React Native equivalents
- Font loading differs from web (may need to load custom fonts)
- Test on iOS and Android if possible

**Success criteria**:
- All mobile components use CarbonScope colors
- Typography updated to CarbonScope fonts
- Dark mode works on mobile
- No CarbonScope colors remain

---

### Task #5: Validate Complete Design System Alignment

**Objective**: Verify that every single line of style aligns with client-approved CarbonScope design system.

**Scope**:
- Search entire codebase for old CarbonScope color values
- Verify all components use design system tokens
- Check for hardcoded colors that should use tokens
- Validate typography consistency
- Test visual appearance across all apps

**Search patterns to verify**:
- `#121215` (old CarbonScope black) - should be replaced
- `#F6F6F6` (old CarbonScope white) - should be replaced
- `#DCDDDE` (old borders) - should be replaced
- `Roobert` font family - should be replaced
- Any `hsl(218 12% 7%)` or similar old HSL values

**Validation checklist**:
- [ ] Frontend: All components use CarbonScope colors
- [ ] Frontend: All typography uses CarbonScope fonts
- [ ] Mobile: All components use CarbonScope colors
- [ ] Mobile: All typography uses CarbonScope fonts
- [ ] Backend HTML: All templates use CarbonScope styling
- [ ] No old CarbonScope brand colors anywhere
- [ ] Dark mode works consistently across all apps
- [ ] Emerald green accent (#10B981, #059669, #34D399) used appropriately
- [ ] EN 15978 lifecycle colors present in relevant components

**Tools**:
- Use `grep` to search for old color values
- Use `git diff` to review all changes
- Visual testing in browser and mobile

**Success criteria**:
- Zero instances of old CarbonScope colors
- All components use CarbonScope design tokens
- Visual consistency across frontend, mobile, and templates
- Client approval criteria met

---

### Task #6: Create Comprehensive Style Guide Documentation

**Objective**: Document the CarbonScope design system usage, component APIs, and migration guidelines.

**Scope**:
- Create `/packages/shared/design-system/README.md` with:
  - Design system philosophy and principles
  - Color token reference with visual swatches
  - Typography scale and usage guidelines
  - Component catalog with examples
  - EN 15978 lifecycle color usage
  - Migration guide from other themes
  - Dark mode implementation guide
  - Accessibility considerations

**Content sections**:
1. **Introduction**: CarbonScope design system overview
2. **Design Tokens**: Complete reference of all tokens
3. **Typography**: Font families, sizes, weights, usage
4. **Color System**: Background, border, text, accent colors
5. **Components**: All atomic and molecule components with props
6. **EN 15978 Integration**: Lifecycle stage colors and usage
7. **Usage Examples**: Code snippets for common patterns
8. **Migration Guide**: How to adopt CarbonScope in new projects
9. **Best Practices**: Guidelines for maintaining consistency

**Success criteria**:
- Complete documentation of all design tokens
- All components documented with prop tables
- Usage examples for each component
- Clear migration instructions
- Professionally formatted markdown

---

### Task #9: Optimize Fonts with next/font for Zero-CLS Loading

**Objective**: Replace Google Fonts CDN imports with next/font self-hosted optimization for zero Cumulative Layout Shift.

**Context**:
- Currently using Google Fonts CDN for Instrument Serif, Plus Jakarta Sans, IBM Plex Mono
- Next.js recommends next/font for performance and zero-CLS
- This is a frontend-only optimization

**Scope**:
- Install or configure next/font in `/apps/frontend`
- Load Instrument Serif, Plus Jakarta Sans, and IBM Plex Mono via next/font
- Update globals.css to use next/font CSS variables
- Remove Google Fonts CDN import
- Configure font display and weight loading
- Update font-family CSS variables

**Files to modify**:
- `/apps/frontend/src/app/layout.tsx` or root layout - Add next/font imports
- `/apps/frontend/src/app/globals.css` - Update font family references
- Remove `@import url('https://fonts.googleapis.com/...')` line

**next/font configuration**:
```typescript
import { Instrument_Serif, Plus_Jakarta_Sans, IBM_Plex_Mono } from 'next/font/google';

const instrumentSerif = Instrument_Serif({
  subsets: ['latin'],
  variable: '--font-instrument',
  display: 'swap',
});

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-jakarta',
  display: 'swap',
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-mono',
  display: 'swap',
});
```

**Success criteria**:
- Fonts load via next/font
- Zero Cumulative Layout Shift
- Font families work correctly
- Performance improvement measurable

---

## Dependencies

Task dependencies (must complete in order):
- Task #1 (Component Library) must complete before #2 (Frontend) and #4 (Mobile) can use shared components
- Tasks #2, #3, #4 can run in parallel after #1
- Task #5 (Validation) requires #2, #3, #4 to be complete
- Task #6 (Documentation) can run anytime but benefits from completed implementation
- Task #9 (Font optimization) can run anytime after #2 (Frontend)

Recommended execution order:
1. Task #1: Component Library
2. Tasks #2, #3, #4 in parallel: Frontend, Templates, Mobile
3. Task #9: Font optimization
4. Task #5: Validation
5. Task #6: Documentation

## Success Metrics

The migration is complete when:
1. ✅ Zero CarbonScope brand colors remain in codebase
2. ✅ All applications use CarbonScope design tokens
3. ✅ Typography uses Instrument Serif, Plus Jakarta Sans, IBM Plex Mono
4. ✅ Dark engineering theme with emerald green accents applied everywhere
5. ✅ EN 15978 lifecycle colors present in relevant components
6. ✅ Component library available for reuse
7. ✅ Comprehensive documentation created
8. ✅ Fonts optimized with next/font
9. ✅ Visual consistency across frontend, mobile, and templates
10. ✅ Client approval criteria met

## Reference Files

- Source design: `/teamspace/studios/this_studio/comprehensive-carbonscope-bim-agent/design_system.jsx`
- Design tokens: `/teamspace/studios/this_studio/comprehensive-carbonscope-bim-agent/carbonscope-init/packages/shared/design-system/tokens.ts`
- Global styles: `/teamspace/studios/this_studio/comprehensive-carbonscope-bim-agent/carbonscope-init/packages/shared/design-system/global.css`
- Frontend globals: `/teamspace/studios/this_studio/comprehensive-carbonscope-bim-agent/carbonscope-init/apps/frontend/src/app/globals.css`
- Mobile globals: `/teamspace/studios/this_studio/comprehensive-carbonscope-bim-agent/carbonscope-init/apps/mobile/global.css`
