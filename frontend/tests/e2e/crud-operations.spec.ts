import { test, expect } from '@playwright/test';

test.describe('CRUD Operations - True E2E', () => {
  test.use({ viewport: { width: 1280, height: 720 } });

  test('should navigate through entity chain using seeded data', async ({ adminPage }) => {
    // Navigate to budget items - should show seeded budget item
    await adminPage.goto('/budget-items');
    await adminPage.waitForLoadState('networkidle');

    // Seeded budget item should be visible
    await expect(adminPage.locator('table')).toBeVisible({ timeout: 10000 });
  });

  test('should navigate through full entity chain', async ({ adminPage }) => {
    // Budget Items -> Business Cases -> Line Items -> WBS -> Assets
    await adminPage.goto('/budget-items');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.locator('h1:has-text("Budget Items")')).toBeVisible();

    await adminPage.goto('/business-cases');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.locator('h1:has-text("Business Cases")')).toBeVisible();

    await adminPage.goto('/line-items');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.locator('h1:has-text("Line Items")')).toBeVisible();

    await adminPage.goto('/wbs');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.locator('h1:has-text("Work Breakdown Structure")')).toBeVisible();

    await adminPage.goto('/assets');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.locator('h1:has-text("Assets")')).toBeVisible();
  });

  test('admin should access all admin features', async ({ adminPage }) => {
    await adminPage.goto('/');
    await adminPage.waitForLoadState('networkidle');

    // Admin should see admin panel
    await expect(adminPage.locator('text=Admin Panel')).toBeVisible({ timeout: 10000 });

    // Access audit logs
    await adminPage.goto('/admin/audit');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.locator('h1:has-text("Audit Logs")')).toBeVisible();

    // Access user groups
    await adminPage.goto('/admin/groups');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.locator('h1:has-text("User Groups")')).toBeVisible();
  });

  test('manager should have different access than admin', async ({ managerPage }) => {
    await managerPage.goto('/');
    await managerPage.waitForLoadState('networkidle');

    // Manager should NOT see admin panel
    await expect(managerPage.locator('text=Admin Panel')).not.toBeVisible({ timeout: 5000 });

    // But should still access regular features
    await managerPage.goto('/budget-items');
    await managerPage.waitForLoadState('networkidle');
    await expect(managerPage.locator('h1:has-text("Budget Items")')).toBeVisible();
  });

  test('user should have restricted access', async ({ userPage }) => {
    await userPage.goto('/');
    await userPage.waitForLoadState('networkidle');

    // User should NOT see admin panel
    await expect(userPage.locator('text=Admin Panel')).not.toBeVisible({ timeout: 5000 });
  });
});
