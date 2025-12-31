import { test, expect } from './conftest';

test.describe('Access Control UI Tests', () => {

  test('Admin user can see all budget items', async ({ adminPage }) => {
    await adminPage.goto('/budget-items');
    await adminPage.waitForLoadState('networkidle');

    await adminPage.screenshot({
      path: 'tests/screenshots/admin-sees-all-budgets.png',
      fullPage: true
    });
  });

  test('Regular user only sees accessible budget items', async ({ userPage }) => {
    await userPage.goto('/budget-items');
    await userPage.waitForLoadState('networkidle');

    await userPage.screenshot({
      path: 'tests/screenshots/user-filtered-budgets.png',
      fullPage: true
    });
  });

  test('User denied access to specific budget item', async ({ userPage }) => {
    await userPage.goto('/budget-items/999');
    await userPage.waitForLoadState('networkidle');

    await userPage.screenshot({
      path: 'tests/screenshots/access-denied-403.png',
      fullPage: true
    });

    await expect(userPage.locator('text=/403|Forbidden|access denied/i')).toBeVisible();
  });

  test('Business case hybrid access - creator view', async ({ userPage }) => {
    await userPage.goto('/business-cases');
    await userPage.waitForLoadState('networkidle');

    await userPage.screenshot({
      path: 'tests/screenshots/bc-creator-access.png',
      fullPage: true
    });
  });

  test('Business case status transition validation', async ({ userPage }) => {
    await userPage.goto('/business-cases/1/edit');
    await userPage.waitForLoadState('networkidle');

    await userPage.screenshot({
      path: 'tests/screenshots/bc-transition-validation-error.png',
      fullPage: true
    });
  });

  test('User groups management - Admin view', async ({ adminPage }) => {
    await adminPage.goto('/admin/groups');
    await adminPage.waitForLoadState('networkidle');

    await adminPage.screenshot({
      path: 'tests/screenshots/admin-user-groups.png',
      fullPage: true
    });
  });

  test('Dashboard health check display', async ({ adminPage }) => {
    await adminPage.goto('/');
    await adminPage.waitForLoadState('networkidle');

    await adminPage.screenshot({
      path: 'tests/screenshots/dashboard-health-check.png',
      fullPage: true
    });

    await expect(adminPage.locator('text=/healthy|connected/i')).toBeVisible();
  });

  test('Access sharing modal - record level permissions', async ({ adminPage }) => {
    await adminPage.goto('/budget-items/1');
    await adminPage.waitForLoadState('networkidle');

    await adminPage.click('button:has-text("Share")');
    await adminPage.waitForTimeout(500);

    await adminPage.screenshot({
      path: 'tests/screenshots/access-sharing-modal.png',
      fullPage: true
    });

    await expect(adminPage.locator('text=/Share Access|Grant Access/i')).toBeVisible();
  });
});
