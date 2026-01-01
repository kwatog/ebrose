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

test.describe('UI/UX Feedback', () => {

  test('should load budget items page', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');

    await page.waitForLoadState('networkidle');
    await expect(page.locator('h1:has-text("Budget Items")')).toBeVisible();
  });

  test('should open create budget item modal', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');

    await page.click('button:has-text("Create Budget Item")');
    await page.waitForTimeout(300);

    await expect(page.locator('.modal-overlay')).toBeVisible();
  });

  test('should display form fields in create modal', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');

    await page.click('button:has-text("Create Budget Item")');
    await page.waitForTimeout(300);

    await expect(page.locator('input[type="text"]').first()).toBeVisible();
    await expect(page.locator('select').first()).toBeVisible(); // Use .first() to avoid strict mode
  });

  test('should allow form input in create modal', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');

    await page.click('button:has-text("Create Budget Item")');
    await page.waitForTimeout(300);

    await page.locator('input[type="text"]').first().fill('WD-TEST-001');
    await page.locator('input[type="text"]').nth(1).fill('Test Budget');

    await expect(page.locator('input[type="text"]').first()).toHaveValue('WD-TEST-001');
    await expect(page.locator('input[type="text"]').nth(1)).toHaveValue('Test Budget');
  });
});
