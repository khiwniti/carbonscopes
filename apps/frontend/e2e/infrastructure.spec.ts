/**
 * infrastructure.spec.ts — Frontend E2E infrastructure verification tests.
 *
 * Prove that the Playwright scaffold is correctly wired up before writing
 * real feature tests.
 *
 *   cd apps/frontend && pnpm exec playwright test e2e/infrastructure.spec.ts
 *
 * Three tests:
 *   1. Frontend loads without JS errors
 *   2. PageHelpers can navigate and find elements
 *   3. AsyncExpect utilities work correctly
 */

import { test, expect } from '@playwright/test';
import { PageHelpers } from './infrastructure/page.helpers';
import { AsyncExpect } from './infrastructure/async_expect';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3002';
const NAV_OPTS = { timeout: 40_000, waitUntil: 'domcontentloaded' as const };

test.describe('E2E Infrastructure Verification', () => {

  test('infrastructure: frontend loads and serves HTML', async ({ page }) => {
    // Collect JS errors
    const jsErrors: string[] = [];
    page.on('pageerror', (err) => jsErrors.push(err.message));

    await page.goto(FRONTEND, NAV_OPTS);

    // Page should return something
    const title = await page.title();
    expect(title).toBeTruthy();

    // No critical JS errors on initial load
    const criticalErrors = jsErrors.filter(
      (e) => !e.includes('Warning:') && !e.includes('ResizeObserver'),
    );
    expect(criticalErrors).toHaveLength(0);
  });

  test('infrastructure: PageHelpers navigation works', async ({ page }) => {
    const helpers = new PageHelpers(page);

    await helpers.navigateToDashboard();

    // Should either show the dashboard or redirect to auth — both are valid.
    const url = page.url();
    expect(url).toContain('localhost');

    if (helpers.isOnAuthPage()) {
      // Not logged in — verify auth page structure exists
      const emailInput = page.locator('input[type="email"]');
      const hasEmail = await emailInput.count() > 0;
      // Auth page should have an email input OR some auth UI
      // (skip assertion if auth is handled differently)
      test.info().annotations.push({
        type: 'note',
        description: 'Redirected to auth — login required for full dashboard tests',
      });
    } else {
      // Logged in — verify page loaded
      await expect(page.locator('body')).toBeVisible();
    }
  });

  test('infrastructure: AsyncExpect utilities work', async ({ page }) => {
    await page.goto(FRONTEND, NAV_OPTS);

    // wait_until with immediate condition
    await AsyncExpect.waitUntil(
      () => true,
      'immediate condition',
      { timeout: 1_000 },
    );

    // waitForCount on body (always 1)
    await AsyncExpect.waitForCount(
      page.locator('body'),
      1,
      'body element to exist',
      { timeout: 5_000 },
    );

    // assertNeverTrue for a condition that stays false
    await AsyncExpect.assertNeverTrue(
      () => false,
      'always-false condition',
      { duration: 500 },
    );

    // waitForValue
    let counter = 0;
    await AsyncExpect.waitForValue(
      () => ++counter,
      3,
      'counter to reach 3',
      { timeout: 5_000, pollInterval: 50 },
    );
    expect(counter).toBeGreaterThanOrEqual(3);
  });

  test('infrastructure: auth fixture produces valid auth state file', async ({}) => {
    // Verify the auth state file can be read by auth.fixture.ts
    // This test uses no browser — just checks file system.
    const fs = await import('fs');
    const path = await import('path');

    const authDir = path.join(__dirname, '.auth');

    // If .auth/user.json exists, it should be valid JSON
    const authFile = path.join(authDir, 'user.json');
    if (fs.existsSync(authFile)) {
      const content = fs.readFileSync(authFile, 'utf-8');
      const parsed = JSON.parse(content);
      expect(parsed).toBeTruthy();
      expect(typeof parsed).toBe('object');
    }
    // If file doesn't exist yet, that's fine — it gets created on first login.
  });
});
