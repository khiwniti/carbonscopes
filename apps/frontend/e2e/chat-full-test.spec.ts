import { test, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';

test('full chat test with carbon credit report', async ({ page }) => {
  // Increase timeout for this test
  test.setTimeout(300000); // 5 minutes
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('ERROR:', msg.text());
    }
  });

  console.log('1. Navigating to home page...');
  await page.goto(FRONTEND, { waitUntil: 'networkidle', timeout: 120000 });
  await page.waitForTimeout(3000);
  
  // Dismiss modal
  const gotItBtn = page.locator('button:has-text("Got it")');
  if (await gotItBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
    await gotItBtn.click();
    console.log('2. Dismissed modal');
    await page.waitForTimeout(1000);
  }
  
  console.log('3. Typing message...');
  const chatInput = page.locator('textarea').first();
  await chatInput.waitFor({ state: 'visible', timeout: 10000 });
  await chatInput.fill('please help me create a sample carbon credit report with fully mockup boq for residential construction project');
  
  await page.screenshot({ path: 'e2e-screenshots/full-01-typed.png' });
  
  console.log('4. Pressing Enter to submit...');
  await chatInput.press('Enter');
  
  // Wait for navigation to project page
  console.log('5. Waiting for navigation to project page...');
  try {
    await page.waitForURL(/\/projects\/.*\/thread\//, { timeout: 30000 });
    console.log('6. Navigated to:', page.url());
  } catch (e) {
    console.log('Navigation timeout, current URL:', page.url());
    await page.screenshot({ path: 'e2e-screenshots/full-02-nav-timeout.png' });
  }
  
  await page.screenshot({ path: 'e2e-screenshots/full-03-project-page.png' });
  
  // Wait for agent response
  console.log('7. Waiting for agent response...');
  await page.waitForTimeout(30000);
  
  await page.screenshot({ path: 'e2e-screenshots/full-04-response-30s.png' });
  
  // Continue waiting
  console.log('8. Waiting more for full response...');
  await page.waitForTimeout(60000);
  
  await page.screenshot({ path: 'e2e-screenshots/full-05-response-90s.png', fullPage: true });
  
  console.log('9. Test complete. Final URL:', page.url());
});
