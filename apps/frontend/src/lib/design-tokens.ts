/**
 * CarbonScope Design Tokens
 * 
 * Type-safe design system tokens for BKS - CarbonScope
 * Embodied Carbon Intelligence Platform
 * 
 * Usage:
 *   import { carbonScope } from '@/lib/design-tokens';
 *   
 *   const MyComponent = () => (
 *     <div style={{ color: carbonScope.colors.primary }}>
 *       {carbonScope.typography.heading}
 *     </div>
 *   );
 */

export const carbonScope = {
  /**
   * Color Palette
   */
  colors: {
    // Primary Brand Colors
    primary: '#10B981',           // Emerald 500
    primaryDark: '#059669',        // Emerald 600
    primaryLight: '#34D399',       // Emerald 400
    primaryDarker: '#047857',      // Emerald 700
    
    // Background Colors
    background: '#0B1120',         // Navy dark
    backgroundAlt: '#0F172A',      // Slate 900
    backgroundSubtle: '#1E293B',   // Slate 800
    
    // Surface Colors
    surface: '#1F2937',            // Gray 800
    surfaceHover: '#374151',       // Gray 700
    surfaceActive: '#4B5563',      // Gray 600
    surfaceElevated: '#111827',    // Gray 900
    
    // Text Colors
    textPrimary: '#F9FAFB',        // Gray 50
    textSecondary: '#D1D5DB',      // Gray 300
    textMuted: '#9CA3AF',          // Gray 400
    textDisabled: '#6B7280',       // Gray 500
    textOnPrimary: '#FFFFFF',      // White
    
    // Border Colors
    border: '#374151',             // Gray 700
    borderLight: '#4B5563',        // Gray 600
    borderStrong: '#1F2937',       // Gray 800
    borderFocus: '#10B981',        // Emerald 500
    
    // Lifecycle Stage Colors (EN 15978)
    lifecycle: {
      // A1-A3: Product Stage
      a1a3: '#10B981',             // Emerald 500
      a1a3Light: '#34D399',        // Emerald 400
      a1a3Dark: '#059669',         // Emerald 600
      
      // A4-A5: Construction Process Stage
      a4a5: '#3B82F6',             // Blue 500
      a4a5Light: '#60A5FA',        // Blue 400
      a4a5Dark: '#2563EB',         // Blue 600
      
      // B1-B5: Use Stage
      b1b5: '#8B5CF6',             // Violet 500
      b1b5Light: '#A78BFA',        // Violet 400
      b1b5Dark: '#7C3AED',         // Violet 600
      
      // B6-B7: Operational Stage
      b6b7: '#F59E0B',             // Amber 500
      b6b7Light: '#FBBF24',        // Amber 400
      b6b7Dark: '#D97706',         // Amber 600
      
      // C1-C4: End of Life Stage
      c1c4: '#EF4444',             // Red 500
      c1c4Light: '#F87171',        // Red 400
      c1c4Dark: '#DC2626',         // Red 600
      
      // D: Beyond System Boundary
      d: '#6366F1',                // Indigo 500
      dLight: '#818CF8',           // Indigo 400
      dDark: '#4F46E5',            // Indigo 600
    },
    
    // Semantic Colors
    success: '#10B981',            // Emerald 500
    successLight: '#D1FAE5',       // Emerald 100
    successDark: '#047857',        // Emerald 700
    
    warning: '#F59E0B',            // Amber 500
    warningLight: '#FEF3C7',       // Amber 100
    warningDark: '#B45309',        // Amber 700
    
    error: '#EF4444',              // Red 500
    errorLight: '#FEE2E2',         // Red 100
    errorDark: '#B91C1C',          // Red 700
    
    info: '#3B82F6',               // Blue 500
    infoLight: '#DBEAFE',          // Blue 100
    infoDark: '#1E40AF',           // Blue 700
  },
  
  /**
   * Typography System
   */
  typography: {
    // Font Families
    fontDisplay: 'Instrument Serif, serif',
    fontHeading: 'Plus Jakarta Sans, sans-serif',
    fontBody: 'Plus Jakarta Sans, sans-serif',
    fontMono: 'IBM Plex Mono, monospace',
    
    // Font Sizes (rem)
    fontSize: {
      xs: '0.75rem',      // 12px
      sm: '0.875rem',     // 14px
      base: '1rem',       // 16px
      lg: '1.125rem',     // 18px
      xl: '1.25rem',      // 20px
      '2xl': '1.5rem',    // 24px
      '3xl': '1.875rem',  // 30px
      '4xl': '2.25rem',   // 36px
      '5xl': '3rem',      // 48px
      '6xl': '3.75rem',   // 60px
    },
    
    // Line Heights
    lineHeight: {
      none: 1,
      tight: 1.25,
      snug: 1.375,
      normal: 1.5,
      relaxed: 1.625,
      loose: 2,
    },
    
    // Font Weights
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
  },
  
  /**
   * Spacing Scale
   */
  spacing: {
    1: '0.25rem',   // 4px
    2: '0.5rem',    // 8px
    3: '0.75rem',   // 12px
    4: '1rem',      // 16px
    5: '1.25rem',   // 20px
    6: '1.5rem',    // 24px
    8: '2rem',      // 32px
    10: '2.5rem',   // 40px
    12: '3rem',     // 48px
    16: '4rem',     // 64px
    20: '5rem',     // 80px
  },
  
  /**
   * Border Radius
   */
  radius: {
    none: '0',
    sm: '0.125rem',   // 2px
    base: '0.25rem',  // 4px
    md: '0.375rem',   // 6px
    lg: '0.5rem',     // 8px
    xl: '0.75rem',    // 12px
    '2xl': '1rem',    // 16px
    full: '9999px',   // Fully rounded
  },
  
  /**
   * Shadows
   */
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    glow: '0 0 20px rgba(16, 185, 129, 0.3)',
    glowStrong: '0 0 40px rgba(16, 185, 129, 0.5)',
  },
  
  /**
   * Z-Index Layers
   */
  zIndex: {
    base: 0,
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modalBackdrop: 1040,
    modal: 1050,
    popover: 1060,
    tooltip: 1070,
    notification: 1080,
  },
} as const;

/**
 * EN 15978 Lifecycle Stage Mapping
 * 
 * Maps lifecycle stages to their color tokens
 */
export const lifecycleStages = {
  'A1-A3': {
    name: 'Product Stage',
    description: 'Raw material supply, Transport, Manufacturing',
    color: carbonScope.colors.lifecycle.a1a3,
    colorLight: carbonScope.colors.lifecycle.a1a3Light,
    colorDark: carbonScope.colors.lifecycle.a1a3Dark,
  },
  'A4-A5': {
    name: 'Construction Process Stage',
    description: 'Transport to site, Construction-installation',
    color: carbonScope.colors.lifecycle.a4a5,
    colorLight: carbonScope.colors.lifecycle.a4a5Light,
    colorDark: carbonScope.colors.lifecycle.a4a5Dark,
  },
  'B1-B5': {
    name: 'Use Stage (Maintenance)',
    description: 'Use, Maintenance, Repair, Replacement, Refurbishment',
    color: carbonScope.colors.lifecycle.b1b5,
    colorLight: carbonScope.colors.lifecycle.b1b5Light,
    colorDark: carbonScope.colors.lifecycle.b1b5Dark,
  },
  'B6-B7': {
    name: 'Use Stage (Operational)',
    description: 'Operational energy use, Operational water use',
    color: carbonScope.colors.lifecycle.b6b7,
    colorLight: carbonScope.colors.lifecycle.b6b7Light,
    colorDark: carbonScope.colors.lifecycle.b6b7Dark,
  },
  'C1-C4': {
    name: 'End of Life Stage',
    description: 'Deconstruction, Transport, Waste processing, Disposal',
    color: carbonScope.colors.lifecycle.c1c4,
    colorLight: carbonScope.colors.lifecycle.c1c4Light,
    colorDark: carbonScope.colors.lifecycle.c1c4Dark,
  },
  'D': {
    name: 'Benefits Beyond System Boundary',
    description: 'Reuse, Recovery, Recycling potentials',
    color: carbonScope.colors.lifecycle.d,
    colorLight: carbonScope.colors.lifecycle.dLight,
    colorDark: carbonScope.colors.lifecycle.dDark,
  },
} as const;

/**
 * Helper function to get lifecycle stage color
 */
export function getLifecycleColor(stage: keyof typeof lifecycleStages, variant: 'default' | 'light' | 'dark' = 'default'): string {
  const stageData = lifecycleStages[stage];
  if (!stageData) return carbonScope.colors.textMuted;
  
  switch (variant) {
    case 'light':
      return stageData.colorLight;
    case 'dark':
      return stageData.colorDark;
    default:
      return stageData.color;
  }
}

/**
 * Gradient Definitions
 */
export const gradients = {
  emerald: `linear-gradient(135deg, ${carbonScope.colors.primaryDark} 0%, ${carbonScope.colors.primary} 50%, ${carbonScope.colors.primaryLight} 100%)`,
  lifecycle: `linear-gradient(
    90deg,
    ${carbonScope.colors.lifecycle.a1a3} 0%,
    ${carbonScope.colors.lifecycle.a4a5} 20%,
    ${carbonScope.colors.lifecycle.b1b5} 40%,
    ${carbonScope.colors.lifecycle.b6b7} 60%,
    ${carbonScope.colors.lifecycle.c1c4} 80%,
    ${carbonScope.colors.lifecycle.d} 100%
  )`,
} as const;

/**
 * Type exports for TypeScript autocomplete
 */
export type CarbonScopeColors = typeof carbonScope.colors;
export type LifecycleStage = keyof typeof lifecycleStages;
export type LifecycleStageInfo = typeof lifecycleStages[LifecycleStage];
