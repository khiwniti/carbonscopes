import { test, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';
const NAV_OPTS = { timeout: 40_000, waitUntil: 'domcontentloaded' as const };

test.describe('Dashboard Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${FRONTEND}/dashboard`, NAV_OPTS);
  });

  test('dashboard shows greeting for authenticated users', async ({ page }) => {
    test.skip(page.url().includes('/auth'), 'Skipping authenticated test - redirected to login');

    const greeting = page.locator('h1, h2, h3').filter({ hasText: /Good|Hello|Welcome/i });
    await expect(greeting.first()).toBeVisible({ timeout: 10000 });
  });

  test('dashboard displays carbonscope modes panel', async ({ page }) => {
    test.skip(page.url().includes('/auth'), 'Skipping authenticated test - redirected to login');

    const slidesMode = page.locator('button').filter({ hasText: /Slides/i });
    await expect(slidesMode).toBeVisible();

    const docsMode = page.locator('button').filter({ hasText: /Docs/i });
    await expect(docsMode).toBeVisible();
  });

  test('chat input is functional', async ({ page }) => {
    test.skip(page.url().includes('/auth'), 'Skipping authenticated test - redirected to login');

    const chatInput = page.locator('[data-testid="chat-input"], textarea, input[placeholder*="Describe what you need"]');
    await expect(chatInput.first()).toBeVisible();

    await chatInput.first().fill('How do I reduce my carbon footprint?');
    await expect(chatInput.first()).toHaveValue('How do I reduce my carbon footprint?');
  });

  test('sidebar accessibility', async ({ page }) => {
    test.skip(page.url().includes('/auth'), 'Skipping authenticated test - redirected to login');

    const projectsLink = page.locator('span').filter({ hasText: /Projects/i });
    await expect(projectsLink.first()).toBeVisible();
  });
});
