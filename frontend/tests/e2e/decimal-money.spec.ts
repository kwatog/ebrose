import { test, expect } from './conftest';

test.describe('Decimal Money Handling', () => {

  test('should display currency with 2 decimal places', async ({ adminPage }) => {
    await adminPage.goto('/budget-items');
    await adminPage.waitForLoadState('networkidle');

    const budgetCell = adminPage.locator('table tbody tr:first-child td:nth-child(4)');
    await expect(budgetCell).toContainText('.00');
  });

  test('should display currency with proper formatting (comma separators)', async ({ adminPage }) => {
    await adminPage.goto('/budget-items');
    await adminPage.waitForLoadState('networkidle');

    const budgetCell = adminPage.locator('table tbody tr:first-child td:nth-child(4)');
    await expect(budgetCell).toContainText(',');
  });

  test('should handle zero values correctly', async ({ adminPage }) => {
    await adminPage.goto('/budget-items');
    await adminPage.waitForLoadState('networkidle');

    await expect(adminPage.locator('text=0.00')).toBeVisible();
  });
});
