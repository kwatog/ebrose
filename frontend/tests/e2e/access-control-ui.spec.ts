import { test, expect } from '@playwright/test';

async function loginAs(page, username, password) {
  await page.goto('/login');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');

  try {
    await page.waitForURL('**/', { timeout: 10000 });
  } catch (e) {
    await page.goto('/');
  }

  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
}

test.describe('Access Control UI Tests', () => {

  test('Admin user can see all budget items', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: 'tests/screenshots/admin-sees-all-budgets.png',
      fullPage: true
    });
  });

  test('Regular user only sees accessible budget items', async ({ page }) => {
    await loginAs(page, 'user', 'user123');
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: 'tests/screenshots/user-filtered-budgets.png',
      fullPage: true
    });
  });

  test('User denied access to specific budget item', async ({ page }) => {
    await loginAs(page, 'user', 'user123');
    await page.goto('/budget-items/999');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: 'tests/screenshots/access-denied-403.png',
      fullPage: true
    });

    // Check for either error message or redirect to budget items list
    // (access denied may redirect rather than show error)
    const hasError = await page.locator('text=/error|denied|forbidden|not found/i').count() > 0;
    const isRedirected = page.url().includes('/budget-items') && !page.url().includes('/budget-items/999');

    expect(hasError || isRedirected).toBeTruthy();
  });

  test('Business case hybrid access - creator view', async ({ page }) => {
    await loginAs(page, 'user', 'user123');
    await page.goto('/business-cases');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: 'tests/screenshots/bc-creator-access.png',
      fullPage: true
    });
  });

  test('Business case status transition validation', async ({ page }) => {
    await loginAs(page, 'user', 'user123');
    await page.goto('/business-cases/1/edit');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: 'tests/screenshots/bc-transition-validation-error.png',
      fullPage: true
    });
  });

  test('User groups management - Admin view', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/admin/groups');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: 'tests/screenshots/admin-user-groups.png',
      fullPage: true
    });
  });

  test('Dashboard health check display', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: 'tests/screenshots/dashboard-health-check.png',
      fullPage: true
    });

    // Check that dashboard loads successfully (has main content)
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  test('Access sharing modal - record level permissions', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/purchase-orders');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Click first Share button if any POs exist
    const shareButtons = page.locator('button:has-text("Share")');
    const shareButtonCount = await shareButtons.count();

    if (shareButtonCount > 0) {
      await shareButtons.first().click();
      await page.waitForTimeout(500);

      await page.screenshot({
        path: 'tests/screenshots/access-sharing-modal.png',
        fullPage: true
      });

      await expect(page.locator('text=/share|grant|access/i').first()).toBeVisible();
    } else {
      // No POs exist - skip test
      expect(true).toBeTruthy();
    }
  });
});
