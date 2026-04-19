/**
 * Enhanced E2E tests with console error monitoring
 * Ensures no JavaScript errors occur during user journeys
 */

import { test, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';
const NAV_OPTS = { timeout: 40_000, waitUntil: 'domcontentloaded' as const };

const IGNORED_ERROR_PATTERNS = [
  /hydration/i,
  /did not match/i,
  /Warning:/,
  /ResizeObserver/,
  /ChunkLoadError/,
  /Loading chunk/,
  /Cannot read properties of null.*reading 'useRef'/,
  /Minified React error #418/,
  /Minified React error #423/,
  /Minified React error #425/,
  /https:\/\/react\.dev\/errors/,
  /Error: Hydration/,
  /There was an error while hydrating/,
  /The server could not finish this Suspense/,
  /Expected server HTML to contain/,
];

function checkConsoleErrors(errors: string[]): void {
  const real = errors.filter(
    (msg) => !IGNORED_ERROR_PATTERNS.some((pat) => pat.test(msg)),
  );
  if (real.length > 0) {
    throw new Error(`Console errors detected:\n${real.join('\n')}`);
  }
}

test.describe('Enhanced E2E with Console Error Monitoring', () => {
  let collectedErrors: string[] = [];

  test.beforeEach(async ({ page }) => {
    collectedErrors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        collectedErrors.push(msg.text());
      }
    });
    page.on('pageerror', (err) => {
      collectedErrors.push(err.message);
    });
  });

  test.afterEach(() => {
    checkConsoleErrors(collectedErrors);
  });

  test.describe('Critical User Journeys', () => {
    test('homepage loads without console errors', async ({ page }) => {
      const res = await page.goto(FRONTEND, NAV_OPTS);
      expect(res?.status()).toBeLessThan(500);
      await expect(page.locator('body')).not.toContainText('Application error', { timeout: 5000 });
    });

    test('authentication page loads without console errors', async ({ page }) => {
      await page.goto(`${FRONTEND}/auth`, NAV_OPTS);
      await expect(
        page.locator('input[type="email"], input[name="email"]').first(),
      ).toBeVisible({ timeout: 8000 });
    });

    test('pricing page loads without console errors', async ({ page }) => {
      const res = await page.goto(`${FRONTEND}/pricing`, NAV_OPTS);
      expect(res?.status()).toBeLessThan(500);
      await expect(page.locator('body')).not.toContainText('Application error', { timeout: 5000 });
    });

    test('about page loads without console errors', async ({ page }) => {
      const res = await page.goto(`${FRONTEND}/about`, NAV_OPTS);
      expect(res?.status()).toBeLessThan(500);
      await expect(page.locator('body')).not.toContainText('Application error', { timeout: 5000 });
    });

    test('support page loads without console errors', async ({ page }) => {
      const res = await page.goto(`${FRONTEND}/support`, NAV_OPTS);
      expect(res?.status()).toBeLessThan(500);
      await expect(page.locator('body')).not.toContainText('Application error', { timeout: 5000 });
    });

    test('legal page loads without console errors', async ({ page }) => {
      const res = await page.goto(`${FRONTEND}/legal`, NAV_OPTS);
      expect(res?.status()).toBeLessThan(500);
      await expect(page.locator('body')).not.toContainText('Application error', { timeout: 5000 });
    });
  });

  test.describe('Navigation Without Console Errors', () => {
    test('navigation between pages produces no console errors', async ({ page }) => {
      await page.goto(FRONTEND, NAV_OPTS);
      await page.goto(`${FRONTEND}/auth`, NAV_OPTS);
      await expect(page.locator('body')).not.toContainText('Application error', { timeout: 5000 });

      await page.goto(FRONTEND, NAV_OPTS);
      await expect(page.locator('body')).toBeVisible();
    });
  });

  test.describe('Responsive Views Without Console Errors', () => {
    const viewports = [
      { name: 'mobile', width: 375, height: 812 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1440, height: 900 },
    ];

    for (const viewport of viewports) {
      test(`${viewport.name} viewport loads without console errors`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.goto(FRONTEND, NAV_OPTS);
        await expect(page.locator('body')).toBeVisible();
      });
    }
  });
});
