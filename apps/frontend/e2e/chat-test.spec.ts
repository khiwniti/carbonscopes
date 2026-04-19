import { test, expect } from '@playwright/test';
import { AsyncExpect } from './infrastructure/async_expect';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';

test.describe('Chat functionality', () => {
  test('start a chat with carbon credit question', async ({ page }) => {
    await page.goto(FRONTEND, { waitUntil: 'domcontentloaded', timeout: 60000 });

    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'e2e-screenshots/chat-01-initial.png' });

    const gotItBtn = page.locator('button:has-text("Got it")');
    if (await gotItBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await gotItBtn.click();
      console.log('Dismissed Memories modal');
      await page.waitForTimeout(2000);
    }

    await page.screenshot({ path: 'e2e-screenshots/chat-02-modal-dismissed.png' });

    const researchBtn = page
      .locator('button:has-text("Research"), div:has-text("Research")')
      .first();
    if (await researchBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await researchBtn.click();
      console.log('Selected Research mode');
      await page.waitForTimeout(1000);
    }

    await page.screenshot({ path: 'e2e-screenshots/chat-03-mode-selected.png' });

    const chatInput = page.locator('[data-testid="chat-input"], textarea').first();
    await AsyncExpect.waitUntil(
      () => chatInput.isVisible(),
      'chat textarea to be visible',
      { timeout: 30_000, pollInterval: 500 },
    );

    await chatInput.click();
    await chatInput.fill('what carbon credit are');
    console.log('Typed: what carbon credit are');

    await page.screenshot({ path: 'e2e-screenshots/chat-04-typed.png' });

    const sendButton = page.locator('button[type="submit"]').first();

    const isDisabled = await sendButton.getAttribute('disabled');
    console.log('Send button disabled:', isDisabled !== null);

    if (isDisabled === null) {
      await sendButton.click();
      console.log('Clicked send button');
    } else {
      console.log('Send button is disabled - likely requires authentication');
      await chatInput.press('Control+Enter');
      console.log('Tried Ctrl+Enter');
    }

    await page.waitForTimeout(10000);
    await page.screenshot({ path: 'e2e-screenshots/chat-05-after-submit.png' });

    const currentUrl = page.url();
    console.log('Final URL:', currentUrl);

    if (currentUrl.includes('/project') || currentUrl.includes('/thread')) {
      console.log('SUCCESS: Chat was submitted and redirected to project/thread');

      await page.waitForTimeout(15000);
      await page.screenshot({ path: 'e2e-screenshots/chat-06-response.png' });
    } else if (currentUrl.includes('/auth')) {
      console.log('Redirected to auth - need to login');
    } else {
      console.log('Still on home page - submission may require auth');
    }
  });
});
