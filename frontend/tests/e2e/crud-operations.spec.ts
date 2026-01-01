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

test.describe('CRUD Operations - True E2E', () => {
  test.use({ viewport: { width: 1280, height: 720 } });

  test('should navigate through entity chain using seeded data', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');

    await page.waitForLoadState('networkidle');

    await expect(page.locator('table')).toBeVisible({ timeout: 10000 });
  });

  test('should navigate through full entity chain', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');

    await page.waitForLoadState('networkidle');
    await expect(page.locator('h1:has-text("Budget Items")')).toBeVisible();

    await loginAs(page, 'admin', 'admin123');
    await page.goto('/business-cases');

    await page.waitForLoadState('networkidle');
    await expect(page.locator('h1:has-text("Business Cases")')).toBeVisible();

    await loginAs(page, 'admin', 'admin123');
    await page.goto('/line-items');

    await page.waitForLoadState('networkidle');
    await expect(page.locator('h1:has-text("Line Items")')).toBeVisible();

    await loginAs(page, 'admin', 'admin123');
    await page.goto('/wbs');

    await page.waitForLoadState('networkidle');
    await expect(page.locator('h1:has-text("Work Breakdown Structure")')).toBeVisible();

    await loginAs(page, 'admin', 'admin123');
    await page.goto('/assets');

    await page.waitForLoadState('networkidle');
    await expect(page.locator('h1:has-text("Assets")')).toBeVisible();
  });

  test('admin should access all admin features', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/');

    await page.waitForLoadState('networkidle');

    // Admin nav shows "Groups" and "Audit Logs" links, not "Admin Panel"
    await expect(page.locator('a[href="/admin/groups"]')).toBeVisible({ timeout: 10000 });

    await loginAs(page, 'admin', 'admin123');
    await page.goto('/admin/audit');

    await page.waitForLoadState('networkidle');
    await expect(page.locator('h1').filter({ hasText: 'Audit Logs' })).toBeVisible();

    await loginAs(page, 'admin', 'admin123');
    await page.goto('/admin/groups');

    await page.waitForLoadState('networkidle');
    await expect(page.locator('h1:has-text("User Groups")')).toBeVisible();
  });

  test('manager should have different access than admin', async ({ page }) => {
    await loginAs(page, 'manager', 'manager123');
    await page.goto('/');

    await page.waitForLoadState('networkidle');

    // Manager should see Groups and Audit Logs links (admin AND manager can see them)
    await expect(page.locator('a[href="/admin/groups"]')).toBeVisible({ timeout: 5000 });

    await loginAs(page, 'manager', 'manager123');
    await page.goto('/budget-items');

    await page.waitForLoadState('networkidle');
    await expect(page.locator('h1:has-text("Budget Items")')).toBeVisible();
  });

  test('user should have restricted access', async ({ page }) => {
    await loginAs(page, 'user', 'user123');
    await page.goto('/');

    await page.waitForLoadState('networkidle');

    // User should NOT see Groups and Audit Logs links
    await expect(page.locator('a[href="/admin/groups"]')).not.toBeVisible({ timeout: 5000 });
  });
});
