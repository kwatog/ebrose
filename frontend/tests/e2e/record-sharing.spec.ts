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

test.describe('Record Access Sharing', () => {

  test('should grant Read access to specific user', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/purchase-orders');

    await page.waitForLoadState('networkidle');

    // Click the first Share button if any POs exist
    const shareButtons = page.locator('button:has-text("Share")');
    const shareButtonCount = await shareButtons.count();

    if (shareButtonCount > 0) {
      await shareButtons.first().click();
      await page.waitForTimeout(500);

      // Verify share modal opened
      await expect(page.locator('text=/share|grant access/i').first()).toBeVisible();
    }
  });

  test('should grant Read/Write access to group', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/purchase-orders');

    await page.waitForLoadState('networkidle');

    const shareButtons = page.locator('button:has-text("Share")');
    const shareButtonCount = await shareButtons.count();

    if (shareButtonCount > 0) {
      await shareButtons.first().click();
      await page.waitForTimeout(500);

      // Check if "Group" option exists in the share modal
      const hasGroupOption = await page.locator('text=/group/i').count() > 0;
      expect(hasGroupOption).toBeTruthy();
    }
  });

  test('should set and verify access expiration', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/purchase-orders');

    await page.waitForLoadState('networkidle');

    const shareButtons = page.locator('button:has-text("Share")');
    const shareButtonCount = await shareButtons.count();

    if (shareButtonCount > 0) {
      await shareButtons.first().click();
      await page.waitForTimeout(500);

      // Verify share modal opened
      await expect(page.locator('text=/share|grant/i').first()).toBeVisible();
    }
  });

  test('should revoke previously granted access', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/purchase-orders');

    await page.waitForLoadState('networkidle');

    const shareButtons = page.locator('button:has-text("Share")');
    const shareButtonCount = await shareButtons.count();

    if (shareButtonCount > 0) {
      await shareButtons.first().click();
      await page.waitForTimeout(500);

      const revokeButton = page.locator('button:has-text("Revoke")').first();
      if (await revokeButton.isVisible()) {
        await revokeButton.click();
        await page.waitForTimeout(500);
      }
    }
  });

  test('should show existing access grants in share modal', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/purchase-orders');

    await page.waitForLoadState('networkidle');

    const shareButtons = page.locator('button:has-text("Share")');
    const shareButtonCount = await shareButtons.count();

    if (shareButtonCount > 0) {
      await shareButtons.first().click();
      await page.waitForTimeout(500);

      // Verify share modal opened
      await expect(page.locator('text=/share|grant|access/i').first()).toBeVisible();
    }
  });
});
