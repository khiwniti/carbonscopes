/**
 * page.helpers.ts — Common Playwright page interaction helpers.
 *
 * Centralises selectors and repeated interaction patterns so individual
 * tests stay readable.  All helpers accept a `Page` and return values /
 * Playwright `Locator`s rather than making assertions themselves —
 * assertions belong in tests.
 *
 * Usage:
 *   import { PageHelpers } from './page.helpers';
 *
 *   const helpers = new PageHelpers(page);
 *   await helpers.navigateToDashboard();
 *   const greeting = await helpers.getGreeting();
 */

import { Page, Locator, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';
const NAV_TIMEOUT = 40_000;

export class PageHelpers {
  constructor(private readonly page: Page) {}

  // ── Navigation ───────────────────────────────────────────────────────────

  async navigateTo(path: string): Promise<void> {
    await this.page.goto(`${FRONTEND}${path}`, {
      waitUntil: 'domcontentloaded',
      timeout: NAV_TIMEOUT,
    });
  }

  async navigateToDashboard(): Promise<void> {
    await this.navigateTo('/dashboard');
  }

  async navigateToProjects(): Promise<void> {
    await this.navigateTo('/projects');
  }

  async navigateToAgentChat(): Promise<void> {
    await this.navigateTo('/carbonscope');
  }

  // ── Auth state ───────────────────────────────────────────────────────────

  isOnAuthPage(): boolean {
    return this.page.url().includes('/auth');
  }

  skipIfNotAuthenticated(testContext: { skip: (condition: boolean, reason: string) => void }): void {
    testContext.skip(
      this.isOnAuthPage(),
      'Skipping: not authenticated (redirected to /auth)',
    );
  }

  // ── Dashboard ────────────────────────────────────────────────────────────

  getGreeting(): Locator {
    return this.page.locator('h1, h2, h3').filter({ hasText: /Good|Hello|Welcome/i }).first();
  }

  getcarbonscopeModesPanel(): Locator {
    // TODO: Update to match actual selector for the carbonscope modes panel.
    return this.page.locator('[data-testid="carbonscope-modes"], [class*="modes"]').first();
  }

  // ── Projects ─────────────────────────────────────────────────────────────

  getProjectCards(): Locator {
    // TODO: Update selector to match actual project card component.
    return this.page.locator('[data-testid="project-card"], [class*="project-card"]');
  }

  async getProjectCount(): Promise<number> {
    return this.getProjectCards().count();
  }

  async clickCreateProject(): Promise<void> {
    await this.page
      .locator('button', { hasText: /new project|create project/i })
      .first()
      .click();
  }

  async fillProjectName(name: string): Promise<void> {
    await this.page
      .locator('input[placeholder*="project name"], input[name="name"]')
      .fill(name);
  }

  // ── Agent Chat (carbonscope) ────────────────────────────────────────────────────

  getChatInput(): Locator {
    return this.page.locator('[data-testid="chat-input"], textarea').first();
  }

  async sendChatMessage(message: string): Promise<void> {
    const input = this.getChatInput();
    await input.fill(message);
    await this.page.keyboard.press('Enter');
  }

  getChatMessages(): Locator {
    // TODO: Update selector to match actual chat message component.
    return this.page.locator('[data-testid="chat-message"], [class*="message"]');
  }

  // ── Navigation sidebar ────────────────────────────────────────────────────

  getSidebarNav(): Locator {
    return this.page.locator('nav[aria-label], aside nav, [data-testid="sidebar"]').first();
  }

  async clickNavItem(label: string): Promise<void> {
    await this.getSidebarNav().locator(`text="${label}"`).click();
  }

  // ── Loading states ────────────────────────────────────────────────────────

  async waitForPageLoad(): Promise<void> {
    // Wait for loading spinners to disappear.
    const spinner = this.page.locator('[data-testid="loading"], [class*="spinner"], [class*="skeleton"]');
    if (await spinner.count() > 0) {
      await spinner.first().waitFor({ state: 'hidden', timeout: 15_000 });
    }
  }

  async waitForToast(message?: string): Promise<Locator> {
    const toast = message
      ? this.page.locator(`[role="alert"]`).filter({ hasText: message })
      : this.page.locator(`[role="alert"]`).first();
    await toast.waitFor({ state: 'visible', timeout: 10_000 });
    return toast;
  }

  // ── Forms ─────────────────────────────────────────────────────────────────

  async submitForm(): Promise<void> {
    await this.page.locator('button[type="submit"]').click();
  }

  async fillInput(label: string, value: string): Promise<void> {
    await this.page.getByLabel(label).fill(value);
  }

  // ── Screenshots ───────────────────────────────────────────────────────────

  async captureScreenshot(name: string): Promise<void> {
    await this.page.screenshot({
      path: `e2e-screenshots/${name}-${Date.now()}.png`,
      fullPage: true,
    });
  }
}
