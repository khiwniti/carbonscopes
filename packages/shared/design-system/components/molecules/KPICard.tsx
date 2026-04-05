import React from 'react';
import { tokens } from '../../tokens';
import { useInView } from '../hooks/useInView';
import { useCountUp } from '../hooks/useCountUp';

export interface KPICardProps {
  /** Card label */
  label: string;
  /** Numeric or string value */
  value: number | string;
  /** Unit label (e.g., "kgCO₂e") */
  unit?: string;
  /** Trend percentage (positive = increase, negative = decrease) */
  trend?: number;
  /** Trend context label */
  trendLabel?: string;
  /** Target value */
  target?: string;
  /** Target label */
  targetLabel?: string;
  /** Sparkline data array */
  sparkData?: number[];
  /** Optional icon */
  icon?: React.ReactNode;
  /** Status indicator */
  status?: 'good' | 'warning' | 'danger';
}

/**
 * KPI card component for key metrics with animations and trend indicators
 */
export function KPICard({
  label,
  value,
  unit,
  trend,
  trendLabel,
  target,
  targetLabel,
  sparkData,
  icon,
  status = 'good',
}: KPICardProps) {
  const [ref, inView] = useInView();
  const numericValue = typeof value === 'number' ? value : 0;
  const animatedValue = useCountUp(numericValue, 1000, inView);

  const trendColor = trend !== undefined && trend > 0 ? tokens.status.danger : tokens.status.good;
  const trendIcon = trend !== undefined && trend > 0 ? '↑' : '↓';

  const statusColors = {
    good: tokens.status.good,
    warning: tokens.status.warning,
    danger: tokens.status.danger,
  };

  return (
    <div
      ref={ref}
      style={{
        background: tokens.bg.card,
        borderRadius: tokens.radius.lg,
        padding: '20px 22px',
        border: `1px solid ${tokens.border.default}`,
        animation: inView ? 'cs-fadeUp 0.5s ease both' : 'none',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 2,
          background: statusColors[status],
          opacity: 0.6,
        }}
      />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <span
          style={{
            fontFamily: tokens.font.body,
            fontSize: 11,
            fontWeight: 600,
            color: tokens.text.muted,
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
          }}
        >
          {label}
        </span>
        {icon && <span style={{ fontSize: 16, opacity: 0.5 }}>{icon}</span>}
      </div>
      <div style={{ marginTop: 10, display: 'flex', alignItems: 'baseline', gap: 6 }}>
        <span
          style={{
            fontFamily: tokens.font.heading,
            fontSize: 32,
            fontWeight: 800,
            color: tokens.text.primary,
            letterSpacing: '-0.02em',
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {typeof value === 'number' ? animatedValue.toLocaleString() : value}
        </span>
        {unit && (
          <span style={{ fontFamily: tokens.font.mono, fontSize: 12, color: tokens.text.muted }}>
            {unit}
          </span>
        )}
      </div>
      {(trend !== undefined || target) && (
        <div
          style={{
            marginTop: 10,
            display: 'flex',
            gap: 12,
            alignItems: 'center',
            flexWrap: 'wrap',
          }}
        >
          {trend !== undefined && (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 3,
                fontFamily: tokens.font.mono,
                fontSize: 11,
                fontWeight: 600,
                color: trendColor,
              }}
            >
              {trendIcon} {Math.abs(trend)}%
              {trendLabel && (
                <span style={{ color: tokens.text.muted, fontWeight: 400 }}>{trendLabel}</span>
              )}
            </span>
          )}
          {target && (
            <span style={{ fontFamily: tokens.font.mono, fontSize: 11, color: tokens.text.muted }}>
              Target: {targetLabel || target}
            </span>
          )}
        </div>
      )}
      {sparkData && (
        <div
          style={{
            marginTop: 12,
            display: 'flex',
            alignItems: 'flex-end',
            gap: 2,
            height: 28,
          }}
        >
          {sparkData.map((val, i) => (
            <div
              key={i}
              style={{
                flex: 1,
                background: `${tokens.green[500]}${i === sparkData.length - 1 ? '' : '44'}`,
                borderRadius: 2,
                height: `${(val / Math.max(...sparkData)) * 100}%`,
                transition: 'height 0.4s ease',
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
