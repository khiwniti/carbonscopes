import { test, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';

test.describe('Carbon Credit Report Chat', () => {
  test('start chat with carbon credit report request', async ({ page }) => {
    // Capture console errors
    const consoleErrors: string[] = [];
    const consoleWarnings: string[] = [];
    const networkErrors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
      if (msg.type() === 'warning') {
        consoleWarnings.push(msg.text());
      }
    });
    
    page.on('pageerror', err => {
      consoleErrors.push(`Page Error: ${err.message}`);
    });
    
    page.on('requestfailed', request => {
      networkErrors.push(`Failed: ${request.url()} - ${request.failure()?.errorText}`);
    });

    // Go to home page
    console.log('Navigating to:', FRONTEND);
    await page.goto(FRONTEND, { waitUntil: 'networkidle', timeout: 120000 });
    
    // Wait for page to stabilize
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'e2e-screenshots/carbon-01-home.png' });
    
    // Dismiss "Introducing Memories" modal if present
    const gotItBtn = page.locator('button:has-text("Got it")');
    if (await gotItBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await gotItBtn.click();
      console.log('Dismissed Memories modal');
      await page.waitForTimeout(1000);
    }
    
    await page.screenshot({ path: 'e2e-screenshots/carbon-02-modal-dismissed.png' });
    
    // Find and fill the chat input
    const chatInput = page.locator('textarea').first();
    await chatInput.waitFor({ state: 'visible', timeout: 10000 });
    
    const message = 'please help me create a sample carbon credit report with fully mockup boq for residential construction project';
    
    await chatInput.click();
    await chatInput.fill(message);
    console.log('Typed message:', message);
    
    await page.screenshot({ path: 'e2e-screenshots/carbon-03-typed.png' });
    
    // Find and click the send button
    const sendButton = page.locator('button[type="submit"]').first();
    const isDisabled = await sendButton.getAttribute('disabled');
    console.log('Send button disabled:', isDisabled !== null);
    
    if (isDisabled === null) {
      await sendButton.click();
      console.log('Clicked send button');
    } else {
      console.log('Send button is disabled - checking why...');
      // Try using keyboard
      await chatInput.press('Control+Enter');
    }
    
    // Wait for response or navigation
    await page.waitForTimeout(15000);
    await page.screenshot({ path: 'e2e-screenshots/carbon-04-after-submit.png' });
    
    const currentUrl = page.url();
    console.log('Current URL:', currentUrl);
    
    // Check if redirected to project/thread
    if (currentUrl.includes('/project') || currentUrl.includes('/thread')) {
      console.log('SUCCESS: Redirected to project/thread page');
      
      // Wait for AI response
      await page.waitForTimeout(30000);
      await page.screenshot({ path: 'e2e-screenshots/carbon-05-response.png' });
    }
    
    // Print all captured errors
    console.log('\n=== CONSOLE ERRORS ===');
    consoleErrors.forEach(e => console.log('ERROR:', e));
    
    console.log('\n=== CONSOLE WARNINGS ===');
    consoleWarnings.slice(0, 10).forEach(w => console.log('WARN:', w));
    
    console.log('\n=== NETWORK ERRORS ===');
    networkErrors.forEach(n => console.log('NETWORK:', n));
    
    // Take final screenshot
    await page.screenshot({ path: 'e2e-screenshots/carbon-06-final.png', fullPage: true });
  });
});
