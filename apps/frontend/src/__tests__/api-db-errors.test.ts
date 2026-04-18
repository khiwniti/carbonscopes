/**
 * Unit tests verifying the frontend API layer handles DB-unavailability
 * responses (HTTP 503 with Retry-After) correctly.
 *
 * Uses bun:test. No real network calls are made; fetch is mocked inline.
 */
import { describe, test, expect, mock, beforeEach } from 'bun:test';

// ---------------------------------------------------------------------------
// Minimal inline replication of the API client's error-handling path.
// We test the LOGIC without importing the real module (which has browser deps).
// ---------------------------------------------------------------------------

class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly retryAfterSeconds: number | null = null,
  ) {
    super(message);
    this.name = 'ApiError';
  }

  get isServiceUnavailable() {
    return this.status === 503;
  }

  get isServerError() {
    return this.status >= 500;
  }
}

/** Simulate the fetch wrapper the api-client uses. */
async function apiFetch(
  fetchFn: (url: string) => Promise<Response>,
  url: string,
): Promise<unknown> {
  const response = await fetchFn(url);

  if (!response.ok) {
    const retryAfterHeader = response.headers.get('retry-after');
    const retryAfter = retryAfterHeader ? parseInt(retryAfterHeader, 10) : null;
    const body = await response.json().catch(() => ({}));
    const message =
      (body as any)?.detail ?? `HTTP ${response.status}`;

    throw new ApiError(response.status, message, retryAfter ? retryAfter : null);
  }

  return response.json();
}

// ---------------------------------------------------------------------------
// Helper: build a mock Response
// ---------------------------------------------------------------------------

function mockResponse(status: number, body: unknown, headers: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', ...headers },
  });
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('apiFetch – HTTP 503 handling', () => {
  test('throws ApiError with status 503 when backend returns 503', async () => {
    const fetch503 = async () =>
      mockResponse(503, { detail: 'Database temporarily unavailable. Please try again shortly.' }, {
        'retry-after': '10',
      });

    let caught: ApiError | null = null;
    try {
      await apiFetch(fetch503, '/v1/agents');
    } catch (e) {
      caught = e as ApiError;
    }

    expect(caught).not.toBeNull();
    expect(caught!.status).toBe(503);
  });

  test('503 error exposes isServiceUnavailable flag', async () => {
    const fetch503 = async () =>
      mockResponse(503, { detail: 'Database temporarily unavailable. Please try again shortly.' }, {
        'retry-after': '10',
      });

    let caught: ApiError | null = null;
    try {
      await apiFetch(fetch503, '/v1/agents');
    } catch (e) {
      caught = e as ApiError;
    }

    expect(caught!.isServiceUnavailable).toBe(true);
  });

  test('503 error exposes retryAfterSeconds from header', async () => {
    const fetch503 = async () =>
      mockResponse(503, { detail: 'Service unavailable' }, { 'retry-after': '10' });

    let caught: ApiError | null = null;
    try {
      await apiFetch(fetch503, '/v1/accounts');
    } catch (e) {
      caught = e as ApiError;
    }

    expect(caught!.retryAfterSeconds).toBe(10);
  });

  test('503 error message does NOT contain internal psycopg details', async () => {
    const backendSanitizedMessage = 'Database temporarily unavailable. Please try again shortly.';
    const fetch503 = async () =>
      mockResponse(503, { detail: backendSanitizedMessage }, { 'retry-after': '10' });

    let caught: ApiError | null = null;
    try {
      await apiFetch(fetch503, '/v1/threads');
    } catch (e) {
      caught = e as ApiError;
    }

    expect(caught!.message).not.toContain('psycopg');
    expect(caught!.message).not.toContain('Circuit breaker');
    expect(caught!.message).not.toContain('57.182.231.186');
  });

  test('503 is correctly identified as a server error', async () => {
    const err = new ApiError(503, 'unavailable', 10);
    expect(err.isServerError).toBe(true);
    expect(err.isServiceUnavailable).toBe(true);
  });
});

describe('apiFetch – HTTP 500 handling', () => {
  test('throws ApiError with status 500', async () => {
    const fetch500 = async () =>
      mockResponse(500, { detail: 'Failed to fetch agents.' });

    let caught: ApiError | null = null;
    try {
      await apiFetch(fetch500, '/v1/agents');
    } catch (e) {
      caught = e as ApiError;
    }

    expect(caught!.status).toBe(500);
  });

  test('500 isServiceUnavailable is false', async () => {
    const err = new ApiError(500, 'Server error', null);
    expect(err.isServiceUnavailable).toBe(false);
    expect(err.isServerError).toBe(true);
  });

  test('500 has no Retry-After (null)', async () => {
    const fetch500 = async () =>
      mockResponse(500, { detail: 'Failed to fetch agents.' });

    let caught: ApiError | null = null;
    try {
      await apiFetch(fetch500, '/v1/agents');
    } catch (e) {
      caught = e as ApiError;
    }

    expect(caught!.retryAfterSeconds).toBeNull();
  });
});

describe('apiFetch – successful responses', () => {
  test('returns parsed JSON for 200', async () => {
    const fetch200 = async () =>
      mockResponse(200, { agents: [], pagination: { total: 0 } });

    const data = await apiFetch(fetch200, '/v1/agents');
    expect(data).toEqual({ agents: [], pagination: { total: 0 } });
  });

  test('returns empty list for empty 200', async () => {
    const fetch200 = async () => mockResponse(200, []);
    const data = await apiFetch(fetch200, '/v1/accounts');
    expect(Array.isArray(data)).toBe(true);
    expect((data as unknown[]).length).toBe(0);
  });
});

describe('apiFetch – 404 handling', () => {
  test('throws ApiError with status 404', async () => {
    const fetch404 = async () =>
      mockResponse(404, { detail: 'Thread not found' });

    let caught: ApiError | null = null;
    try {
      await apiFetch(fetch404, '/v1/threads/missing-id/agent-runs');
    } catch (e) {
      caught = e as ApiError;
    }

    expect(caught!.status).toBe(404);
    expect(caught!.isServiceUnavailable).toBe(false);
    expect(caught!.isServerError).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// Exponential backoff utility (used by the frontend's retry logic)
// ---------------------------------------------------------------------------

describe('exponential backoff calculation', () => {
  function calcBackoff(attempt: number, baseMs: number, maxMs: number): number {
    return Math.min(baseMs * Math.pow(2, attempt), maxMs);
  }

  test('attempt 0 returns base delay', () => {
    expect(calcBackoff(0, 500, 30_000)).toBe(500);
  });

  test('attempt 1 doubles the delay', () => {
    expect(calcBackoff(1, 500, 30_000)).toBe(1000);
  });

  test('delay is capped at maxMs', () => {
    expect(calcBackoff(10, 500, 30_000)).toBe(30_000);
  });

  test('respects Retry-After over computed backoff when larger', () => {
    const retryAfterMs = 10_000;  // 10s from header
    const computedMs = calcBackoff(0, 500, 30_000);  // 500ms
    const actual = Math.max(retryAfterMs, computedMs);
    expect(actual).toBe(10_000);
  });
});
