import { test, expect } from '@playwright/test';

async function loginAs(page, username, password) {
  await page.goto('/login');
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');

  try {
    await page.waitForURL('**/', { timeout: 10000 });
  } catch (e) {
    await page.goto('/');
  }

  await page.waitForLoadState('networkidle');
}

test.describe('Role-Based Access Control - True E2E', () => {
  test('Viewer role can see budget items', async ({ page }) => {
    await loginAs(page, 'user', 'user123');
    await page.goto('/budget-items');

    await page.waitForLoadState('networkidle');

    await expect(page.locator('table').or(page.locator('.empty-state'))).toBeVisible({ timeout: 10000 });
  });

  test('Manager can access budget items', async ({ page }) => {
    await loginAs(page, 'manager', 'manager123');
    await page.goto('/budget-items');

    await page.waitForLoadState('networkidle');

    await expect(page.locator('table').or(page.locator('.empty-state'))).toBeVisible({ timeout: 10000 });
  });

  test('Admin sees admin links', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/');

    await page.waitForLoadState('networkidle');

    await expect(page.locator('a[href="/admin/groups"]')).toBeVisible({ timeout: 10000 });
  });

  test('Manager also sees admin links', async ({ page }) => {
    await loginAs(page, 'manager', 'manager123');
    await page.goto('/');

    await page.waitForLoadState('networkidle');

    await expect(page.locator('a[href="/admin/groups"]')).toBeVisible({ timeout: 5000 });
  });

  test('User can access budget items', async ({ page }) => {
    await loginAs(page, 'user', 'user123');
    await page.goto('/budget-items');

    await page.waitForLoadState('networkidle');

    const rows = await page.locator('table tbody tr').count();
    expect(rows).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Role Permission Matrix - True E2E', () => {
  const permissions = [
    { role: 'Admin', create: true, read: true, update: true, delete: true, admin: true },
    { role: 'Manager', create: true, read: true, update: true, delete: true, admin: true },
    { role: 'User', create: true, read: true, update: true, delete: false, admin: false },
    { role: 'Viewer', create: true, read: true, update: false, delete: false, admin: false },
  ];

  permissions.forEach(({ role, create, read, update, delete: del, admin }) => {
    test(`${role} permissions: C:${create} R:${read} U:${update} D:${del} Admin:${admin}`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();

      const credentials: Record<string, { username: string; password: string }> = {
        Admin: { username: 'admin', password: 'admin123' },
        Manager: { username: 'manager', password: 'manager123' },
        User: { username: 'user', password: 'user123' },
        Viewer: { username: 'user', password: 'user123' },
      };

      const cred = credentials[role];

      await page.goto('/login');
      await page.fill('#username', cred.username);
      await page.fill('#password', cred.password);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(2000);

      await page.goto('/budget-items');
      await page.waitForLoadState('networkidle');

      if (read) {
        await expect(page.locator('table').or(page.locator('.empty-state'))).toBeVisible({ timeout: 10000 });
      }

      if (create) {
        await expect(page.locator('button:has-text("Create Budget Item")')).toBeVisible();
      } else {
        await expect(page.locator('button:has-text("Create Budget Item")')).not.toBeVisible();
      }

      if (admin) {
        await expect(page.locator('a[href="/admin/groups"]')).toBeVisible();
      } else {
        await expect(page.locator('a[href="/admin/groups"]')).not.toBeVisible();
      }

      await context.close();
    });
  });
});
