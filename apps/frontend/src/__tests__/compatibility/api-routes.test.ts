/**
 * Frontend ↔ Backend Compatibility Tests
 *
 * Verifies that every API endpoint the frontend calls actually exists on
 * the running backend. Requires BACKEND_URL env variable (default: http://localhost:8000/v1).
 *
 * Run: BACKEND_URL=http://localhost:8000/v1 bun test src/__tests__/compatibility/
 */

import { describe, test, expect, beforeAll } from 'bun:test';

const BACKEND_URL = process.env.BACKEND_URL ?? 'http://localhost:8000/v1';
const TIMEOUT_MS = 5000;

// ─── helpers ─────────────────────────────────────────────────────────────────

async function probe(
  method: string,
  path: string,
): Promise<{ status: number; ok: boolean }> {
  try {
    const res = await fetch(`${BACKEND_URL}${path}`, {
      method,
      signal: AbortSignal.timeout(TIMEOUT_MS),
      headers: { 'Content-Type': 'application/json' },
    });
    return { status: res.status, ok: true };
  } catch (e: unknown) {
    const name = (e as Error)?.name;
    if (name === 'AbortError' || name === 'TimeoutError') return { status: 0, ok: false };
    return { status: -1, ok: false };
  }
}

/**
 * Endpoint is "reachable" if backend responds (any HTTP status).
 * 401/403/404 mean the route exists but requires auth or valid params.
 * 0  = connection timeout (route unreachable)
 * -1 = backend down
 */
function isReachable(status: number) {
  return status > 0;
}

// ─── backend availability check ──────────────────────────────────────────────

let backendAvailable = false;

beforeAll(async () => {
  const { status } = await probe('GET', '/health');
  backendAvailable = status > 0;
  if (!backendAvailable) {
    console.warn(`⚠️  Backend not reachable at ${BACKEND_URL} — skipping live tests`);
  }
});

// ─── health ──────────────────────────────────────────────────────────────────

describe('Backend health', () => {
  test('GET /health responds', async () => {
    const { status } = await probe('GET', '/health');
    expect(status).toBeGreaterThan(0);
  });

  test('GET /health returns JSON with status field', async () => {
    const res = await fetch(`${BACKEND_URL}/health`).catch(() => null);
    if (!res) return; // backend down — skip
    const body = await res.json();
    expect(body).toHaveProperty('status');
    expect(['healthy', 'degraded', 'shutting_down']).toContain(body.status);
  });
});

// ─── core routes the frontend uses (unauthenticated probe) ───────────────────

describe('Core API routes exist', () => {
  const routes: [string, string][] = [
    ['GET',  '/accounts'],
    ['GET',  '/threads'],
    ['GET',  '/tools'],
    ['GET',  '/api-keys'],
    ['GET',  '/billing/account-state'],
    ['GET',  '/memory/settings'],
    ['GET',  '/notifications/settings'],
    ['GET',  '/referrals/stats'],
    ['GET',  '/triggers/all'],
    ['GET',  '/user-roles'],
  ];

  for (const [method, path] of routes) {
    test(`${method} ${path} → reachable (401/403 expected without auth)`, async () => {
      if (!backendAvailable) return; // skip if backend down
      const { status } = await probe(method, path);
      expect(isReachable(status)).toBe(true);
      // Without auth, expect 401 or 403 — NOT 404 (route doesn't exist)
      expect(status).not.toBe(404);
    });
  }
});

// ─── admin routes ─────────────────────────────────────────────────────────────

describe('Admin routes exist', () => {
  const adminRoutes: [string, string][] = [
    ['GET', '/admin/system-status'],
    ['GET', '/admin/analytics/summary'],
    ['GET', '/admin/sandbox-pool/stats'],
    ['GET', '/admin/stateless/health'],
  ];

  for (const [method, path] of adminRoutes) {
    test(`${method} ${path} → reachable`, async () => {
      if (!backendAvailable) return;
      const { status } = await probe(method, path);
      expect(isReachable(status)).toBe(true);
      expect(status).not.toBe(404);
    });
  }
});

// ─── agent routes ─────────────────────────────────────────────────────────────

describe('Agent routes exist', () => {
  const agentRoutes: [string, string][] = [
    ['POST', '/agents/json/analyze'],
    ['GET',  '/agents/json/analyze'],
  ];

  for (const [method, path] of agentRoutes) {
    test(`${method} ${path} → reachable`, async () => {
      if (!backendAvailable) return;
      const { status } = await probe(method, path);
      expect(isReachable(status)).toBe(true);
      expect(status).not.toBe(404);
    });
  }
});
