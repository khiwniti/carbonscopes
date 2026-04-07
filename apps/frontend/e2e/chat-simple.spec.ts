import { test, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';

test('simple chat test', async ({ page }) => {
  test.setTimeout(300000);
  
  console.log('Loading page...');
  await page.goto(FRONTEND, { waitUntil: 'domcontentloaded', timeout: 60000 });
  
  // Wait for page to fully render
  await page.waitForTimeout(10000);
  await page.screenshot({ path: 'e2e-screenshots/simple-01-loaded.png' });
  
  // Dismiss modal if present
  const gotItBtn = page.locator('button:has-text("Got it")');
  if (await gotItBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
    await gotItBtn.click();
    await page.waitForTimeout(2000);
  }
  
  await page.screenshot({ path: 'e2e-screenshots/simple-02-modal-dismissed.png' });
  
  // Find textarea
  const chatInput = page.locator('textarea').first();
  console.log('Textarea visible:', await chatInput.isVisible({ timeout: 5000 }).catch(() => false));
  
  if (await chatInput.isVisible({ timeout: 10000 }).catch(() => false)) {
    await chatInput.fill('please help me create a sample carbon credit report with fully mockup boq for residential construction project');
    console.log('Message typed');
    
    await page.screenshot({ path: 'e2e-screenshots/simple-03-typed.png' });
    
    // Submit with Enter
    await chatInput.press('Enter');
    console.log('Enter pressed');
    
    // Wait for navigation
    await page.waitForTimeout(15000);
    console.log('Current URL:', page.url());
    
    await page.screenshot({ path: 'e2e-screenshots/simple-04-after-submit.png' });
    
    // If on project page, wait for response
    if (page.url().includes('/projects/')) {
      console.log('On project page, waiting for response...');
      
      await page.waitForTimeout(60000);
      await page.screenshot({ path: 'e2e-screenshots/simple-05-response.png', fullPage: true });
    }
  } else {
    console.log('Textarea not found');
    await page.screenshot({ path: 'e2e-screenshots/simple-no-textarea.png' });
  }
  
  console.log('Test complete');
});
