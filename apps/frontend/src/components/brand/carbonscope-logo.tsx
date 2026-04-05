/**
 * CarbonScope Logo Component
 * 
 * 3-layer strata design representing carbon lifecycle stages (EN 15978)
 * Variants: full (logo + wordmark), icon (logo only), wordmark (text only)
 * Sizes: sm (24px), md (32px), lg (48px), xl (64px)
 * Themes: light, dark, auto
 */

import React from 'react';
import { carbonScope } from '@/lib/design-tokens';

export interface CarbonScopeLogoProps {
  /** Logo variant */
  variant?: 'full' | 'icon' | 'wordmark';
  /** Logo size */
  size?: 'sm' | 'md' | 'lg' | 'xl' | number;
  /** Color theme */
  theme?: 'light' | 'dark' | 'auto';
  /** Additional CSS classes */
  className?: string;
  /** Animate on hover */
  animated?: boolean;
}

const sizeMap = {
  sm: 24,
  md: 32,
  lg: 48,
  xl: 64,
};

export function CarbonScopeLogo({
  variant = 'full',
  size = 'md',
  theme = 'auto',
  className = '',
  animated = false,
}: CarbonScopeLogoProps) {
  const logoSize = typeof size === 'number' ? size : sizeMap[size];
  const wordmarkWidth = logoSize * 4; // Wordmark is ~4x wider than logo

  // Determine colors based on theme
  const isDark = theme === 'dark' || (theme === 'auto' && typeof window !== 'undefined');
  const primaryColor = carbonScope.colors.primary;
  const textColor = isDark ? carbonScope.colors.textPrimary : carbonScope.colors.background;

  const renderIcon = () => (
    <svg
      width={logoSize}
      height={logoSize}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`${animated ? 'transition-transform hover:scale-110' : ''} ${className}`}
    >
      {/* Bottom Layer (A1-A3) - Emerald */}
      <path
        d="M8 48L32 56L56 48V32L32 40L8 32V48Z"
        fill={carbonScope.colors.lifecycle.a1a3}
        opacity="0.9"
      />
      <path
        d="M8 48L32 56L56 48V32L32 40L8 32V48Z"
        stroke={carbonScope.colors.lifecycle.a1a3Dark}
        strokeWidth="1"
        opacity="0.5"
      />

      {/* Middle Layer (B1-B7) - Violet to Amber gradient */}
      <defs>
        <linearGradient id="middleGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={carbonScope.colors.lifecycle.b1b5} />
          <stop offset="100%" stopColor={carbonScope.colors.lifecycle.b6b7} />
        </linearGradient>
      </defs>
      <path
        d="M8 32L32 40L56 32V16L32 24L8 16V32Z"
        fill="url(#middleGradient)"
        opacity="0.85"
      />
      <path
        d="M8 32L32 40L56 32V16L32 24L8 16V32Z"
        stroke={carbonScope.colors.lifecycle.b1b5Dark}
        strokeWidth="1"
        opacity="0.5"
      />

      {/* Top Layer (C1-D) - Red to Indigo gradient */}
      <defs>
        <linearGradient id="topGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={carbonScope.colors.lifecycle.c1c4} />
          <stop offset="100%" stopColor={carbonScope.colors.lifecycle.d} />
        </linearGradient>
      </defs>
      <path
        d="M8 16L32 24L56 16V8L32 16L8 8V16Z"
        fill="url(#topGradient)"
        opacity="0.8"
      />
      <path
        d="M8 16L32 24L56 16V8L32 16L8 8V16Z"
        stroke={carbonScope.colors.lifecycle.c1c4Dark}
        strokeWidth="1"
        opacity="0.5"
      />

      {/* Center accent - Emerald glow */}
      <circle
        cx="32"
        cy="32"
        r="4"
        fill={primaryColor}
        opacity="0.6"
      />
      <circle
        cx="32"
        cy="32"
        r="4"
        fill="none"
        stroke={primaryColor}
        strokeWidth="2"
        opacity="0.4"
      >
        {animated && (
          <animate
            attributeName="r"
            values="4;6;4"
            dur="2s"
            repeatCount="indefinite"
          />
        )}
      </circle>
    </svg>
  );

  const renderWordmark = () => (
    <svg
      width={wordmarkWidth}
      height={logoSize}
      viewBox="0 0 256 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <text
        x="0"
        y="48"
        fontFamily={carbonScope.typography.fontHeading}
        fontSize="40"
        fontWeight={carbonScope.typography.fontWeight.bold}
        fill={textColor}
        letterSpacing="-0.02em"
      >
        CarbonScope
      </text>
      {/* Emerald underline accent */}
      <rect
        x="0"
        y="54"
        width="256"
        height="3"
        fill={primaryColor}
        opacity="0.6"
      />
    </svg>
  );

  // Render based on variant
  switch (variant) {
    case 'icon':
      return renderIcon();
    
    case 'wordmark':
      return renderWordmark();
    
    case 'full':
    default:
      return (
        <div className={`flex items-center gap-3 ${className}`}>
          {renderIcon()}
          {renderWordmark()}
        </div>
      );
  }
}

/**
 * Animated logo variant with lifecycle pulse effect
 */
export function CarbonScopeAnimatedLogo(props: Omit<CarbonScopeLogoProps, 'animated'>) {
  return <CarbonScopeLogo {...props} animated={true} />;
}

/**
 * Logo with BKS prefix
 */
export function BKSCarbonScopeLogo(props: CarbonScopeLogoProps) {
  const { size = 'md', className = '' } = props;
  const logoSize = typeof size === 'number' ? size : sizeMap[size];
  
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span 
        style={{
          fontFamily: carbonScope.typography.fontHeading,
          fontSize: logoSize * 0.5,
          fontWeight: carbonScope.typography.fontWeight.semibold,
          color: carbonScope.colors.textMuted,
          letterSpacing: '0.1em',
        }}
      >
        BKS
      </span>
      <div style={{ 
        width: '1px',
        height: logoSize * 0.6,
        backgroundColor: carbonScope.colors.border,
        opacity: 0.5,
      }} />
      <CarbonScopeLogo {...props} variant="full" />
    </div>
  );
}
