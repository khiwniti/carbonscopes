# CarbonScope Design System Fix Plan

## Overview
Complete alignment of ALL frontend components with design_system.jsx specification, replacing semantic tokens with direct CarbonScope styling.

## Critical Findings from Audit
1. CarbonScopeLoader uses hardcoded colors (#ffffff, #000000) instead of CarbonScope tokens
2. Hero section uses Tailwind semantic tokens instead of direct CarbonScope styling
3. CarbonScope branding still present (CarbonScope-brandmark-bg.svg, CarbonScopeLogo)
4. SVG plan icons use old CarbonScope color (#121215)
5. 547 component files need verification for CarbonScope compliance
6. Missing CarbonScope-specific animations (cs-pulse, cs-glow, cs-fadeUp)

## User's Expected Styling Pattern
From provided HTML example - components should use:
- **Inline styles** with CSS custom properties: `style="font-family: var(--font-display); color: #E2E8F0"`
- **Direct CarbonScope colors**: `#34D399`, `#E2E8F0`, `rgba(52, 211, 153, 0.15)`
- **CarbonScope animations**: `animate-cs-pulse`, not generic `animate-pulse`
- **CSS variables**: `var(--cs-bg-card)`, `var(--cs-text-primary)`, etc.

## Implementation Tasks

### Task #1: Create CarbonScopeLoader Component
**Priority**: CRITICAL
**File**: `/apps/frontend/src/components/ui/carbonscope-loader.tsx`

**Spec**:
- Replace CarbonScopeLoader with CarbonScope-themed loader
- Use emerald green spinner: `var(--cs-green-400)` or `#34D399`
- Use CarbonScope glow effect: `box-shadow: 0 0 16px rgba(52, 211, 153, 0.15)`
- Support dark theme (default) with optional light variant
- Match design_system.jsx styling patterns
- Export as CarbonScopeLoader, keep CarbonScopeLoader as deprecated alias for backwards compatibility

**Files to Modify**:
- Create: `src/components/ui/carbonscope-loader.tsx`
- Update: All files importing CarbonScopeLoader to use CarbonScopeLoader

---

### Task #2: Update Hero Section to Direct CarbonScope Styling
**Priority**: CRITICAL
**File**: `/apps/frontend/src/components/home/hero-section.tsx`

**Spec**:
Replace Tailwind semantic classes with direct CarbonScope styling matching user's HTML example:
- Title: `style="font-family: var(--font-display); color: #E2E8F0; line-height: 1.1"`
- Accent text: `style="color:#34D399;font-style:italic"`
- Subtitle: `style="font-family: var(--font-body); color: #64748B"`
- Badge/pill: `style="background: rgba(52, 211, 153, 0.15); border: 1px solid #065F46"`
- Status indicator: Use `animate-cs-pulse` animation

**Pattern to Follow**:
```tsx
<h1 style={{
  fontFamily: 'var(--font-display)',
  color: '#E2E8F0',
  lineHeight: 1.1,
}}>
  Understand Your <span style={{ color: '#34D399', fontStyle: 'italic' }}>Carbon Footprint</span>
</h1>
```

---

### Task #3: Replace CarbonScope Branding with CarbonScope/Suna
**Priority**: CRITICAL
**Files**:
- `/apps/frontend/src/components/home/hero-section.tsx` (line 89)
- `/apps/frontend/src/components/home/navbar.tsx` (line 12)
- `/apps/frontend/public/CarbonScope-brandmark-bg.svg`

**Spec**:
- Remove all references to `CarbonScope-brandmark-bg.svg`
- Replace `CarbonScopeLogo` component with `SunaLogo` or `CarbonScopeLogo`
- Update background to use CarbonScope design patterns (carbon grid, molecular patterns)
- Ensure all branding reflects Suna/CarbonScope identity, not CarbonScope

---

### Task #4: Update SVG Plan Icons to CarbonScope Colors
**Priority**: HIGH
**Files**: All files in `/apps/frontend/public/plan-icons/`

**Spec**:
- Replace `fill="#121215"` (old CarbonScope black) with CarbonScope text colors
- Use `fill="#E2E8F0"` (cs-text-primary) for main text
- Use `fill="#94A3B8"` (cs-text-secondary) for subtle elements
- Update background colors from `#E0E0E0` to CarbonScope equivalents
- Maintain icon readability and contrast

**Files to Update**:
- `basic.svg`
- `plus.svg`
- `pro.svg`
- `ultra.svg`

---

### Task #5: Audit and Fix High-Priority Components
**Priority**: HIGH
**Scope**: Components with hardcoded colors or missing CarbonScope styling

**Target Files** (from grep results):
1. `src/components/ui/animated-bg.tsx` - Background animations
2. `src/components/ui/border-beam.tsx` - Decorative effects
3. `src/components/ui/grain-icon.tsx` - Icon styling
4. `src/components/home/navbar.tsx` - Navigation colors
5. `src/components/home/footer-section.tsx` - Footer colors
6. `src/components/billing/pricing-section.tsx` - Pricing display
7. `src/components/agents/agent-configuration-dialog.tsx` - Agent UI

**Spec**:
- Replace all hardcoded hex colors with CarbonScope tokens
- Use CSS custom properties: `var(--cs-*)` or direct values from design_system.jsx
- Apply CarbonScope animations where appropriate
- Ensure emerald green accent (#34D399, #10B981, #059669) for primary actions
- Use dark engineering base colors (#0B1120, #162032, #1E293B)

---

### Task #6: Create Component Audit Spreadsheet
**Priority**: MEDIUM
**File**: `/claudedocs/carbonscope-component-audit.md`

**Spec**:
- Systematic audit of all 547 component files
- Track: File path, CarbonScope compliance status, issues found, fix priority
- Categories: ✅ Compliant, ⚠️ Partial, ❌ Non-compliant, 🔍 Needs Review
- Prioritize user-facing components: home, dashboard, agents, auth
- Generate fix tasks for all non-compliant components

---

### Task #7: Update shadcn/ui Components Theme
**Priority**: MEDIUM
**Files**: `/apps/frontend/src/components/ui/*.tsx` (shadcn components)

**Spec**:
- Review all shadcn/ui primitive components (button, card, dialog, input, etc.)
- Override default styling with CarbonScope design tokens
- Ensure `cn()` utility preserves CarbonScope colors
- Update component variants to use CarbonScope color scale
- Test all variants (default, primary, secondary, ghost, danger)

**Key Components**:
- `button.tsx` - Use emerald green for primary variant
- `card.tsx` - Use cs-bg-card background
- `input.tsx` - Use cs-bg-input, cs-border-active for focus
- `dialog.tsx` - Use cs-bg-elevated, cs-border-default

---

### Task #8: Implement Missing CarbonScope Animations
**Priority**: MEDIUM

**Spec**:
- Verify all keyframe animations from design_system.jsx are in globals.css
- Replace generic Tailwind animations with CarbonScope equivalents:
  - `animate-pulse` → `animate-cs-pulse`
  - `animate-spin` → `animate-cs-spin`
  - Generic fade-in → `animate-cs-fadeIn`, `animate-cs-fadeUp`
- Add utility classes for CarbonScope animations
- Document animation usage patterns

**Animations to Implement**:
- cs-fadeUp, cs-fadeIn, cs-scaleIn, cs-slideRight (✅ already in global.css)
- cs-pulse, cs-glow, cs-shimmer (✅ already in global.css)
- cs-countUp, cs-bar, cs-fillUp, cs-float, cs-spin (✅ already in global.css)

---

### Task #9: Validate Complete Design System Alignment
**Priority**: LOW (Final Validation)

**Spec**:
- Run comprehensive grep for old CarbonScope colors: `#121215`, `#F6F6F6`, `#DCDDDE`
- Search for non-CarbonScope rgba values
- Verify all components use CarbonScope fonts (Instrument Serif, Plus Jakarta Sans, IBM Plex Mono)
- Check for remaining `Roobert` font references
- Validate all hardcoded colors match CarbonScope palette
- Create final compliance report

**Success Criteria**:
- Zero CarbonScope brand references
- Zero non-CarbonScope colors
- All components use CSS custom properties or design_system.jsx tokens
- Visual consistency across all pages and components
- Build completes without errors
- All tests pass

---

## Execution Order

1. **Task #1** - CarbonScopeLoader (high impact, widely used)
2. **Task #3** - Remove CarbonScope branding (critical for brand identity)
3. **Task #2** - Hero section (most visible page, sets pattern for others)
4. **Task #4** - SVG plan icons (quick win, clear spec)
5. **Task #5** - High-priority components (systematic fixes)
6. **Task #7** - shadcn/ui theme (foundation for all UI components)
7. **Task #6** - Component audit (identify remaining issues)
8. **Task #8** - Animations (polish and consistency)
9. **Task #9** - Final validation (quality gate)

## Success Metrics

- ✅ All 547 component files audited and compliant
- ✅ Zero CarbonScope brand references remain
- ✅ All components use CarbonScope design tokens exclusively
- ✅ Visual consistency matches design_system.jsx specification
- ✅ User's HTML example pattern applied throughout
- ✅ Build succeeds with zero TypeScript errors
- ✅ All existing tests pass
- ✅ Client approval criteria met: "every single line of style completely aligned"
