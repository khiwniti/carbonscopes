/**
 * CarbonScope Theme Configuration
 * 
 * Theme settings for BKS - CarbonScope platform
 * Manages dark/light mode transitions and color schemes
 */

export const carbonScopeTheme = {
  /**
   * Default theme mode
   * CarbonScope is optimized for dark mode (engineering aesthetic)
   */
  defaultTheme: 'dark' as const,
  
  /**
   * Whether to enable system theme detection
   */
  enableSystem: true,
  
  /**
   * Disable transitions when theme changes
   * (Prevents flash of unstyled content)
   */
  disableTransitionOnChange: true,
  
  /**
   * Storage key for theme preference
   */
  storageKey: 'carbonscope-theme',
  
  /**
   * Theme attribute (class or data-attribute)
   */
  attribute: 'class' as const,
  
  /**
   * Available theme values
   */
  themes: ['light', 'dark', 'system'] as const,
} as const;

/**
 * Theme-specific CSS variable overrides
 * Applied when theme changes
 */
export const themeVariables = {
  dark: {
    '--background': 'var(--carbonscope-background)',
    '--foreground': 'var(--carbonscope-text-primary)',
    '--primary': 'var(--carbonscope-primary)',
    '--primary-foreground': 'var(--carbonscope-text-on-primary)',
    '--muted': 'var(--carbonscope-surface)',
    '--muted-foreground': 'var(--carbonscope-text-muted)',
    '--border': 'var(--carbonscope-border)',
    '--input': 'var(--carbonscope-surface)',
    '--ring': 'var(--carbonscope-primary)',
  },
  light: {
    '--background': '#FFFFFF',
    '--foreground': '#111827',
    '--primary': 'var(--carbonscope-primary)',
    '--primary-foreground': '#FFFFFF',
    '--muted': '#F3F4F6',
    '--muted-foreground': '#6B7280',
    '--border': '#E5E7EB',
    '--input': '#FFFFFF',
    '--ring': 'var(--carbonscope-primary)',
  },
} as const;

/**
 * Get theme-specific CSS variables
 */
export function getThemeVariables(theme: 'light' | 'dark'): Record<string, string> {
  return themeVariables[theme];
}

/**
 * Apply theme variables to document
 */
export function applyThemeVariables(theme: 'light' | 'dark'): void {
  if (typeof window === 'undefined') return;
  
  const variables = getThemeVariables(theme);
  const root = document.documentElement;
  
  Object.entries(variables).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });
}
