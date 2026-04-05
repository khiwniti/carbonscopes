import React from 'react';
import { tokens } from '../../tokens';

export interface MaterialOption {
  /** Option name */
  name: string;
  /** GWP value */
  gwp: number;
  /** Source/EPD reference */
  source?: string;
}

export interface MaterialComparisonRowProps {
  /** Material category name */
  name: string;
  /** Material options to compare */
  options: MaterialOption[];
}

/**
 * Material comparison row component for side-by-side EPD comparison
 */
export function MaterialComparisonRow({ name, options }: MaterialComparisonRowProps) {
  const best = Math.min(...options.map((o) => o.gwp));

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '160px 1fr',
        gap: 16,
        alignItems: 'center',
        padding: '12px 0',
        borderBottom: `1px solid ${tokens.border.muted}`,
      }}
    >
      <span
        style={{
          fontFamily: tokens.font.heading,
          fontSize: 13,
          fontWeight: 600,
          color: tokens.text.primary,
        }}
      >
        {name}
      </span>
      <div style={{ display: 'flex', gap: 8 }}>
        {options.map((o, i) => (
          <div
            key={i}
            style={{
              flex: 1,
              padding: '10px 12px',
              borderRadius: tokens.radius.md,
              background: o.gwp === best ? tokens.green.glow : tokens.bg.hover,
              border: `1px solid ${o.gwp === best ? tokens.green[800] : tokens.border.muted}`,
              position: 'relative',
            }}
          >
            {o.gwp === best && (
              <span
                style={{
                  position: 'absolute',
                  top: -6,
                  right: 8,
                  background: tokens.green[600],
                  color: '#fff',
                  padding: '1px 6px',
                  borderRadius: tokens.radius.full,
                  fontFamily: tokens.font.mono,
                  fontSize: 8,
                  fontWeight: 700,
                }}
              >
                BEST
              </span>
            )}
            <div
              style={{
                fontFamily: tokens.font.heading,
                fontSize: 16,
                fontWeight: 700,
                color: o.gwp === best ? tokens.green[400] : tokens.text.primary,
              }}
            >
              {o.gwp}
              <span style={{ fontSize: 10, color: tokens.text.muted, marginLeft: 3 }}>
                kgCO₂e
              </span>
            </div>
            <div
              style={{
                fontFamily: tokens.font.body,
                fontSize: 11,
                color: tokens.text.secondary,
                marginTop: 2,
              }}
            >
              {o.name}
            </div>
            {o.source && (
              <div
                style={{
                  fontFamily: tokens.font.mono,
                  fontSize: 9,
                  color: tokens.text.muted,
                  marginTop: 4,
                }}
              >
                {o.source}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
