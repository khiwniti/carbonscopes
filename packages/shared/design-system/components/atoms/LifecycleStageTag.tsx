import React from 'react';
import { tokens, LIFECYCLE_STAGES } from '../../tokens';

export interface LifecycleStageTagProps {
  /** Lifecycle stage key (e.g., "A1A3", "B6B7") */
  stageKey: string;
}

/**
 * Lifecycle stage tag component for EN 15978 modules
 */
export function LifecycleStageTag({ stageKey }: LifecycleStageTagProps) {
  const stage = LIFECYCLE_STAGES.find((s) => s.key === stageKey) || LIFECYCLE_STAGES[0];

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5,
        padding: '2px 8px',
        borderRadius: tokens.radius.sm,
        background: stage.bg,
        border: `1px solid ${stage.color}22`,
        fontFamily: tokens.font.mono,
        fontSize: 11,
        fontWeight: 600,
        color: stage.color,
      }}
    >
      <span
        style={{
          width: 6,
          height: 6,
          borderRadius: 2,
          background: stage.color,
        }}
      />
      {stage.label}
    </span>
  );
}
