import React from 'react';
import { tokens, LIFECYCLE_STAGES } from '../../tokens';
import { useInView } from '../hooks/useInView';

export interface ComparisonOptionData {
  [key: string]: number;
}

export interface ComparisonOption {
  /** Option label */
  label: string;
  /** Lifecycle stage data */
  data: ComparisonOptionData;
  /** Is this the best option? */
  best?: boolean;
}

export interface StackedBarComparisonProps {
  /** Array of comparison options */
  options: ComparisonOption[];
}

/**
 * Stacked bar comparison component for design option analysis
 */
export function StackedBarComparison({ options }: StackedBarComparisonProps) {
  const [ref, inView] = useInView();

  const maxTotal = Math.max(
    ...options.map((o) => LIFECYCLE_STAGES.reduce((sum, st) => sum + (o.data[st.key] || 0), 0))
  );

  return (
    <div
      ref={ref}
      style={{
        background: tokens.bg.card,
        borderRadius: tokens.radius.lg,
        padding: 24,
        border: `1px solid ${tokens.border.default}`,
      }}
    >
      <div
        style={{
          fontFamily: tokens.font.heading,
          fontSize: 15,
          fontWeight: 700,
          color: tokens.text.primary,
          marginBottom: 20,
        }}
      >
        Design Option Comparison
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {options.map((opt, oi) => {
          const total = LIFECYCLE_STAGES.reduce((sum, st) => sum + (opt.data[st.key] || 0), 0);
          return (
            <div key={oi}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span
                  style={{
                    fontFamily: tokens.font.heading,
                    fontSize: 13,
                    fontWeight: 600,
                    color: tokens.text.primary,
                  }}
                >
                  {opt.label}
                </span>
                <span
                  style={{
                    fontFamily: tokens.font.mono,
                    fontSize: 12,
                    fontWeight: 600,
                    color: opt.best ? tokens.green[400] : tokens.text.secondary,
                  }}
                >
                  {(total / 1000).toFixed(0)}k kgCO₂e
                  {opt.best && (
                    <span style={{ marginLeft: 6, color: tokens.green[400] }}>✓ Best</span>
                  )}
                </span>
              </div>
              <div
                style={{
                  display: 'flex',
                  height: 28,
                  borderRadius: tokens.radius.sm,
                  overflow: 'hidden',
                  border: `1px solid ${opt.best ? tokens.green[800] : tokens.border.muted}`,
                }}
              >
                {LIFECYCLE_STAGES.map((st) => {
                  const val = opt.data[st.key] || 0;
                  const w = (val / maxTotal) * 100;
                  return (
                    <div
                      key={st.key}
                      title={`${st.label}: ${val.toLocaleString()} kgCO₂e`}
                      style={{
                        width: inView ? `${w}%` : '0%',
                        background: st.color,
                        transition: `width 0.8s ${tokens.ease.smooth}`,
                        transitionDelay: `${oi * 100}ms`,
                      }}
                    />
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 16 }}>
        {LIFECYCLE_STAGES.map((s) => (
          <div key={s.key} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: 2,
                background: s.color,
              }}
            />
            <span style={{ fontFamily: tokens.font.mono, fontSize: 9, color: tokens.text.muted }}>
              {s.label} {s.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
