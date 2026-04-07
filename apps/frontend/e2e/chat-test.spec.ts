import { test, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';

test.describe('Chat functionality', () => {
  test('start a chat with carbon credit question', async ({ page }) => {
    // Go to home page
    await page.goto(FRONTEND, { waitUntil: 'domcontentloaded', timeout: 90000 });
    
    // Wait for page to fully load
    await page.waitForTimeout(5000);
    await page.screenshot({ path: 'e2e-screenshots/chat-01-initial.png' });
    
    // Dismiss "Introducing Memories" modal if present
    const gotItBtn = page.locator('button:has-text("Got it")');
    if (await gotItBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await gotItBtn.click();
      console.log('Dismissed Memories modal');
      await page.waitForTimeout(2000);
    }
    
    await page.screenshot({ path: 'e2e-screenshots/chat-02-modal-dismissed.png' });
    
    // Select "Research" mode for carbon credit question
    const researchBtn = page.locator('button:has-text("Research"), div:has-text("Research")').first();
    if (await researchBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await researchBtn.click();
      console.log('Selected Research mode');
      await page.waitForTimeout(1000);
    }
    
    await page.screenshot({ path: 'e2e-screenshots/chat-03-mode-selected.png' });
    
    // Find and fill the chat input
    const chatInput = page.locator('textarea').first();
    await chatInput.waitFor({ state: 'visible', timeout: 10000 });
    
    await chatInput.click();
    await chatInput.fill('what carbon credit are');
    console.log('Typed: what carbon credit are');
    
    await page.screenshot({ path: 'e2e-screenshots/chat-04-typed.png' });
    
    // Find the send button (green arrow button)
    const sendButton = page.locator('button[type="submit"]').first();
    
    // Check if button is enabled
    const isDisabled = await sendButton.getAttribute('disabled');
    console.log('Send button disabled:', isDisabled !== null);
    
    if (isDisabled === null) {
      // Button is enabled, click it
      await sendButton.click();
      console.log('Clicked send button');
    } else {
      // Button is disabled, try keyboard shortcut or check if auth is needed
      console.log('Send button is disabled - likely requires authentication');
      
      // Try Ctrl+Enter or Cmd+Enter
      await chatInput.press('Control+Enter');
      console.log('Tried Ctrl+Enter');
    }
    
    // Wait for any response or redirect
    await page.waitForTimeout(10000);
    await page.screenshot({ path: 'e2e-screenshots/chat-05-after-submit.png' });
    
    // Check current state
    const currentUrl = page.url();
    console.log('Final URL:', currentUrl);
    
    // Check if we're on a project/thread page (successful submission)
    if (currentUrl.includes('/project') || currentUrl.includes('/thread')) {
      console.log('SUCCESS: Chat was submitted and redirected to project/thread');
      
      // Wait for AI response
      await page.waitForTimeout(15000);
      await page.screenshot({ path: 'e2e-screenshots/chat-06-response.png' });
    } else if (currentUrl.includes('/auth')) {
      console.log('Redirected to auth - need to login');
    } else {
      console.log('Still on home page - submission may require auth');
    }
  });
});
