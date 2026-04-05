import React from 'react';
import { tokens } from '../../tokens';
import { useInView } from '../hooks/useInView';
import { Badge } from '../atoms/Badge';

export interface BenchmarkBand {
  /** Minimum value for this band */
  min: number;
  /** Maximum value for this band */
  max: number;
  /** Band label (e.g., "A+", "Good") */
  label: string;
  /** Band color */
  color: string;
  /** Badge variant */
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'accent';
}

export interface BenchmarkGaugeProps {
  /** Current value */
  value: number;
  /** Benchmark bands configuration */
  bands: BenchmarkBand[];
  /** Gauge label */
  label: string;
  /** Unit of measurement */
  unit?: string;
}

/**
 * Benchmark gauge component for comparing values against rating bands
 */
export function BenchmarkGauge({ value, bands, label, unit = 'kgCO₂e/m²' }: BenchmarkGaugeProps) {
  const [ref, inView] = useInView();
  const total = bands[bands.length - 1].max;
  const pct = Math.min((value / total) * 100, 100);
  const currentBand = bands.find((b) => value >= b.min && value < b.max) || bands[bands.length - 1];

  return (
    <div
      ref={ref}
      style={{
        background: tokens.bg.card,
        borderRadius: tokens.radius.lg,
        padding: 20,
        border: `1px solid ${tokens.border.default}`,
      }}
    >
      <div
        style={{
          fontFamily: tokens.font.heading,
          fontSize: 13,
          fontWeight: 700,
          color: tokens.text.primary,
          marginBottom: 4,
        }}
      >
        {label}
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 5, marginBottom: 14 }}>
        <span
          style={{
            fontFamily: tokens.font.heading,
            fontSize: 24,
            fontWeight: 800,
            color: currentBand.color,
          }}
        >
          {value}
        </span>
        <span style={{ fontFamily: tokens.font.mono, fontSize: 11, color: tokens.text.muted }}>
          {unit}
        </span>
        <Badge variant={currentBand.variant || 'default'}>{currentBand.label}</Badge>
      </div>
      <div
        style={{
          position: 'relative',
          height: 10,
          borderRadius: 5,
          overflow: 'hidden',
          display: 'flex',
        }}
      >
        {bands.map((b, i) => (
          <div
            key={i}
            style={{ flex: b.max - b.min, height: '100%', background: `${b.color}44` }}
          />
        ))}
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            bottom: 0,
            width: inView ? `${pct}%` : '0%',
            transition: 'width 1s cubic-bezier(0.45,0,0.15,1)',
            background: currentBand.color,
            borderRadius: 5,
            boxShadow: `0 0 8px ${currentBand.color}44`,
          }}
        />
      </div>
      <div style={{ display: 'flex', marginTop: 6 }}>
        {bands.map((b, i) => (
          <div
            key={i}
            style={{
              flex: b.max - b.min,
              fontFamily: tokens.font.mono,
              fontSize: 8,
              color: tokens.text.muted,
              textAlign: 'center',
            }}
          >
            {b.label}
          </div>
        ))}
      </div>
    </div>
  );
}
