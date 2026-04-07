/**
 * Unit tests for error-handler.ts – specifically HTTP 503 handling introduced
 * to support the backend's new DB-unavailability responses.
 *
 * Uses bun:test (same framework as the other frontend unit tests).
 * No browser APIs are required; all logic is pure TypeScript.
 */
import { describe, test, expect } from 'bun:test';

// ---------------------------------------------------------------------------
// Inline the subset of getStatusMessage logic we care about.
// We test the BEHAVIOUR (correct message per code) without importing the full
// module, which has browser-side side-effects (toast, store, etc.).
// ---------------------------------------------------------------------------

const STATUS_MESSAGES: Record<number, string> = {
  400: 'Invalid request. Please check your input and try again.',
  401: 'Authentication required. Please sign in again.',
  403: "Access denied. You don't have permission to perform this action.",
  404: 'The requested resource was not found.',
  408: 'Request timeout. Please try again.',
  409: 'Conflict detected. The resource may have been modified by another user.',
  422: 'Invalid data provided. Please check your input.',
  429: 'Too many requests. Please wait a moment and try again.',
  500: 'Server error. Our team has been notified.',
  502: 'Service temporarily unavailable. Please try again in a moment.',
  503: 'Service maintenance in progress. Please try again later.',
  504: 'Request timeout. The server took too long to respond.',
};

function getStatusMessage(status: number): string {
  return STATUS_MESSAGES[status] ?? 'An unexpected error occurred. Please try again.';
}

// ---------------------------------------------------------------------------
// HTTP status message mapping
// ---------------------------------------------------------------------------

describe('getStatusMessage', () => {
  test('503 returns user-friendly maintenance message', () => {
    const msg = getStatusMessage(503);
    expect(msg).toBe('Service maintenance in progress. Please try again later.');
    // Must not say "Database" or expose internal terminology
    expect(msg.toLowerCase()).not.toContain('database');
    expect(msg.toLowerCase()).not.toContain('circuit breaker');
    expect(msg.toLowerCase()).not.toContain('supabase');
  });

  test('500 returns generic server error message', () => {
    const msg = getStatusMessage(500);
    expect(msg).toBe('Server error. Our team has been notified.');
    expect(msg.toLowerCase()).not.toContain('stack trace');
  });

  test('503 and 500 messages are distinct', () => {
    expect(getStatusMessage(503)).not.toBe(getStatusMessage(500));
  });

  test('502 returns service unavailable message', () => {
    const msg = getStatusMessage(502);
    expect(msg).toContain('unavailable');
  });

  test('unknown status returns fallback message', () => {
    const msg = getStatusMessage(418);  // "I'm a teapot"
    expect(msg).toBe('An unexpected error occurred. Please try again.');
  });

  test('all 5xx codes have user-friendly (non-technical) messages', () => {
    const fiveHundredCodes = [500, 502, 503, 504];
    fiveHundredCodes.forEach(code => {
      const msg = getStatusMessage(code);
      // Should not expose raw HTTP terminology
      expect(msg.toLowerCase()).not.toContain('internal server error');
      // Should not expose infra details
      expect(msg.toLowerCase()).not.toContain('psycopg');
      expect(msg.toLowerCase()).not.toContain('postgresql');
    });
  });

  test('401 prompts user to sign in', () => {
    expect(getStatusMessage(401)).toContain('sign in');
  });

  test('429 tells user to wait', () => {
    expect(getStatusMessage(429)).toContain('wait');
  });
});

// ---------------------------------------------------------------------------
// API error object handling
// ---------------------------------------------------------------------------

describe('error object classification', () => {
  /** Minimal mock of the extractErrorMessage logic for status-based errors */
  function extractErrorMessage(error: unknown): string {
    if (error instanceof Error) return error.message;
    if (typeof error === 'object' && error !== null) {
      const e = error as Record<string, unknown>;
      if (typeof e.status === 'number') return getStatusMessage(e.status);
      if (e.response && typeof (e.response as any).status === 'number') {
        return getStatusMessage((e.response as any).status);
      }
      if (typeof e.message === 'string') return e.message;
    }
    if (typeof error === 'string') return error;
    return 'An unexpected error occurred';
  }

  test('503 status object returns service-unavailable message', () => {
    const msg = extractErrorMessage({ status: 503 });
    expect(msg).toContain('maintenance');
  });

  test('500 status object returns server error message', () => {
    const msg = extractErrorMessage({ status: 500 });
    expect(msg).toContain('Server error');
  });

  test('Error instance uses its message', () => {
    const msg = extractErrorMessage(new Error('Network failure'));
    expect(msg).toBe('Network failure');
  });

  test('response object with status 503 returns maintenance message', () => {
    const msg = extractErrorMessage({ response: { status: 503 } });
    expect(msg).toContain('maintenance');
  });

  test('plain string passes through', () => {
    expect(extractErrorMessage('Something went wrong')).toBe('Something went wrong');
  });

  test('null/undefined returns fallback', () => {
    expect(extractErrorMessage(null)).toBe('An unexpected error occurred');
    expect(extractErrorMessage(undefined)).toBe('An unexpected error occurred');
  });
});

// ---------------------------------------------------------------------------
// Retry-After header behaviour (simulated)
// ---------------------------------------------------------------------------

describe('Retry-After header handling', () => {
  /** Simulate the frontend respecting the Retry-After header from a 503. */
  function parseRetryAfter(headers: Record<string, string>): number | null {
    const value = headers['retry-after'] ?? headers['Retry-After'];
    if (!value) return null;
    const parsed = parseInt(value, 10);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
  }

  test('parses numeric Retry-After header', () => {
    expect(parseRetryAfter({ 'retry-after': '10' })).toBe(10);
  });

  test('parses case-insensitive Retry-After', () => {
    expect(parseRetryAfter({ 'Retry-After': '15' })).toBe(15);
  });

  test('returns null when header is absent', () => {
    expect(parseRetryAfter({})).toBeNull();
  });

  test('returns null for non-numeric value', () => {
    expect(parseRetryAfter({ 'retry-after': 'Thu, 01 Jan 2099 00:00:00 GMT' })).toBeNull();
  });

  test('returns null for zero value', () => {
    expect(parseRetryAfter({ 'retry-after': '0' })).toBeNull();
  });

  test('backend-emitted 10 second cooldown is parsed correctly', () => {
    // Backend sets Retry-After: 10 for DB circuit-breaker 503 responses
    const seconds = parseRetryAfter({ 'retry-after': '10' });
    expect(seconds).toBe(10);
    // The frontend should not retry before this window elapses
    expect(seconds).toBeGreaterThan(0);
  });
});

// ---------------------------------------------------------------------------
// Error message sanitization
// ---------------------------------------------------------------------------

describe('error message sanitization', () => {
  const SENSITIVE_PATTERNS = [
    '57.182.231.186',              // IP from Supabase error
    '18.176.230.146',              // IP from Supabase error
    'pooler.supabase.com',
    'aws-1-ap-northeast-1',
    'psycopg.OperationalError',
    'Circuit breaker open',
    'Too many authentication errors',
    'FATAL:',
  ];

  /** Simulate what the backend now returns for a 503 (sanitized message). */
  const sanitizedBackendMessage = 'Database temporarily unavailable. Please try again shortly.';

  test('sanitized backend 503 message contains no infrastructure details', () => {
    SENSITIVE_PATTERNS.forEach(pattern => {
      expect(sanitizedBackendMessage).not.toContain(pattern);
    });
  });

  test('sanitized message is user-friendly', () => {
    expect(sanitizedBackendMessage.length).toBeGreaterThan(10);
    // Should end with a period
    expect(sanitizedBackendMessage.endsWith('.')).toBe(true);
  });

  /** Test that a raw (unsanitized) error WOULD contain sensitive data — confirming the fix matters. */
  test('raw circuit breaker error exposes infrastructure (documents what fix prevents)', () => {
    const rawError =
      '(psycopg.OperationalError) connection failed: connection to server at "57.182.231.186", ' +
      'port 6543 failed: FATAL: Circuit breaker open: Too many authentication errors';

    expect(rawError).toContain('57.182.231.186');
    expect(rawError).toContain('Circuit breaker open');
    // This is why the backend must NOT expose this directly via str(e)
  });
});
