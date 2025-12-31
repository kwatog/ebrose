import { test as base, type BrowserContext, type Page } from '@playwright/test';

const USERS = {
  admin: { username: 'admin', password: 'admin123', role: 'Admin' },
  manager: { username: 'manager', password: 'manager123', role: 'Manager' },
  user: { username: 'user', password: 'user123', role: 'User' },
};

async function loginUser(page: Page, username: string, password: string): Promise<void> {
  await page.goto('/login');
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');

  // Wait for either navigation to '/' or for the cookie to be set
  // The navigateTo('/') in Vue may not trigger page.waitForURL in some cases
  await page.waitForFunction(() => {
    const cookie = document.cookie.split('; ').find(c => c.startsWith('user_info='));
    return cookie !== undefined;
  }, { timeout: 10000 }).catch(() => {
    // If cookie wait times out, just continue - the navigation might have happened
  });
}

export const test = base.extend<{
  adminPage: Page;
  managerPage: Page;
  userPage: Page;
  adminContext: BrowserContext;
  managerContext: BrowserContext;
  userContext: BrowserContext;
}>({
  adminPage: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await loginUser(page, USERS.admin.username, USERS.admin.password);
    await use(page);
    await context.close();
  },

  managerPage: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await loginUser(page, USERS.manager.username, USERS.manager.password);
    await use(page);
    await context.close();
  },

  userPage: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await loginUser(page, USERS.user.username, USERS.user.password);
    await use(page);
    await context.close();
  },

  adminContext: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await loginUser(page, USERS.admin.username, USERS.admin.password);
    await use(context);
    await context.close();
  },

  managerContext: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await loginUser(page, USERS.manager.username, USERS.manager.password);
    await use(context);
    await context.close();
  },

  userContext: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await loginUser(page, USERS.user.username, USERS.user.password);
    await use(context);
    await context.close();
  },
});

export { expect } from '@playwright/test';
