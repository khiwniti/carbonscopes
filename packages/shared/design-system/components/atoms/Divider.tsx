import React from 'react';
import { tokens } from '../../tokens';

export interface DividerProps {
  /** Optional label text */
  label?: string;
}

/**
 * Divider component for visual separation with optional label
 */
export function Divider({ label }: DividerProps) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '8px 0' }}>
      <div style={{ flex: 1, height: 1, background: tokens.border.default }} />
      {label && (
        <span
          style={{
            fontFamily: tokens.font.mono,
            fontSize: 10,
            color: tokens.text.muted,
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            whiteSpace: 'nowrap',
          }}
        >
          {label}
        </span>
      )}
      <div style={{ flex: 1, height: 1, background: tokens.border.default }} />
    </div>
  );
}
