import { test, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3001';

test('chat with anonymous auth', async ({ page }) => {
  test.setTimeout(300000);
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('ERROR:', msg.text());
    }
  });

  console.log('1. Going to auth page...');
  await page.goto(`${FRONTEND}/auth`, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3000);
  
  // Dismiss "Introducing Memories" modal first
  const gotItBtn = page.locator('button:has-text("Got it")');
  if (await gotItBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
    console.log('1.5. Dismissing Memories modal...');
    await gotItBtn.click();
    await page.waitForTimeout(1000);
  }
  
  await page.screenshot({ path: 'e2e-screenshots/auth-01-page.png' });
  
  // Find and click "Continue as Guest" button
  console.log('2. Looking for Guest button...');
  const guestButton = page.locator('button:has-text("Continue as Guest")');
  
  if (await guestButton.isVisible({ timeout: 10000 }).catch(() => false)) {
    console.log('3. Clicking Continue as Guest...');
    await guestButton.click();
    
    // Wait for navigation to dashboard/agents
    console.log('4. Waiting for navigation...');
    try {
      await page.waitForURL(/\/(dashboard|agents)/, { timeout: 30000 });
      console.log('5. Navigated to:', page.url());
    } catch (e) {
      console.log('5. Navigation timeout, current URL:', page.url());
    }
    
    await page.waitForTimeout(5000);
    await page.screenshot({ path: 'e2e-screenshots/auth-02-after-guest.png' });
    
    // Now go to home to start a chat
    console.log('6. Going to home page...');
    await page.goto(FRONTEND, { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForTimeout(5000);
    
    // Dismiss modal if present again
    if (await gotItBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await gotItBtn.click();
      await page.waitForTimeout(1000);
    }
    
    await page.screenshot({ path: 'e2e-screenshots/auth-03-home.png' });
    
    // Type message
    console.log('7. Typing message...');
    const chatInput = page.locator('textarea').first();
    if (await chatInput.isVisible({ timeout: 10000 }).catch(() => false)) {
      await chatInput.fill('please help me create a sample carbon credit report with fully mockup boq for residential construction project');
      
      await page.screenshot({ path: 'e2e-screenshots/auth-04-typed.png' });
      
      // Press Enter to submit
      console.log('8. Submitting...');
      await chatInput.press('Enter');
      
      // Wait for navigation to project page
      console.log('9. Waiting for project page...');
      try {
        await page.waitForURL(/\/projects\/.*\/thread\//, { timeout: 30000 });
        console.log('10. Navigated to:', page.url());
      } catch (e) {
        console.log('10. Nav timeout, current URL:', page.url());
      }
      
      await page.screenshot({ path: 'e2e-screenshots/auth-05-project.png' });
      
      // Wait for AI response
      console.log('11. Waiting for AI response (60s)...');
      await page.waitForTimeout(60000);
      
      await page.screenshot({ path: 'e2e-screenshots/auth-06-response.png', fullPage: true });
      
      console.log('12. Test complete. Final URL:', page.url());
    } else {
      console.log('Textarea not found');
    }
  } else {
    console.log('Guest button not found');
    await page.screenshot({ path: 'e2e-screenshots/auth-no-guest.png' });
  }
});
