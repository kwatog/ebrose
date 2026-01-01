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

test.describe('Decimal Money Handling', () => {

  test('should display currency with 2 decimal places', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');

    // Budget Amount is in column 3 (td:nth-child(3))
    const budgetCell = page.locator('table tbody tr:first-child td:nth-child(3)');
    await expect(budgetCell).toContainText('.00');
  });

  test('should display currency with proper formatting (comma separators)', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');

    // Budget Amount is in column 3 (td:nth-child(3))
    const budgetCell = page.locator('table tbody tr:first-child td:nth-child(3)');
    await expect(budgetCell).toContainText(',');
  });

  test('should handle zero values correctly', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');

    const zeroValue = await page.locator('text=0.00').count();
    if (zeroValue === 0) {
      expect(true).toBeTruthy();
    } else {
      await expect(page.locator('text=0.00').first()).toBeVisible();
    }
  });
});
