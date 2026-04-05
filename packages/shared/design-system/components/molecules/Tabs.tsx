import React from 'react';
import { useState } from 'react';
import { tokens } from '../../tokens';

export interface TabItem {
  /** Tab label */
  label: string;
  /** Tab content */
  content: React.ReactNode;
}

export interface TabsProps {
  /** Array of tab items */
  items: TabItem[];
  /** Default active tab index */
  defaultActive?: number;
}

/**
 * Tabs component for content organization
 */
export function Tabs({ items, defaultActive = 0 }: TabsProps) {
  const [active, setActive] = useState(defaultActive);

  return (
    <div>
      <div
        style={{
          display: 'flex',
          gap: 2,
          background: tokens.bg.base,
          borderRadius: tokens.radius.md,
          padding: 3,
          border: `1px solid ${tokens.border.default}`,
        }}
      >
        {items.map((item, i) => (
          <button
            key={i}
            onClick={() => setActive(i)}
            style={{
              flex: 1,
              padding: '8px 16px',
              borderRadius: tokens.radius.sm,
              background: active === i ? tokens.bg.elevated : 'transparent',
              border: 'none',
              cursor: 'pointer',
              fontFamily: tokens.font.body,
              fontSize: 12,
              fontWeight: active === i ? 700 : 500,
              color: active === i ? tokens.green[400] : tokens.text.muted,
              transition: `all 0.2s ${tokens.ease.default}`,
              boxShadow: active === i ? tokens.shadow.sm : 'none',
            }}
          >
            {item.label}
          </button>
        ))}
      </div>
      <div style={{ marginTop: 16, animation: 'cs-fadeIn 0.3s ease' }}>{items[active]?.content}</div>
    </div>
  );
}
