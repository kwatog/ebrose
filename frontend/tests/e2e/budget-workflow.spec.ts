import { test, expect } from './conftest';

test.describe('Budget to Business Case Workflow', () => {

  test('should create budget item successfully', async ({ adminPage }) => {
    await adminPage.goto('/budget-items');

    await adminPage.click('button:has-text("Create Budget Item")');
    await adminPage.waitForTimeout(300);

    await adminPage.fill('input[placeholder*="WD-"]', 'WD-2025-TEST');
    await adminPage.fill('input[placeholder*="Title"]', 'IT Infrastructure Budget');
    await adminPage.fill('input[type="number"]', '100000');
    await adminPage.selectOption('select', { label: 'USD' });
    await adminPage.fill('input[placeholder*="2025"]', '2025');

    await adminPage.click('button:has-text("Create")');
    await adminPage.waitForTimeout(500);

    await expect(adminPage.locator('.modal-overlay')).not.toBeVisible();
  });

  test('should navigate through dashboard quick actions', async ({ adminPage }) => {
    await adminPage.goto('/');

    await expect(adminPage.locator('text=Total Budget')).toBeVisible();

    await adminPage.click('a[href="/budget-items"]');
    await expect(adminPage).toHaveURL('/budget-items');
  });

  test('should filter budget items by fiscal year', async ({ adminPage }) => {
    await adminPage.goto('/budget-items');
    await adminPage.waitForLoadState('networkidle');

    await adminPage.selectOption('select', { label: '2025' });
  });
});

test.describe('Purchase Order Workflow', () => {

  test('should display inherited owner group in PO form', async ({ managerPage }) => {
    await managerPage.goto('/purchase-orders');
    await managerPage.waitForLoadState('networkidle');

    await managerPage.click('button:has-text("Create PO")');
    await managerPage.waitForTimeout(300);

    await expect(managerPage.locator('text=Owner Group will be automatically inherited')).toBeVisible();
  });
});
