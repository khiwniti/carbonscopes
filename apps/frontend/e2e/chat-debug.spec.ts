import { test, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';

test('debug chat submission', async ({ page }) => {
  const allRequests: string[] = [];
  const allResponses: string[] = [];
  
  page.on('request', req => {
    allRequests.push(`${req.method()} ${req.url()}`);
  });
  
  page.on('response', res => {
    allResponses.push(`${res.status()} ${res.url()}`);
  });
  
  page.on('console', msg => {
    console.log('BROWSER:', msg.text());
  });

  await page.goto(FRONTEND, { waitUntil: 'networkidle', timeout: 120000 });
  await page.waitForTimeout(3000);
  
  // Dismiss modal
  const gotItBtn = page.locator('button:has-text("Got it")');
  if (await gotItBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
    await gotItBtn.click();
    await page.waitForTimeout(1000);
  }
  
  // Type message
  const chatInput = page.locator('textarea').first();
  await chatInput.waitFor({ state: 'visible', timeout: 10000 });
  await chatInput.fill('please help me create a sample carbon credit report with fully mockup boq for residential construction project');
  
  await page.screenshot({ path: 'e2e-screenshots/debug-01-typed.png' });
  
  // Get all buttons and log them
  const allButtons = page.locator('button');
  const buttonCount = await allButtons.count();
  console.log('Total buttons:', buttonCount);
  
  // Find the submit button more specifically
  const submitBtn = page.locator('button[type="submit"]');
  const submitCount = await submitBtn.count();
  console.log('Submit buttons:', submitCount);
  
  for (let i = 0; i < submitCount; i++) {
    const btn = submitBtn.nth(i);
    const isVisible = await btn.isVisible();
    const isDisabled = await btn.isDisabled();
    const text = await btn.textContent();
    console.log(`Submit button ${i}: visible=${isVisible}, disabled=${isDisabled}, text="${text?.trim()}"`);
  }
  
  // Clear requests before clicking
  allRequests.length = 0;
  
  // Click the visible submit button
  const visibleSubmit = submitBtn.first();
  console.log('Clicking submit button...');
  
  // Use force click in case there's an overlay
  await visibleSubmit.click({ force: true });
  
  // Wait and capture requests
  await page.waitForTimeout(5000);
  
  console.log('\n=== REQUESTS AFTER CLICK ===');
  allRequests.forEach(r => console.log(r));
  
  await page.screenshot({ path: 'e2e-screenshots/debug-02-after-click.png' });
  
  // Check current URL
  console.log('Current URL:', page.url());
  
  // Try pressing Enter key instead
  console.log('\nTrying Enter key...');
  await chatInput.focus();
  await chatInput.press('Enter');
  await page.waitForTimeout(5000);
  
  console.log('\n=== REQUESTS AFTER ENTER ===');
  allRequests.slice(-10).forEach(r => console.log(r));
  
  await page.screenshot({ path: 'e2e-screenshots/debug-03-after-enter.png' });
  console.log('Final URL:', page.url());
});
