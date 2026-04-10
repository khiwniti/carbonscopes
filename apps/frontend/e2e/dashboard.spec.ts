import { test, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3002';
const NAV_OPTS = { timeout: 40_000, waitUntil: 'domcontentloaded' as const };

test.describe('Dashboard Features', () => {
  // We'll skip the tests that require real login for now, 
  // or use a setup that bypasses it if available.
  
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard - it should redirect to auth if not logged in
    await page.goto(`${FRONTEND}/dashboard`, NAV_OPTS);
  });

  test('dashboard shows greeting for authenticated users', async ({ page }) => {
    // This test will skip if redirected to /auth
    if (page.url().includes('/auth')) {
      test.skip(true, 'Skipping authenticated test - redirected to login');
    }
    
    // Check for greeting component
    const greeting = page.locator('h1, h2, h3').filter({ hasText: /Good|Hello|Welcome/i });
    await expect(greeting.first()).toBeVisible({ timeout: 10000 });
  });

  test('dashboard displays Suna modes panel', async ({ page }) => {
    if (page.url().includes('/auth')) {
      test.skip(true, 'Skipping authenticated test - redirected to login');
    }
    
    // SunaModesPanel should be visible
    // Based on suna-modes-panel.tsx, it likely contains mode buttons like "Slides", "Data", etc.
    const slidesMode = page.locator('button').filter({ hasText: /Slides/i });
    await expect(slidesMode).toBeVisible();
    
    const docsMode = page.locator('button').filter({ hasText: /Docs/i });
    await expect(docsMode).toBeVisible();
  });

  test('chat input is functional', async ({ page }) => {
    if (page.url().includes('/auth')) {
      test.skip(true, 'Skipping authenticated test - redirected to login');
    }
    
    // Check for chat input
    const chatInput = page.locator('textarea, input[placeholder*="Describe what you need"]');
    await expect(chatInput.first()).toBeVisible();
    
    // Try to type something
    await chatInput.first().fill('How do I reduce my carbon footprint?');
    await expect(chatInput.first()).toHaveValue('How do I reduce my carbon footprint?');
  });

  test('sidebar accessibility', async ({ page }) => {
    if (page.url().includes('/auth')) {
      test.skip(true, 'Skipping authenticated test - redirected to login');
    }
    
    // Sidebar should be present (via AppProviders)
    // Check for common sidebar elements like "Projects" or "Knowledge"
    const projectsLink = page.locator('span').filter({ hasText: /Projects/i });
    await expect(projectsLink.first()).toBeVisible();
  });
});
