'use client';

import { useEffect, useState, Suspense, lazy } from 'react';

/**
 * CarbonScope Global Background
 *
 * Applies the landing page's signature dark engineering aesthetic
 * across all pages — animated gradient contours, emerald/cyan glow orbs,
 * and subtle contour grid lines on the #0B1120 navy base.
 */

const AnimatedBg = lazy(() =>
  import('@/components/ui/animated-bg').then(mod => ({ default: mod.AnimatedBg }))
);

export function CarbonBackground() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 0,
        overflow: 'hidden',
        background: '#0B1120',
      }}
    >
      {/* Animated gradient background contours */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.4,
          background: `
            radial-gradient(circle at 20% 30%, rgba(16, 185, 129, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(34, 211, 238, 0.12) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(6, 78, 59, 0.08) 0%, transparent 70%)
          `,
          animation: 'luxuryPulse 8s ease-in-out infinite',
        }}
      />

      {/* Contour grid lines */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.06,
          background: `
            repeating-linear-gradient(
              0deg,
              transparent,
              transparent 100px,
              rgba(16, 185, 129, 0.3) 100px,
              rgba(16, 185, 129, 0.3) 101px
            ),
            repeating-linear-gradient(
              90deg,
              transparent,
              transparent 100px,
              rgba(34, 211, 238, 0.2) 100px,
              rgba(34, 211, 238, 0.2) 101px
            )
          `,
          animation: 'contourShift 20s linear infinite',
        }}
      />

      {/* Glow orbs */}
      <div
        style={{
          position: 'absolute',
          top: '10%',
          left: '15%',
          width: '400px',
          height: '400px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, transparent 70%)',
          filter: 'blur(60px)',
          animation: 'float 12s ease-in-out infinite',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '15%',
          right: '20%',
          width: '350px',
          height: '350px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(34, 211, 238, 0.12) 0%, transparent 70%)',
          filter: 'blur(70px)',
          animation: 'float 15s ease-in-out infinite reverse',
        }}
      />

      {/* Framer-motion animated arcs (subtle, for additional depth) */}
      {mounted && (
        <Suspense fallback={null}>
          <AnimatedBg
            variant="hero"
            blurMultiplier={2}
            sizeMultiplier={1.2}
          />
        </Suspense>
      )}
    </div>
  );
}