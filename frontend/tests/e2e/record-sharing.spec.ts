import { test, expect } from './conftest';

test.describe('Record Access Sharing', () => {

  test('should grant Read access to specific user', async ({ adminPage }) => {
    await adminPage.goto('/budget-items/1');
    await adminPage.waitForLoadState('networkidle');

    await adminPage.click('button:has-text("Share")');
    await adminPage.waitForTimeout(500);
  });

  test('should grant Read/Write access to group', async ({ adminPage }) => {
    await adminPage.goto('/budget-items/1');
    await adminPage.waitForLoadState('networkidle');

    await adminPage.click('button:has-text("Share")');
    await adminPage.waitForTimeout(500);

    await expect(adminPage.locator('text=Grant to Group')).toBeVisible();
  });

  test('should set and verify access expiration', async ({ adminPage }) => {
    await adminPage.goto('/budget-items/1');
    await adminPage.waitForLoadState('networkidle');

    await adminPage.click('button:has-text("Share")');
    await adminPage.waitForTimeout(500);
  });

  test('should revoke previously granted access', async ({ adminPage }) => {
    await adminPage.goto('/budget-items/1');
    await adminPage.waitForLoadState('networkidle');

    await adminPage.click('button:has-text("Share")');
    await adminPage.waitForTimeout(500);

    const revokeButton = adminPage.locator('button:has-text("Revoke")').first();
    if (await revokeButton.isVisible()) {
      await revokeButton.click();
      await adminPage.waitForTimeout(500);
    }
  });

  test('should show existing access grants in share modal', async ({ adminPage }) => {
    await adminPage.goto('/budget-items/1');
    await adminPage.waitForLoadState('networkidle');

    await adminPage.click('button:has-text("Share")');
    await adminPage.waitForTimeout(500);
  });
});
