import { test, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3002';
const NAV_OPTS = { timeout: 40_000, waitUntil: 'domcontentloaded' as const };

test.describe('Project Features', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard - to use the sidebar for projects
    await page.goto(`${FRONTEND}/dashboard`, NAV_OPTS);
  });

  test('project list in sidebar is accessible', async ({ page }) => {
    if (page.url().includes('/auth')) {
      test.skip(true, 'Skipping authenticated test - redirected to login');
    }
    
    // "Projects" header should be present
    const projectsHeader = page.locator('span').filter({ hasText: /^Projects$/ });
    await expect(projectsHeader).toBeVisible();
    
    // Check if "New project" button (plus icon) exists
    const newProjectBtn = page.locator('button').filter({ hasText: /New project/i }).or(
        page.locator('button[aria-label*="New project"]')
    );
    // Since it's a Tooltip, the aria-label might not be directly on the button.
    // Let's use the plus icon locator if we can, or just check for existence
    const plusIcon = page.locator('svg.lucide-plus');
    await expect(plusIcon.first()).toBeVisible();
  });

  test('can open new project dialog', async ({ page }) => {
    if (page.url().includes('/auth')) {
      test.skip(true, 'Skipping authenticated test - redirected to login');
    }
    
    // Click plus icon to open dialog
    const plusIcon = page.locator('svg.lucide-plus').first();
    await plusIcon.click();
    
    // NewAgentDialog should appear
    // It should have a heading like "New project" or "Create agent"
    const dialogHeading = page.locator('h2, h3').filter({ hasText: /New|Create/i });
    await expect(dialogHeading.first()).toBeVisible();
  });

  test('individual project view redirects to login if unauthenticated', async ({ page }) => {
    // Attempting to visit a random project page directly
    const randomProjectId = '550e8400-e29b-41d4-a716-446655440000';
    await page.goto(`${FRONTEND}/projects/${randomProjectId}`, NAV_OPTS);
    
    // Should be redirected or show login
    await expect(page).toHaveURL(/.*auth|.*sign-in/);
  });
});
