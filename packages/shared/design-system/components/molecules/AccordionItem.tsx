import React from 'react';
import { useState } from 'react';
import { tokens } from '../../tokens';

export interface AccordionItemProps {
  /** Accordion title */
  title: string;
  /** Accordion content */
  children: React.ReactNode;
  /** Default open state */
  defaultOpen?: boolean;
  /** Optional badge element */
  badge?: React.ReactNode;
}

/**
 * Accordion item component for collapsible content sections
 */
export function AccordionItem({ title, children, defaultOpen = false, badge }: AccordionItemProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div style={{ borderBottom: `1px solid ${tokens.border.muted}` }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: '100%',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: '14px 0',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span
            style={{
              fontFamily: tokens.font.heading,
              fontSize: 13,
              fontWeight: 600,
              color: tokens.text.primary,
            }}
          >
            {title}
          </span>
          {badge}
        </div>
        <span
          style={{
            color: tokens.green[400],
            fontSize: 14,
            transform: open ? 'rotate(45deg)' : 'rotate(0)',
            transition: 'transform 0.2s ease',
          }}
        >
          +
        </span>
      </button>
      <div
        style={{
          maxHeight: open ? 400 : 0,
          overflow: 'hidden',
          transition: 'all 0.3s ease',
          opacity: open ? 1 : 0,
        }}
      >
        <div
          style={{
            padding: '0 0 14px',
            fontFamily: tokens.font.body,
            fontSize: 13,
            lineHeight: 1.6,
            color: tokens.text.secondary,
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
}
