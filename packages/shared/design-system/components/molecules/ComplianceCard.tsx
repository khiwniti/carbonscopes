import React from 'react';
import { tokens } from '../../tokens';

export interface ComplianceCardProps {
  /** Framework name */
  framework: string;
  /** Compliance status */
  status: 'pass' | 'warning' | 'fail';
  /** Current score */
  score: number;
  /** Maximum score */
  maxScore: number;
  /** Additional details */
  details?: string;
}

/**
 * Compliance card component for framework compliance tracking
 */
export function ComplianceCard({ framework, status, score, maxScore, details }: ComplianceCardProps) {
  const pct = (score / maxScore) * 100;

  const statusMap = {
    pass: { color: tokens.status.good, icon: '✓', bg: tokens.status.good_bg },
    warning: { color: tokens.status.warning, icon: '⚠', bg: tokens.status.warning_bg },
    fail: { color: tokens.status.danger, icon: '✕', bg: tokens.status.danger_bg },
  };

  const s = statusMap[status];

  return (
    <div
      style={{
        background: tokens.bg.card,
        borderRadius: tokens.radius.lg,
        padding: 18,
        border: `1px solid ${tokens.border.default}`,
        borderLeft: `3px solid ${s.color}`,
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div
          style={{
            fontFamily: tokens.font.heading,
            fontSize: 14,
            fontWeight: 700,
            color: tokens.text.primary,
          }}
        >
          {framework}
        </div>
        <span
          style={{
            width: 24,
            height: 24,
            borderRadius: tokens.radius.full,
            background: s.bg,
            color: s.color,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 12,
            fontWeight: 700,
          }}
        >
          {s.icon}
        </span>
      </div>
      <div style={{ marginTop: 10, display: 'flex', alignItems: 'baseline', gap: 4 }}>
        <span
          style={{
            fontFamily: tokens.font.heading,
            fontSize: 22,
            fontWeight: 800,
            color: s.color,
          }}
        >
          {score}
        </span>
        <span style={{ fontFamily: tokens.font.mono, fontSize: 11, color: tokens.text.muted }}>
          / {maxScore}
        </span>
      </div>
      <div
        style={{
          marginTop: 8,
          height: 4,
          background: tokens.bg.hover,
          borderRadius: 2,
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${pct}%`,
            background: s.color,
            borderRadius: 2,
            transition: 'width 0.8s ease',
          }}
        />
      </div>
      {details && (
        <div
          style={{
            fontFamily: tokens.font.body,
            fontSize: 11,
            color: tokens.text.muted,
            marginTop: 8,
            lineHeight: 1.5,
          }}
        >
          {details}
        </div>
      )}
    </div>
  );
}
