import React, { useState } from 'react';
import { tokens } from '../../tokens';

export interface InputProps {
  /** Input label */
  label?: string;
  /** Placeholder text */
  placeholder?: string;
  /** Suffix text (e.g., unit) */
  suffix?: string;
  /** Input type */
  type?: string;
  /** Use monospace font */
  mono?: boolean;
  /** Value */
  value?: string;
  /** Change handler */
  onChange?: (value: string) => void;
  /** Error state */
  error?: boolean;
  /** Error message */
  errorMessage?: string;
  /** Disabled state */
  disabled?: boolean;
  /** Read-only state */
  readOnly?: boolean;
}

/**
 * Input field component with label and suffix support
 */
export function Input({
  label,
  placeholder,
  suffix,
  type = 'text',
  mono,
  value: controlledValue,
  onChange,
  error,
  errorMessage,
  disabled,
  readOnly,
}: InputProps) {
  const [focused, setFocused] = useState(false);
  const [internalValue, setInternalValue] = useState('');

  const value = controlledValue !== undefined ? controlledValue : internalValue;
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    if (onChange) {
      onChange(newValue);
    } else {
      setInternalValue(newValue);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
      {label && (
        <label
          style={{
            fontFamily: tokens.font.body,
            fontSize: 11,
            fontWeight: 600,
            color: tokens.text.muted,
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
          }}
        >
          {label}
        </label>
      )}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          background: disabled ? tokens.bg.hover : tokens.bg.input,
          borderRadius: tokens.radius.md,
          border: `1.5px solid ${
            error
              ? tokens.status.danger
              : focused
              ? tokens.border.active
              : tokens.border.default
          }`,
          boxShadow: focused && !error ? `0 0 0 3px ${tokens.border.focus}` : 'none',
          transition: `all 0.2s ${tokens.ease.default}`,
          opacity: disabled ? 0.6 : 1,
          cursor: disabled ? 'not-allowed' : 'default',
        }}
      >
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={handleChange}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          disabled={disabled}
          readOnly={readOnly}
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            padding: '10px 14px',
            color: tokens.text.primary,
            fontFamily: mono ? tokens.font.mono : tokens.font.body,
            fontSize: 13,
            cursor: disabled ? 'not-allowed' : readOnly ? 'default' : 'text',
          }}
        />
        {suffix && (
          <span
            style={{
              padding: '0 12px 0 0',
              fontFamily: tokens.font.mono,
              fontSize: 11,
              color: tokens.text.muted,
            }}
          >
            {suffix}
          </span>
        )}
      </div>
      {error && errorMessage && (
        <span
          style={{
            fontFamily: tokens.font.body,
            fontSize: 11,
            color: tokens.status.danger,
            marginTop: 4,
          }}
        >
          {errorMessage}
        </span>
      )}
    </div>
  );
}
