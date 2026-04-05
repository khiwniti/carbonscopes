import React from 'react';
import { tokens } from '../../tokens';

export interface ToastProps {
  /** Toast message */
  message: string;
  /** Toast type */
  type?: 'success' | 'warning' | 'error' | 'info';
  /** Visibility state */
  visible: boolean;
}

/**
 * Toast notification component for user feedback
 */
export function Toast({ message, type = 'success', visible }: ToastProps) {
  const typeMap = {
    success: {
      icon: '✓',
      color: tokens.status.good,
      bg: tokens.status.good_bg,
      border: 'rgba(16,185,129,0.3)',
    },
    warning: {
      icon: '⚠',
      color: tokens.status.warning,
      bg: tokens.status.warning_bg,
      border: 'rgba(245,158,11,0.3)',
    },
    error: {
      icon: '✕',
      color: tokens.status.danger,
      bg: tokens.status.danger_bg,
      border: 'rgba(239,68,68,0.3)',
    },
    info: {
      icon: 'ℹ',
      color: tokens.status.info,
      bg: tokens.status.info_bg,
      border: 'rgba(59,130,246,0.3)',
    },
  };

  const t = typeMap[type];

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        zIndex: 9999,
        background: tokens.bg.elevated,
        border: `1px solid ${t.border}`,
        borderRadius: tokens.radius.lg,
        padding: '14px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        boxShadow: tokens.shadow.lg,
        backdropFilter: 'blur(8px)',
        transform: visible ? 'translateY(0)' : 'translateY(120%)',
        opacity: visible ? 1 : 0,
        transition: `all 0.4s ${tokens.ease.spring}`,
      }}
    >
      <span
        style={{
          width: 22,
          height: 22,
          borderRadius: tokens.radius.full,
          background: t.bg,
          color: t.color,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 11,
          fontWeight: 700,
          border: `1px solid ${t.border}`,
        }}
      >
        {t.icon}
      </span>
      <span
        style={{
          fontFamily: tokens.font.body,
          fontSize: 13,
          fontWeight: 500,
          color: tokens.text.primary,
        }}
      >
        {message}
      </span>
    </div>
  );
}
