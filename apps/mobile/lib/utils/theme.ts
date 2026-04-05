import { DarkTheme, DefaultTheme, type Theme } from '@react-navigation/native';

export const THEME = {
light: {
background: '#162032', /* CarbonScope elevated (lighter for light mode) */
foreground: '#E2E8F0', /* CarbonScope primary text */
card: '#1A2332', /* CarbonScope elevated card */
cardForeground: '#E2E8F0',
popover: '#162032',
popoverForeground: '#E2E8F0',
primary: '#10B981', /* CarbonScope primary - Emerald green */
primaryForeground: '#FFFFFF',
secondary: '#1E293B', /* CarbonScope secondary */
secondaryForeground: '#E2E8F0',
muted: '#1A2332',
mutedForeground: '#94A3B8', /* CarbonScope secondary text */
accent: '#34D399', /* CarbonScope accent - Light emerald */
accentForeground: '#0B1120',
destructive: '#F87171', /* CarbonScope danger */
border: '#1E293B', /* CarbonScope border */
input: '#0D1526', /* CarbonScope input */
ring: 'rgba(5, 150, 105, 0.5)', /* CarbonScope focus ring */
radius: '0.625rem',
/* EN 15978 Lifecycle Charts - CarbonScope */
chart1: '#3B82F6', /* Blue - A1-A3 */
chart2: '#60A5FA', /* Light Blue - A4-A5 */
chart3: '#F59E0B', /* Amber - B1-B5 */
chart4: '#EA580C', /* Orange - B6-B7 */
chart5: '#6B7280', /* Gray - C1-C4 */
},
dark: {
background: '#0B1120', /* CarbonScope base - Deep blue-black */
foreground: '#E2E8F0', /* CarbonScope primary text */
card: '#162032', /* CarbonScope card - Elevated dark */
cardForeground: '#E2E8F0',
popover: '#111827', /* CarbonScope surface */
popoverForeground: '#E2E8F0',
primary: '#10B981', /* CarbonScope primary - Emerald green */
primaryForeground: '#FFFFFF',
secondary: '#1E293B', /* CarbonScope secondary */
secondaryForeground: '#E2E8F0',
muted: '#1A2332', /* CarbonScope elevated */
mutedForeground: '#94A3B8', /* CarbonScope secondary text */
accent: '#34D399', /* CarbonScope accent - Light emerald */
accentForeground: '#0B1120',
destructive: '#F87171', /* CarbonScope danger */
border: '#1E293B', /* CarbonScope border */
input: '#0D1526', /* CarbonScope input */
ring: 'rgba(5, 150, 105, 0.5)', /* CarbonScope focus ring */
radius: '0.625rem',
/* EN 15978 Lifecycle Charts - CarbonScope */
chart1: '#3B82F6', /* Blue - A1-A3 */
chart2: '#60A5FA', /* Light Blue - A4-A5 */
chart3: '#F59E0B', /* Amber - B1-B5 */
chart4: '#EA580C', /* Orange - B6-B7 */
chart5: '#6B7280', /* Gray - C1-C4 */
},
};
 
export const NAV_THEME: Record<'light' | 'dark', Theme> = {
  light: {
    ...DefaultTheme,
    colors: {
      background: THEME.light.background,
      border: THEME.light.border,
      card: THEME.light.card,
      notification: THEME.light.destructive,
      primary: THEME.light.primary,
      text: THEME.light.foreground,
    },
  },
  dark: {
    ...DarkTheme,
    colors: {
      background: THEME.dark.background,
      border: THEME.dark.border,
      card: THEME.dark.card,
      notification: THEME.dark.destructive,
      primary: THEME.dark.primary,
      text: THEME.dark.foreground,
    },
  },
};