import React, { useState } from 'react';
import { tokens } from '../../tokens';
import { Divider } from '../atoms/Divider';

const NAV_ITEMS = [
  { label: 'Dashboard', icon: '📊' },
  { label: 'Materials', icon: '🧱' },
  { label: 'BIM Import', icon: '📐' },
  { label: 'Reports', icon: '📄' },
  { label: 'Settings', icon: '⚙' },
] as const;

const LIFECYCLE_SCOPES = ['A1-A3', 'A1-A5', 'A-C', 'A-D'] as const;

const FRAMEWORKS = ['RICS', 'LETI', 'BREEAM', 'LEED', 'DGNB', 'RE2020'] as const;

export interface ProjectSidebarProps {
  /** Active nav item index (0-based). Defaults to 0 (Dashboard). */
  activeNavIndex?: number;
  /** GIA in m² for the study period info panel. */
  gia?: number;
  /** Study period in years. */
  studyPeriod?: number;
  /** Callback when a nav item is clicked. */
  onNavClick?: (index: number) => void;
}

/**
 * Project navigation sidebar for the CarbonScope dashboard.
 * Contains branding, nav links, lifecycle scope selector, framework selector,
 * and a study period summary panel.
 */
export function ProjectSidebar({
  activeNavIndex = 0,
  gia = 12450,
  studyPeriod = 60,
  onNavClick,
}: ProjectSidebarProps) {
  const [scope, setScope] = useState<string>('A-C');
  const [framework, setFramework] = useState<string>('RICS');

  return (
    <div
      style={{
        width: 240,
        background: tokens.bg.surface,
        borderRight: `1px solid ${tokens.border.default}`,
        padding: '20px 16px',
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
        fontSize: 12,
        flexShrink: 0,
      }}
    >
      {/* ── Logo ── */}
      <div>
        <div
          style={{
            fontFamily: tokens.font.heading,
            fontSize: 16,
            fontWeight: 800,
            color: tokens.green[400],
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <span
            style={{
              width: 28,
              height: 28,
              borderRadius: tokens.radius.md,
              background: tokens.green.glow,
              border: `1px solid ${tokens.green[800]}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 14,
              flexShrink: 0,
            }}
          >
            ◇
          </span>
          CarbonScope
        </div>
      </div>

      <Divider label="navigation" />

      {/* ── Nav Items ── */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {NAV_ITEMS.map((item, i) => {
          const isActive = i === activeNavIndex;
          return (
            <button
              key={item.label}
              onClick={() => onNavClick?.(i)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '8px 10px',
                borderRadius: tokens.radius.md,
                background: isActive ? tokens.green.glow : 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: isActive ? tokens.green[400] : tokens.text.muted,
                fontFamily: tokens.font.body,
                fontSize: 13,
                fontWeight: isActive ? 600 : 400,
                transition: `all 0.15s ${tokens.ease.default}`,
                width: '100%',
                textAlign: 'left',
                borderLeft: isActive
                  ? `2px solid ${tokens.green[500]}`
                  : '2px solid transparent',
              }}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          );
        })}
      </nav>

      <Divider label="scope" />

      {/* ── Lifecycle Scope Selector ── */}
      <div>
        <div
          style={{
            fontFamily: tokens.font.body,
            fontSize: 10,
            fontWeight: 600,
            color: tokens.text.muted,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            marginBottom: 6,
          }}
        >
          Lifecycle Scope
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {LIFECYCLE_SCOPES.map((s) => {
            const isActive = scope === s;
            return (
              <button
                key={s}
                onClick={() => setScope(s)}
                style={{
                  padding: '4px 10px',
                  borderRadius: tokens.radius.sm,
                  background: isActive ? tokens.green[600] : tokens.bg.hover,
                  border: `1px solid ${isActive ? tokens.green[500] : tokens.border.muted}`,
                  color: isActive ? '#fff' : tokens.text.muted,
                  fontFamily: tokens.font.mono,
                  fontSize: 10,
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: `all 0.15s ${tokens.ease.default}`,
                }}
              >
                {s}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Framework Selector ── */}
      <div>
        <div
          style={{
            fontFamily: tokens.font.body,
            fontSize: 10,
            fontWeight: 600,
            color: tokens.text.muted,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            marginBottom: 6,
          }}
        >
          Framework
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {FRAMEWORKS.map((f) => {
            const isActive = framework === f;
            return (
              <button
                key={f}
                onClick={() => setFramework(f)}
                style={{
                  padding: '5px 10px',
                  borderRadius: tokens.radius.sm,
                  textAlign: 'left',
                  background: isActive ? tokens.green.glow : 'transparent',
                  border: 'none',
                  color: isActive ? tokens.green[400] : tokens.text.muted,
                  fontFamily: tokens.font.mono,
                  fontSize: 11,
                  fontWeight: isActive ? 600 : 400,
                  cursor: 'pointer',
                  transition: `all 0.15s ${tokens.ease.default}`,
                }}
              >
                {f}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Study Period Info ── */}
      <div
        style={{
          marginTop: 'auto',
          padding: '12px',
          borderRadius: tokens.radius.md,
          background: tokens.bg.base,
          border: `1px solid ${tokens.border.muted}`,
        }}
      >
        <div
          style={{
            fontFamily: tokens.font.mono,
            fontSize: 9,
            color: tokens.text.muted,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            marginBottom: 6,
          }}
        >
          Study Period
        </div>
        <div
          style={{
            fontFamily: tokens.font.heading,
            fontSize: 18,
            fontWeight: 800,
            color: tokens.text.primary,
          }}
        >
          {studyPeriod}{' '}
          <span
            style={{ fontSize: 11, color: tokens.text.muted, fontWeight: 400 }}
          >
            years
          </span>
        </div>
        <div
          style={{
            fontFamily: tokens.font.mono,
            fontSize: 9,
            color: tokens.text.muted,
            marginTop: 4,
          }}
        >
          GIA: {gia.toLocaleString()} m²
        </div>
      </div>
    </div>
  );
}
