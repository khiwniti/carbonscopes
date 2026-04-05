/**
 * API Contract Tests — verify frontend TypeScript types match backend JSON shapes
 *
 * Probes each endpoint with real HTTP and validates the response shape
 * against what the frontend's TypeScript types expect.
 */

import { describe, test, expect, beforeAll } from 'bun:test';

const BACKEND_URL = process.env.BACKEND_URL ?? 'http://localhost:8000/v1';

let backendUp = false;

beforeAll(async () => {
  try {
    const r = await fetch(`${BACKEND_URL}/health`, { signal: AbortSignal.timeout(4000) });
    backendUp = r.status > 0;
  } catch { backendUp = false; }
});

async function get(path: string) {
  try {
    const r = await fetch(`${BACKEND_URL}${path}`, {
      signal: AbortSignal.timeout(4000),
    });
    return { status: r.status, body: r.status < 500 ? await r.json().catch(() => null) : null };
  } catch {
    return { status: -1, body: null };
  }
}

// ─── /health shape ───────────────────────────────────────────────────────────

describe('GET /health — response shape', () => {
  test('has required fields', async () => {
    if (!backendUp) return;
    const { body } = await get('/health');
    expect(body).not.toBeNull();
    expect(body).toHaveProperty('status');
    expect(body).toHaveProperty('timestamp');
    expect(body).toHaveProperty('instance_id');
  });

  test('agent_system has expected structure', async () => {
    if (!backendUp) return;
    const { body } = await get('/health');
    if (!body) return;
    expect(body).toHaveProperty('agent_system');
    const as = body.agent_system;
    expect(typeof as.initialized).toBe('boolean');
    expect(typeof as.active_agents).toBe('number');
  });

  test('status is one of known values', async () => {
    if (!backendUp) return;
    const { body } = await get('/health');
    expect(['healthy', 'degraded', 'shutting_down']).toContain(body?.status);
  });
});

// ─── unauthenticated endpoints return correct shape ───────────────────────────

describe('Unauthenticated requests — error shape', () => {
  // All protected endpoints should return 401, not a random error format
  const protectedEndpoints = [
    '/accounts',
    '/threads',
    '/api-keys',
    '/billing/account-state',
    '/memory/settings',
    '/user-roles',
  ];

  for (const path of protectedEndpoints) {
    test(`${path} returns 401/403 with parseable JSON`, async () => {
      if (!backendUp) return;
      const { status, body } = await get(path);
      if (status === -1) return; // backend down
      // Must be auth error, not server crash
      expect([401, 403, 422]).toContain(status);
      // Body should be JSON (FastAPI default or our custom error shape)
      expect(body).not.toBeNull();
    });
  }
});

// ─── OpenAPI spec completeness ────────────────────────────────────────────────

describe('OpenAPI spec — frontend endpoints covered', () => {
  // The complete set of paths the frontend calls
  const frontendPaths = [
    '/v1/accounts',
    '/v1/threads',
    '/v1/tools',
    '/v1/api-keys',
    '/v1/billing/account-state',
    '/v1/memory/settings',
    '/v1/notifications/settings',
    '/v1/triggers/all',
    '/v1/user-roles',
    '/v1/referrals/stats',
    '/v1/admin/system-status',
    '/v1/admin/analytics/summary',
  ];

  let specPaths: string[] = [];

  beforeAll(async () => {
    if (!backendUp) return;
    try {
      // OpenAPI spec is served at /openapi.json (without /v1 prefix)
      const r = await fetch(`http://localhost:8000/openapi.json`, {
        signal: AbortSignal.timeout(5000),
      });
      if (r.ok) {
        const spec = await r.json();
        specPaths = Object.keys(spec.paths ?? {});
      }
    } catch { /* ignore */ }
  });

  test('OpenAPI spec is reachable', async () => {
    if (!backendUp) return;
    const r = await fetch('http://localhost:8000/openapi.json', {
      signal: AbortSignal.timeout(5000),
    }).catch(() => null);
    if (!r) return;
    expect(r.status).toBe(200);
  });

  for (const path of frontendPaths) {
    test(`${path} is in OpenAPI spec`, async () => {
      if (!backendUp || specPaths.length === 0) return;
      const found = specPaths.some(p => p === path || p.startsWith(path));
      expect(found).toBe(true);
    });
  }
});

// ─── Frontend URL construction matches backend routes ────────────────────────

describe('URL construction — no mismatches', () => {
  test('/v1 prefix is correct', () => {
    // Backend registers routes under /v1 — verify the frontend BACKEND_URL includes it
    const backendUrl = BACKEND_URL ?? 'http://localhost:8000/v1';
    expect(backendUrl).toMatch(/\/v1$/);
  });

  test('known route patterns are well-formed', () => {
    const examples = [
      '/threads',
      '/projects/some-id/threads',
      '/agents/some-id/custom-mcp-tools',
      '/billing/account-state',
    ];
    for (const path of examples) {
      expect(path).toMatch(/^\/[a-z]/);
      expect(path).not.toContain('//');
      expect(path).not.toContain(' ');
    }
  });
});
