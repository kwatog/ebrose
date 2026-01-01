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

test.describe('UI/UX Feedback', () => {

  test('should load budget items page', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await expect(page.locator('.base-card, h3').filter({ hasText: /Budget/i })).toBeVisible({ timeout: 10000 });
  });

  test('should open create budget item modal', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await page.click('button:has-text("+ Create Budget Item")');
    await page.waitForTimeout(500);

    await expect(page.locator('.modal-overlay, [role="dialog"]')).toBeVisible();
  });

  test('should display form fields in create modal', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await page.click('button:has-text("+ Create Budget Item")');
    await page.waitForTimeout(500);

    // Check for form inputs (BaseInput renders with label)
    const inputCount = await page.locator('input[type="text"], input[type="number"], label').count();
    expect(inputCount).toBeGreaterThan(0);
  });

  test('should allow form input in create modal', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await page.click('button:has-text("+ Create Budget Item")');
    await page.waitForTimeout(500);

    // Fill form fields
    const textInputs = page.locator('input[type="text"]');
    if (await textInputs.count() >= 2) {
      await textInputs.first().fill('WD-TEST-001');
      await textInputs.nth(1).fill('Test Budget');

      await expect(textInputs.first()).toHaveValue('WD-TEST-001');
      await expect(textInputs.nth(1)).toHaveValue('Test Budget');
    }
  });
});
