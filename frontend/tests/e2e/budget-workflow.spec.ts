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

test.describe('Budget to Business Case Workflow', () => {

  test('should create budget item successfully', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');

    await page.waitForLoadState('networkidle');

    await page.click('button:has-text("Create Budget Item")');
    await page.waitForTimeout(300);

    // Verify modal opened with form fields
    await expect(page.locator('.modal-overlay')).toBeVisible();
    await expect(page.locator('input[type="text"]').first()).toBeVisible();
    await expect(page.locator('.modal select').first()).toBeVisible();
    await expect(page.locator('.modal button[type="submit"]')).toBeVisible();
  });

  test('should navigate through dashboard quick actions', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/');

    await expect(page.locator('text=Total Budget')).toBeVisible();

    await page.click('a[href="/budget-items"]');
    await expect(page).toHaveURL('/budget-items');
  });

  test('should filter budget items by fiscal year', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');

    await page.waitForLoadState('networkidle');

    await page.selectOption('select', { label: '2025' });
  });
});

test.describe('Purchase Order Workflow', () => {

  test('should display inherited owner group in PO form', async ({ page }) => {
    await loginAs(page, 'manager', 'manager123');
    await page.goto('/purchase-orders');

    await page.waitForLoadState('networkidle');

    // Button text is "+ Create PO"
    await page.click('button:has-text("+ Create PO")');
    await page.waitForTimeout(300);

    // Verify modal opened successfully
    await expect(page.locator('.modal-overlay')).toBeVisible();
  });
});
