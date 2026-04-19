import { test, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';
const NAV_OPTS = { timeout: 40_000, waitUntil: 'domcontentloaded' as const };

test.describe('Project Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${FRONTEND}/dashboard`, NAV_OPTS);
  });

  test('project list in sidebar is accessible', async ({ page }) => {
    test.skip(page.url().includes('/auth'), 'Skipping authenticated test - redirected to login');

    const projectsHeader = page.locator('span').filter({ hasText: /^Projects$/ });
    await expect(projectsHeader).toBeVisible();

    const plusIcon = page.locator('svg.lucide-plus');
    await expect(plusIcon.first()).toBeVisible();
  });

  test('can open new project dialog', async ({ page }) => {
    test.skip(page.url().includes('/auth'), 'Skipping authenticated test - redirected to login');

    const plusIcon = page.locator('svg.lucide-plus').first();
    await plusIcon.click();

    const dialogHeading = page.locator('h2, h3').filter({ hasText: /New|Create/i });
    await expect(dialogHeading.first()).toBeVisible();
  });

  test('individual project view redirects to login if unauthenticated', async ({ page }) => {
    const randomProjectId = '550e8400-e29b-41d4-a716-446655440000';
    await page.goto(`${FRONTEND}/projects/${randomProjectId}`, NAV_OPTS);

    await expect(page).toHaveURL(/.*auth|.*sign-in/);
  });
});
