import React, { useState } from 'react';
import { tokens } from '../../tokens';

export interface ButtonProps {
  /** Button content */
  children: React.ReactNode;
  /** Visual variant */
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  /** Button size */
  size?: 'sm' | 'md' | 'lg';
  /** Optional icon element */
  icon?: React.ReactNode;
  /** Click handler */
  onClick?: () => void;
  /** Disabled state */
  disabled?: boolean;
}

/**
 * Button component with multiple variants and sizes
 */
export function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  onClick,
  disabled,
}: ButtonProps) {
  const [hover, setHover] = useState(false);

  const sizeStyles = {
    sm: { padding: '6px 14px', fontSize: 12 },
    md: { padding: '9px 20px', fontSize: 13 },
    lg: { padding: '12px 28px', fontSize: 14 },
  };

  const variantStyles = {
    primary: {
      bg: hover ? tokens.green[700] : tokens.green[600],
      color: '#fff',
      border: 'none',
      shadow: `0 0 16px ${tokens.green.glow}`,
    },
    secondary: {
      bg: hover ? tokens.bg.hover : 'transparent',
      color: tokens.text.primary,
      border: `1px solid ${hover ? tokens.border.hover : tokens.border.default}`,
      shadow: 'none',
    },
    ghost: {
      bg: hover ? tokens.green.glow : 'transparent',
      color: tokens.green[400],
      border: 'none',
      shadow: 'none',
    },
    danger: {
      bg: hover ? '#991B1B' : tokens.status.danger,
      color: '#fff',
      border: 'none',
      shadow: 'none',
    },
  };

  const sz = sizeStyles[size];
  const v = variantStyles[variant];

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        padding: sz.padding,
        fontSize: sz.fontSize,
        background: v.bg,
        color: v.color,
        border: v.border || 'none',
        borderRadius: tokens.radius.md,
        fontFamily: tokens.font.body,
        fontWeight: 600,
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        transition: `all 0.2s ${tokens.ease.default}`,
        letterSpacing: '0.01em',
        boxShadow: variant === 'primary' && hover ? v.shadow : 'none',
      }}
    >
      {icon}
      {children}
    </button>
  );
}
