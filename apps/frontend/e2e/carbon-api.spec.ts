/**
 * carbon-api.spec.ts — Backend API smoke tests via Playwright request fixture.
 * Tests the FastAPI backend on port 8000.
 */

import { test, expect } from '@playwright/test';

const BACKEND = process.env.BACKEND_URL ?? 'http://localhost:8000/v1';

test.describe('Carbon API Smoke Tests', () => {
  test('GET /v1/health returns status ok', async ({ request }) => {
    let res;
    try {
      res = await request.get(`${BACKEND}/health`);
    } catch {
      test.skip(true, 'Backend not reachable');
      return;
    }
    test.skip(res.status() === 0, 'Backend not reachable');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('status');
    expect(['ok', 'healthy', 'running']).toContain(body.status);
  });

  test('GET /v1/projects returns array or 401', async ({ request }) => {
    let res;
    try {
      res = await request.get(`${BACKEND}/projects`);
    } catch {
      test.skip(true, 'Backend not reachable');
      return;
    }
    expect([200, 401, 403, 422]).toContain(res.status());
    if (res.status() === 200) {
      const body = await res.json();
      expect(Array.isArray(body) || typeof body === 'object').toBe(true);
    }
  });

  test('POST /v1/carbon/calculate rejects invalid payload with 4xx', async ({ request }) => {
    let res;
    try {
      res = await request.post(`${BACKEND}/carbon/calculate`, {
        data: { invalid: true },
        headers: { 'Content-Type': 'application/json' },
      });
    } catch {
      test.skip(true, 'Backend not reachable');
      return;
    }
    expect(res.status()).toBeGreaterThanOrEqual(400);
    expect(res.status()).toBeLessThan(500);
  });

  test('POST /v1/carbon/calculate with mock BOQ payload', async ({ request }) => {
    const mockPayload = {
      project_name: 'E2E Test Project',
      items: [
        { material: 'concrete', quantity: 100, unit: 'm3' },
        { material: 'steel', quantity: 50, unit: 'kg' },
      ],
    };
    let res;
    try {
      res = await request.post(`${BACKEND}/carbon/calculate`, {
        data: mockPayload,
        headers: { 'Content-Type': 'application/json' },
      });
    } catch {
      test.skip(true, 'Backend not reachable');
      return;
    }
    expect(res.status()).not.toBe(500);
    if (res.status() === 200) {
      const body = await res.json();
      expect(body).toHaveProperty('total_carbon');
    }
  });
});
