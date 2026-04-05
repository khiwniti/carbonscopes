import React from 'react';
import { tokens } from '../../tokens';

export interface SkeletonProps {
  /** Width (CSS value) */
  w?: string;
  /** Height (CSS value) */
  h?: string;
  /** Border radius (CSS value) */
  r?: string;
}

/**
 * Skeleton loader component for loading states
 */
export function Skeleton({ w = '100%', h = '20px', r = tokens.radius.md }: SkeletonProps) {
  return (
    <div
      style={{
        width: w,
        height: h,
        borderRadius: r,
        background: `linear-gradient(90deg, ${tokens.bg.hover} 25%, ${tokens.bg.elevated} 50%, ${tokens.bg.hover} 75%)`,
        backgroundSize: '200% 100%',
        animation: 'cs-shimmer 1.5s ease-in-out infinite',
      }}
    />
  );
}
