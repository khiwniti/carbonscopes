'use client';

/**
 * CarbonScope Logo - CORRECT Design from branding_design.jsx
 * 3 Isometric Layers representing EN 15978 lifecycle stages
 */

import React from 'react';
import { cn } from '@/lib/utils';

export interface CarbonScopeLogoSimpleProps {
  size?: number;
  className?: string;
  animate?: boolean;
  glow?: boolean;
}

export function CarbonScopeLogoSimple({
  size = 40,
  className = '',
  animate = false,
  glow = false,
}: CarbonScopeLogoSimpleProps) {
  return (
    <svg
      viewBox="0 0 40 40"
      width={size}
      height={size}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn('flex-shrink-0', className)}
      style={{
        filter: glow ? 'drop-shadow(0 0 16px rgba(52,211,153,0.3))' : 'none',
        animation: animate ? 'cs-glow 3s ease-in-out infinite' : 'none',
      }}
    >
      {/* Layer 1 (Top) - Cyan: A1-A3 Product Stage */}
      <path
        className="layer-1"
        d="M20 4L6 11L20 18L34 11L20 4Z"
        fill="url(#sg-cyan)"
        style={{ animation: animate ? 'cs-layerIn1 0.6s ease both 0.1s' : 'none' }}
      />

      {/* Layer 2 (Middle) - Emerald: A4-B7 Construction & Use */}
      <path
        className="layer-2"
        d="M6 16L20 23L34 16L34 21L20 28L6 21V16Z"
        fill="url(#sg-emerald)"
        style={{ animation: animate ? 'cs-layerIn2 0.6s ease both 0.3s' : 'none' }}
      />

      {/* Layer 3 (Bottom) - Dark Emerald: C1-D Circular Future */}
      <path
        className="layer-3"
        d="M6 26L20 33L34 26L34 31L20 38L6 31V26Z"
        fill="url(#sg-dark)"
        style={{ animation: animate ? 'cs-layerIn3 0.6s ease both 0.5s' : 'none' }}
      />

      <defs>
        {/* Cyan gradient - Product stage */}
        <linearGradient
          id="sg-cyan"
          x1="6"
          y1="4"
          x2="34"
          y2="18"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#22D3EE" />
          <stop offset="1" stopColor="#0891B2" />
        </linearGradient>

        {/* Emerald gradient - Construction & Use */}
        <linearGradient
          id="sg-emerald"
          x1="6"
          y1="16"
          x2="34"
          y2="28"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#34D399" />
          <stop offset="1" stopColor="#059669" />
        </linearGradient>

        {/* Dark emerald gradient - Circular Future */}
        <linearGradient
          id="sg-dark"
          x1="6"
          y1="26"
          x2="34"
          y2="38"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#10B981" />
          <stop offset="1" stopColor="#064E3B" />
        </linearGradient>
      </defs>
    </svg>
  );
}

/**
 * Logo with wordmark (horizontal lockup)
 */
export function CarbonScopeLogoWithText({
  size = 40,
  className = '',
  glow = false,
}: CarbonScopeLogoSimpleProps) {
  const logoSize = size;
  const fontSize = size * 0.55;
  const subSize = size * 0.18;

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <CarbonScopeLogoSimple size={logoSize} glow={glow} />
      <div className="flex flex-col">
        <span
          className="font-heading font-extrabold leading-none tracking-tight"
          style={{ fontSize: `${fontSize}px` }}
        >
          <span className="text-slate-100">Carbon</span>
          <span className="text-emerald-400">Scope</span>
        </span>
        <span
          className="font-mono font-medium text-slate-500 uppercase tracking-widest mt-0.5"
          style={{ fontSize: `${subSize}px`, letterSpacing: '0.14em' }}
        >
          Embodied Carbon Intelligence
        </span>
      </div>
    </div>
  );
}
