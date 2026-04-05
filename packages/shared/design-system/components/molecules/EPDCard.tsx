import React from 'react';
import { useState } from 'react';
import { tokens } from '../../tokens';
import { Badge } from '../atoms/Badge';
import { LifecycleStageTag } from '../atoms/LifecycleStageTag';

export interface EPDCardProps {
  /** Product name */
  product: string;
  /** Manufacturer name */
  manufacturer: string;
  /** Global Warming Potential value */
  gwp: number;
  /** Unit of measurement */
  unit: string;
  /** Product category */
  category: string;
  /** Percentile within category */
  percentile: number;
  /** EPD verification status */
  verified?: boolean;
  /** Lifecycle stage */
  stage?: string;
}

/**
 * EPD (Environmental Product Declaration) card component
 */
export function EPDCard({
  product,
  manufacturer,
  gwp,
  unit,
  category,
  percentile,
  verified,
  stage = 'A1A3',
}: EPDCardProps) {
  const [hover, setHover] = useState(false);

  const percentileColor =
    percentile <= 30 ? tokens.status.good : percentile <= 60 ? tokens.status.warning : tokens.status.danger;

  return (
    <div
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        background: tokens.bg.card,
        borderRadius: tokens.radius.lg,
        padding: 20,
        border: `1px solid ${hover ? tokens.green[800] : tokens.border.default}`,
        transition: `all 0.25s ${tokens.ease.default}`,
        transform: hover ? 'translateY(-2px)' : 'none',
        boxShadow: hover ? tokens.shadow.glow : 'none',
        cursor: 'pointer',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          gap: 8,
        }}
      >
        <div style={{ flex: 1 }}>
          <div
            style={{
              fontFamily: tokens.font.heading,
              fontSize: 14,
              fontWeight: 700,
              color: tokens.text.primary,
            }}
          >
            {product}
          </div>
          <div
            style={{
              fontFamily: tokens.font.body,
              fontSize: 11,
              color: tokens.text.muted,
              marginTop: 2,
            }}
          >
            {manufacturer}
          </div>
        </div>
        <LifecycleStageTag stageKey={stage} />
      </div>
      <div style={{ marginTop: 14, display: 'flex', alignItems: 'baseline', gap: 6 }}>
        <span
          style={{
            fontFamily: tokens.font.heading,
            fontSize: 26,
            fontWeight: 800,
            color: tokens.green[400],
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {gwp}
        </span>
        <span style={{ fontFamily: tokens.font.mono, fontSize: 11, color: tokens.text.muted }}>
          {unit}
        </span>
      </div>
      <div style={{ marginTop: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontFamily: tokens.font.body, fontSize: 10, color: tokens.text.muted }}>
            Category Percentile
          </span>
          <span
            style={{
              fontFamily: tokens.font.mono,
              fontSize: 10,
              fontWeight: 600,
              color: percentileColor,
            }}
          >
            {percentile}th
          </span>
        </div>
        <div
          style={{
            height: 4,
            background: tokens.bg.hover,
            borderRadius: 2,
            position: 'relative',
          }}
        >
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              bottom: 0,
              width: `${percentile}%`,
              background: percentileColor,
              borderRadius: 2,
              transition: 'width 0.6s ease',
            }}
          />
          <div
            style={{
              position: 'absolute',
              left: '20%',
              top: -2,
              bottom: -2,
              width: 1,
              background: tokens.text.muted,
              opacity: 0.3,
            }}
          />
        </div>
      </div>
      <div style={{ marginTop: 12, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        <Badge variant="default">{category}</Badge>
        {verified && (
          <Badge variant="success" dot>
            Verified EPD
          </Badge>
        )}
      </div>
    </div>
  );
}
