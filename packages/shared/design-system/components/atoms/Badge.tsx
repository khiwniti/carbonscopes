import React from 'react';
import { tokens } from '../../tokens';

// Badge style constants
const BADGE_GAP = 6;
const BADGE_PADDING = '3px 10px';
const BADGE_FONT_SIZE = 11;
const BADGE_FONT_WEIGHT = 600;
const BADGE_DOT_SIZE = 5;

export interface BadgeProps {
  /** Badge content */
  children: React.ReactNode;
  /** Visual variant */
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'accent';
  /** Show colored dot indicator */
  dot?: boolean;
}

/**
 * Badge component for status indicators and labels
 */
export function Badge({ children, variant = 'default', dot }: BadgeProps) {
  const variantMap = {
    default: { bg: tokens.bg.hover, color: tokens.text.secondary, border: tokens.border.default },
    success: { bg: tokens.status.good_bg, color: tokens.status.good, border: 'rgba(16,185,129,0.2)' },
    warning: { bg: tokens.status.warning_bg, color: tokens.status.warning, border: 'rgba(245,158,11,0.2)' },
    danger: { bg: tokens.status.danger_bg, color: tokens.status.danger, border: 'rgba(239,68,68,0.2)' },
    info: { bg: tokens.status.info_bg, color: tokens.status.info, border: 'rgba(59,130,246,0.2)' },
    accent: { bg: tokens.green.glow, color: tokens.green[400], border: 'rgba(52,211,153,0.2)' },
  };

  const styles = variantMap[variant];

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: BADGE_GAP,
        padding: BADGE_PADDING,
        borderRadius: tokens.radius.full,
        background: styles.bg,
        color: styles.color,
        border: `1px solid ${styles.border}`,
        fontFamily: tokens.font.body,
        fontSize: BADGE_FONT_SIZE,
        fontWeight: BADGE_FONT_WEIGHT,
        letterSpacing: '0.04em',
        textTransform: 'uppercase',
        lineHeight: '18px',
      }}
    >
      {dot && (
        <span
          style={{
            width: BADGE_DOT_SIZE,
            height: BADGE_DOT_SIZE,
            borderRadius: '50%',
            background: styles.color,
          }}
        />
      )}
      {children}
    </span>
  );
}
