import React from 'react';
import { tokens } from '../../tokens';

export interface SectionTitleProps {
  /** Small mono uppercase tag (e.g., "Design Tokens", "Components") */
  tag: string;
  /** Main section heading */
  title: string;
  /** Optional supporting description */
  desc?: string;
}

/**
 * Section title component for design system section headers.
 * Uses Instrument Serif for the heading and IBM Plex Mono for the tag.
 */
export function SectionTitle({ tag, title, desc }: SectionTitleProps) {
  return (
    <div style={{ marginBottom: 32 }}>
      <div
        style={{
          fontFamily: tokens.font.mono,
          fontSize: 10,
          fontWeight: 600,
          color: tokens.green[500],
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          marginBottom: 8,
        }}
      >
        {tag}
      </div>
      <h2
        style={{
          fontFamily: tokens.font.display,
          fontSize: 32,
          fontWeight: 400,
          color: tokens.text.primary,
          lineHeight: 1.15,
          letterSpacing: '-0.01em',
        }}
      >
        {title}
      </h2>
      {desc && (
        <p
          style={{
            fontFamily: tokens.font.body,
            fontSize: 14,
            color: tokens.text.muted,
            marginTop: 8,
            maxWidth: 600,
            lineHeight: 1.6,
          }}
        >
          {desc}
        </p>
      )}
    </div>
  );
}
