import { test, expect } from '@playwright/test';

async function loginAs(page, username, password) {
  await page.goto('/login');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000); // Wait for hydration
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');

  try {
    await page.waitForURL('**/', { timeout: 10000 });
  } catch (e) {
    await page.goto('/');
  }

  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000); // Wait for dashboard to load
}

test.describe('Login Flow', () => {
  test('should login successfully with admin credentials', async ({ page }) => {
    let loginSucceeded = false;
    page.on('response', async (response) => {
      if (response.url().includes('/auth/login') && response.status() === 200) {
        loginSucceeded = true;
      }
    });

    await loginAs(page, 'admin', 'admin123');
    await page.waitForTimeout(1000);

    expect(loginSucceeded).toBe(true);
    expect(page.url()).not.toContain('/login');
  });

  test('should show error on failed login with wrong credentials', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await page.fill('#username', 'wronguser');
    await page.fill('#password', 'wrongpass');
    await page.click('button[type="submit"]');

    await page.waitForTimeout(3000);

    // Should stay on login page after failed attempt
    await expect(page).toHaveURL('/login');
  });

  test('admin user should see admin navigation items', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');

    // Admin nav is in dropdown - hover to see it
    await page.locator('button.nav-link:has-text("Admin")').hover();
    await page.waitForTimeout(500);

    await expect(page.locator('text=User Groups')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=Audit Logs')).toBeVisible({ timeout: 5000 });
  });

  test('manager user should see admin navigation items', async ({ page }) => {
    await loginAs(page, 'manager', 'manager123');

    // Admin nav is in dropdown - hover to see it
    await page.locator('button.nav-link:has-text("Admin")').hover();
    await page.waitForTimeout(500);

    await expect(page.locator('text=User Groups')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=Audit Logs')).toBeVisible({ timeout: 5000 });
  });

  test('regular user should not see admin navigation items', async ({ page }) => {
    await loginAs(page, 'user', 'user123');

    await expect(page.locator('button.nav-link:has-text("Admin")')).not.toBeVisible({ timeout: 5000 });
  });
});
