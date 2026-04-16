import React from 'react';
import { tokens, LIFECYCLE_STAGES } from '../../tokens';
import { useInView } from '../hooks/useInView';
import { Badge } from '../atoms/Badge';

export interface LifecycleDataPoint {
  /** Lifecycle stage key */
  key: string;
  /** Carbon value */
  value: number;
}

export interface LifecycleBarChartProps {
  /** Array of lifecycle data points */
  data: LifecycleDataPoint[];
  /** Chart height in pixels */
  height?: number;
}

/**
 * Lifecycle bar chart component for EN 15978 stage breakdown
 */
export function LifecycleBarChart({ data, height = 260 }: LifecycleBarChartProps) {
  const [ref, inView] = useInView();
  const maxVal = Math.max(...data.map((d) => d.value));
  if (maxVal === 0) return <div style={{color: tokens.text.muted}}>No data available</div>;

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
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 20,
        }}
      >
        <div>
          <div
            style={{
              fontFamily: tokens.font.heading,
              fontSize: 15,
              fontWeight: 700,
              color: tokens.text.primary,
            }}
          >
            Lifecycle Stage Breakdown
          </div>
          <div
            style={{
              fontFamily: tokens.font.body,
              fontSize: 12,
              color: tokens.text.muted,
              marginTop: 2,
            }}
          >
            kgCO₂e by EN 15978 module
          </div>
        </div>
        <Badge variant="accent">EN 15978</Badge>
      </div>
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: 10,
          height,
          paddingBottom: 28,
          position: 'relative',
        }}
      >
        {/* Y-axis grid */}
        {[0, 0.25, 0.5, 0.75, 1].map((pct) => (
          <div
            key={pct}
            style={{
              position: 'absolute',
              left: 0,
              right: 0,
              bottom: 28 + (height - 28) * pct,
              borderBottom: `1px ${pct === 0 ? 'solid' : 'dashed'} ${tokens.border.muted}`,
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <span
              style={{
                position: 'absolute',
                left: -4,
                transform: 'translateX(-100%)',
                fontFamily: tokens.font.mono,
                fontSize: 9,
                color: tokens.text.muted,
                paddingRight: 4,
              }}
            >
              {Math.round((maxVal * pct) / 1000)}k
            </span>
          </div>
        ))}
        {data.map((d, i) => {
          const stage = LIFECYCLE_STAGES.find((s) => s.key === d.key) || LIFECYCLE_STAGES[0];
          const barH = (d.value / maxVal) * (height - 28);
          const isNeg = d.key === 'D';
          return (
            <div
              key={d.key}
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 4,
                position: 'relative',
                zIndex: 1,
              }}
            >
              <span
                style={{
                  fontFamily: tokens.font.mono,
                  fontSize: 10,
                  fontWeight: 600,
                  color: stage.color,
                  opacity: inView ? 1 : 0,
                  transition: 'opacity 0.4s ease',
                  transitionDelay: `${i * 80}ms`,
                }}
              >
                {(d.value / 1000).toFixed(0)}k
              </span>
              <div
                style={{
                  width: '100%',
                  maxWidth: 52,
                  height: barH,
                  borderRadius: '6px 6px 2px 2px',
                  background: `linear-gradient(180deg, ${stage.color}, ${stage.color}88)`,
                  transformOrigin: 'bottom',
                  transform: inView ? 'scaleY(1)' : 'scaleY(0)',
                  transition: `transform 0.6s ${tokens.ease.spring}`,
                  transitionDelay: `${i * 80}ms`,
                  boxShadow: `0 0 12px ${stage.color}22`,
                  opacity: isNeg ? 0.6 : 1,
                }}
              />
              <div style={{ textAlign: 'center' }}>
                <div
                  style={{
                    fontFamily: tokens.font.mono,
                    fontSize: 10,
                    fontWeight: 700,
                    color: stage.color,
                  }}
                >
                  {stage.label}
                </div>
                <div
                  style={{
                    fontFamily: tokens.font.body,
                    fontSize: 9,
                    color: tokens.text.muted,
                  }}
                >
                  {stage.name}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
