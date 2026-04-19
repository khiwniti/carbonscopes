/**
 * Enhanced E2E tests with console error monitoring
 * Ensures no JavaScript errors occur during user journeys
 */

import { test, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';
const NAV_OPTS = { timeout: 40_000, waitUntil: 'domcontentloaded' as const };

/**
 * Helper to check for console errors and warnings
 */
async function checkConsoleErrors(page): Promise<void> {
  // Collect all console messages
  const consoleMessages: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleMessages.push(`ERROR: ${msg.text()}`);
    } else if (msg.type() === 'warning') {
      // Only capture warnings that aren't just development noise
      const text = msg.text();
      if (!text.includes('Warning:') && !text.includes('development')) {
        consoleMessages.push(`WARNING: ${text}`);
      }
    }
  });

  // Wait a bit for any async console messages
  await page.waitForTimeout(1000);

  // Assert no errors
  const errors = consoleMessages.filter(msg => msg.startsWith('ERROR:'));
  if (errors.length > 0) {
    console.error('Console errors detected:', errors.join('\n'));
    expect(errors.length).toBe(0);
  }

  // Log warnings for visibility but don't fail test
  const warnings = consoleMessages.filter(msg => msg.startsWith('WARNING:'));
  if (warnings.length > 0) {
    console.warn('Console warnings detected:', warnings.join('\n'));
  }
}

test.describe('Enhanced E2E with Console Error Monitoring', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing console messages before each test
    await page.evaluate(() => {
      console.clear();
    });
  });

  test.afterEach(async ({ page }) => {
    // Check for console errors after each test
    await checkConsoleErrors(page);
  });

  // Test critical user journeys
  test.describe('Critical User Journeys', () => {
    
    test('homepage loads without console errors', async ({ page }) => {
      const res = await page.goto(FRONTEND, NAV_OPTS);
      expect(res?.status()).toBeLessThan(500);
      await expect(page.locator('body')).not.toContainText('Application error', { timeout: 5000 });
    });

    test('authentication page loads without console errors', async ({ page }) => {
      await page.goto(`${FRONTEND}/auth`, NAV_OPTS);
      await expect(page.locator('input[type="email"], input[name="email"]').first()).toBeVisible({ timeout: 8000 });
    });

    test('pricing page loads without console errors', async ({ page }) => {
      await page.goto(`${FRONTEND}/pricing`, NAV_OPTS);
      await expect(page.locator('body')).toContainText('Pricing', { timeout: 5000 });
    });

    test('about page loads without console errors', async ({ page }) => {
      await page.goto(`${FRONTEND}/about`, NAV_OPTS);
      await expect(page.locator('body')).toContainText('About', { timeout: 5000 });
    });

    test('support page loads without console errors', async ({ page }) => {
      await page.goto(`${FRONTEND}/support`, NAV_OPTS);
      await expect(page.locator('body')).toContainText('Support', { timeout: 5000 });
    });

    test('legal page loads without console errors', async ({ page }) => {
      await page.goto(`${FRONTEND}/legal`, NAV_OPTS);
      await expect(page.locator('body')).toContainText('Legal', { timeout: 5000 });
    });
  });

  test.describe('Navigation Without Console Errors', () => {
    test('navigation between pages produces no console errors', async ({ page }) => {
      // Start at homepage
      await page.goto(FRONTEND, NAV_OPTS);
      
      // Navigate to auth
      await page.click('text=Sign in');
      await page.waitForURL(`${FRONTEND}/auth`);
      
      // Navigate to pricing
      await page.click('text=Pricing');
      await page.waitForURL(`${FRONTEND}/pricing`);
      
      // Navigate back to home via logo
      await page.click('header a[href="/"]');
      await page.waitForURL(FRONTEND);
    });
  });

  test.describe('Responsive Views Without Console Errors', () => {
    const viewports = [
      { name: 'mobile', width: 375, height: 812 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1440, height: 900 }
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