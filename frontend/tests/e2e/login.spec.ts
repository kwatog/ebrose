import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
  test('should login successfully with admin credentials', async ({ page }) => {
    const responses: string[] = [];

    page.on('response', async (response) => {
      if (response.url().includes('/auth/login')) {
        responses.push(`${response.status()}`);
      }
    });

    await page.goto('/login');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('button[type="submit"]');

    await page.waitForTimeout(2000);

    expect(responses).toContain('200');
  });

  test('should show error on failed login with wrong credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('#username', 'wronguser');
    await page.fill('#password', 'wrongpass');
    await page.click('button[type="submit"]');

    await expect(page.locator('.error-message')).toContainText('Incorrect username or password', { timeout: 5000 });
    await expect(page).toHaveURL('/login');
  });

  test('admin user should see admin navigation items', async ({ adminPage }) => {
    await adminPage.goto('/');

    await expect(adminPage.locator('text=Admin Panel')).toBeVisible({ timeout: 10000 });
  });

  test('manager user should not see admin navigation items', async ({ managerPage }) => {
    await managerPage.goto('/');

    await expect(managerPage.locator('text=Admin Panel')).not.toBeVisible({ timeout: 5000 });
  });

  test('regular user should not see admin navigation items', async ({ userPage }) => {
    await userPage.goto('/');

    await expect(userPage.locator('text=Admin Panel')).not.toBeVisible({ timeout: 5000 });
  });
});
