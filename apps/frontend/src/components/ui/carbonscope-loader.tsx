'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

interface CarbonScopeLoaderProps {
  /**
   * Size preset for the loader
   * @default 'medium'
   */
  size?: 'small' | 'medium' | 'large' | 'xlarge';
  /**
   * Custom size in pixels (overrides size preset)
   */
  customSize?: number;
  /**
   * Animation speed multiplier (affects spin duration)
   * @default 1.0
   */
  speed?: number;
  /**
   * Additional className for the container
   */
  className?: string;
  /**
   * Additional style for the container
   */
  style?: React.CSSProperties;
  /**
   * Whether the animation should autoPlay
   * @default true
   */
  autoPlay?: boolean;
  /**
   * Whether the animation should loop
   * @default true
   */
  loop?: boolean;
  /**
   * Force a specific loader variant (overrides auto-detection).
   * Use 'white' on dark backgrounds, 'black' on light backgrounds.
   * @default 'auto'
   */
  variant?: 'white' | 'black' | 'auto';
  /**
   * Force light or dark theme for the loader colour.
   * @deprecated Use 'variant' instead
   */
  forceTheme?: 'light' | 'dark';
}

const SIZE_MAP = {
  small: 20,
  medium: 40,
  large: 80,
  xlarge: 120,
} as const;

/**
 * CarbonScopeLoader - Emerald green circular loading animation for CarbonScope
 *
 * Uses CSS-based circular spinner with emerald green (#34D399) branding and
 * signature CarbonScope glow effect. Optimized for dark backgrounds.
 *
 * **Design Tokens:**
 * - Primary Color: Emerald Green (#34D399 / cs-green-400)
 * - Glow Effect: 0 0 16px rgba(52, 211, 153, 0.15)
 * - Border Base: rgba(52, 211, 153, 0.2)
 *
 * @example
 * ```tsx
 * // Default medium size
 * <CarbonScopeLoader />
 *
 * // Large loader
 * <CarbonScopeLoader size="large" />
 *
 * // Custom pixel-perfect size
 * <CarbonScopeLoader customSize={64} />
 *
 * // Slower animation
 * <CarbonScopeLoader speed={0.5} />
 * ```
 */
export function CarbonScopeLoader({
  size = 'medium',
  customSize,
  speed = 1.0,
  className,
  style,
  autoPlay = true,
  loop = true,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  variant,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  forceTheme,
}: CarbonScopeLoaderProps) {
  const loaderSize = customSize || SIZE_MAP[size];

  // Track mounted state to prevent hydration mismatch
  const [mounted, setMounted] = React.useState(false);

  // Set mounted on client
  React.useEffect(() => {
    setMounted(true);
  }, []);

  // Calculate border width based on size (roughly 1/16 of the size, min 2px)
  const borderWidth = Math.max(2, Math.round(loaderSize / 16));

  // Calculate animation duration based on speed (lower speed = slower rotation)
  const animationDuration = 0.8 / speed;

  // CarbonScope design tokens
  const borderColor = 'rgba(52, 211, 153, 0.2)'; // cs-green-400 with 20% opacity
  const spinnerColor = '#34D399'; // cs-green-400
  const glowEffect = '0 0 16px rgba(52, 211, 153, 0.15)';

  // Don't render during SSR - render a placeholder instead
  if (!mounted) {
    return (
      <div
        className={cn('flex items-center justify-center', className)}
        style={style}
      >
        <div
          style={{
            width: loaderSize,
            height: loaderSize
          }}
        />
      </div>
    );
  }

  return (
    <div className={cn('flex items-center justify-center', className)} style={style}>
      <div
        style={{
          width: loaderSize,
          height: loaderSize,
          border: `${borderWidth}px solid ${borderColor}`,
          borderTopColor: spinnerColor,
          borderRadius: '50%',
          boxShadow: glowEffect,
          animation: autoPlay && loop
            ? `carbonscope-spin ${animationDuration}s linear infinite`
            : autoPlay
              ? `carbonscope-spin ${animationDuration}s linear`
              : 'none',
        }}
      />
      <style jsx>{`
        @keyframes carbonscope-spin {
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
}
