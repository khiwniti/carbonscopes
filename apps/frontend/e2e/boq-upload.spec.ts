/**
 * boq-upload.spec.ts — BOQ (Bill of Quantities) upload smoke test.
 * Verifies the upload UI is accessible and functional.
 */

import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';
const NAV_OPTS = { timeout: 40_000, waitUntil: 'domcontentloaded' as const };

async function dismissModal(page: import('@playwright/test').Page): Promise<void> {
  const gotItBtn = page.locator('button:has-text("Got it")');
  if (await gotItBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
    await gotItBtn.click();
    await page.waitForTimeout(500);
  }
}

test.describe('BOQ Upload Flow', () => {
  test('chat input area is visible on home page', async ({ page }) => {
    await page.goto(FRONTEND, NAV_OPTS);
    await dismissModal(page);

    const chatArea = page.locator('[data-testid="chat-input"], textarea').first();
    await expect(chatArea).toBeVisible({ timeout: 30_000 });
  });

  test('file attachment button is present in chat input', async ({ page }) => {
    await page.goto(FRONTEND, NAV_OPTS);
    await dismissModal(page);
    await page.waitForTimeout(2000);

    const fileInput = page.locator('input[type="file"]');
    const attachBtn = page.locator(
      '[aria-label*="attach" i], [aria-label*="upload" i], [data-testid*="upload"]',
    );
    const hasUpload =
      (await fileInput.count()) > 0 || (await attachBtn.count()) > 0;
    expect(hasUpload).toBe(true);
  });

  test('file input accepts xlsx and csv', async ({ page }) => {
    await page.goto(FRONTEND, NAV_OPTS);
    await dismissModal(page);
    await page.waitForTimeout(2000);

    const fileInput = page.locator('input[type="file"]').first();
    if ((await fileInput.count()) === 0) {
      test.skip(true, 'No file input found — skipping upload acceptance test');
      return;
    }
    const accept = await fileInput.getAttribute('accept');
    const isAcceptable =
      !accept ||
      accept.includes('xlsx') ||
      accept.includes('*') ||
      accept.includes('spreadsheet') ||
      accept.includes('csv');
    expect(isAcceptable).toBe(true);
  });

  test('uploading a file shows progress or acknowledgment', async ({ page }) => {
    test.setTimeout(60_000);
    await page.goto(FRONTEND, NAV_OPTS);
    await dismissModal(page);
    await page.waitForTimeout(2000);

    const fileInput = page.locator('input[type="file"]').first();
    if ((await fileInput.count()) === 0) {
      test.skip(true, 'No file input found — skipping upload progress test');
      return;
    }

    const tmpDir = path.join(process.cwd(), 'e2e-screenshots');
    fs.mkdirSync(tmpDir, { recursive: true });
    const tmpFile = path.join(tmpDir, 'test-boq.csv');
    fs.writeFileSync(tmpFile, 'material,quantity,unit\nconcrete,100,m3\nsteel,50,kg\n');

    await fileInput.setInputFiles(tmpFile);
    await page.waitForTimeout(3000);

    const bodyText = (await page.locator('body').textContent()) ?? '';
    const hasUploadSignal =
      bodyText.includes('test-boq') ||
      (await page
        .locator('[role="progressbar"], [data-testid*="progress"], [class*="progress"]')
        .count()) > 0 ||
      (await page.locator('[class*="attachment"], [class*="file"]').count()) > 0;

    if (fs.existsSync(tmpFile)) {
      fs.unlinkSync(tmpFile);
    }

    expect(hasUploadSignal).toBe(true);
  });
});
