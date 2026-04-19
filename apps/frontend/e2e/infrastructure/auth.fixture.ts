/**
 * auth.fixture.ts — Playwright authentication fixture for CarbonScope E2E tests.
 *
 * Provides:
 * - `authenticatedPage` — a `Page` already logged in with a test user session
 * - `authState` — the raw Playwright storage state (cookies + localStorage)
 *
 * Usage:
 *   import { test } from './auth.fixture';
 *
 *   test('dashboard loads', async ({ authenticatedPage }) => {
 *     await authenticatedPage.goto('/dashboard');
 *     await expect(authenticatedPage.locator('h1')).toBeVisible();
 *   });
 */

import { test as base, expect, Page, BrowserContext } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';
const BACKEND  = process.env.BACKEND_URL ?? 'http://localhost:8000';

// Storage state file — reused across tests in the same worker to avoid
// logging in for every single test.
const AUTH_STATE_FILE = path.join(__dirname, '..', '.auth', 'user.json');

// ── Test user credentials ──────────────────────────────────────────────────
// Override via environment variables in CI.
const TEST_EMAIL    = process.env.TEST_USER_EMAIL ?? 'e2e-test@carbonscopes.dev';
const TEST_PASSWORD = process.env.TEST_USER_PASSWORD ?? 'test_password_e2e_12345';

export type AuthFixtures = {
  /** A Page with an active authenticated session. */
  authenticatedPage: Page;
  /** Raw storage state (cookies + localStorage) for the test session. */
  authState: Record<string, unknown>;
};

/**
 * Extended test with authentication fixtures.
 *
 * Replace your `import { test } from '@playwright/test'` with:
 *   `import { test } from '../infrastructure/auth.fixture'`
 */
export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ browser }, use) => {
    const context = await _getOrCreateAuthContext(browser);
    const page = await context.newPage();

    await use(page);

    await page.close();
    // Do NOT close the context here — it is reused across tests in the worker.
  },

  authState: async ({}, use) => {
    const state = _loadAuthState();
    await use(state);
  },
});

export { expect };

// ── Helpers ────────────────────────────────────────────────────────────────

let _cachedContext: BrowserContext | null = null;

async function _getOrCreateAuthContext(
  browser: import('@playwright/test').Browser,
): Promise<BrowserContext> {
  // Reuse context within the same worker process.
  if (_cachedContext) return _cachedContext;

  // Try loading persisted storage state.
  if (fs.existsSync(AUTH_STATE_FILE)) {
    _cachedContext = await browser.newContext({ storageState: AUTH_STATE_FILE });
    return _cachedContext;
  }

  // No stored session — perform login.
  const context = await browser.newContext();
  const page = await context.newPage();

  await _performLogin(page);

  // Persist session for subsequent tests / workers.
  fs.mkdirSync(path.dirname(AUTH_STATE_FILE), { recursive: true });
  await context.storageState({ path: AUTH_STATE_FILE });

  await page.close();
  _cachedContext = context;
  return _cachedContext;
}

/**
 * Navigate to the login page and complete the auth flow.
 *
 * TODO: Update selectors to match the actual login page UI.
 */
async function _performLogin(page: Page): Promise<void> {
  await page.goto(`${FRONTEND}/auth`, { waitUntil: 'domcontentloaded', timeout: 30_000 });

  // Fill email
  await page.locator('input[type="email"], input[name="email"]').fill(TEST_EMAIL);

  // Fill password
  await page.locator('input[type="password"], input[name="password"]').fill(TEST_PASSWORD);

  // Submit
  await page.locator('button[type="submit"]').click();

  // Wait for redirect away from /auth
  await page.waitForURL((url) => !url.pathname.startsWith('/auth'), { timeout: 15_000 });
}

function _loadAuthState(): Record<string, unknown> {
  if (!fs.existsSync(AUTH_STATE_FILE)) return {};
  try {
    return JSON.parse(fs.readFileSync(AUTH_STATE_FILE, 'utf-8'));
  } catch {
    return {};
  }
}
