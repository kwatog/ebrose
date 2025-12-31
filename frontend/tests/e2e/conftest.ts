import { test as base, chromium, type BrowserContext } from '@playwright/test';

export const test = base.extend<{
  authenticatedContext: BrowserContext;
  adminContext: BrowserContext;
  managerContext: BrowserContext;
  userContext: BrowserContext;
}>({
  authenticatedContext: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto('http://localhost:3000/login');
    await page.fill('#username', 'testadmin');
    await page.fill('#password', 'testpass123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');

    await context.close();
  },

  adminContext: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto('http://localhost:3000/login');
    await page.fill('#username', 'testadmin');
    await page.fill('#password', 'testpass123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');

    await use(context);
    await context.close();
  },

  managerContext: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto('http://localhost:3000/login');
    await page.fill('#username', 'testmanager');
    await page.fill('#password', 'testpass123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');

    await use(context);
    await context.close();
  },

  userContext: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto('http://localhost:3000/login');
    await page.fill('#username', 'testuser');
    await page.fill('#password', 'testpass123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');

    await use(context);
    await context.close();
  },
});

export { expect } from '@playwright/test';
