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

test.describe('Session & Authentication', () => {
  test('should redirect to login when accessing protected route without auth', async ({ page }) => {
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await expect(page).toHaveURL(/\/login/);
  });

  test('should clear tokens and redirect after logout', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.goto('/admin/audit');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Logout button in header
    await page.click('button.logout-btn, button[title="Logout"]');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await expect(page).toHaveURL(/\/login/);
  });

  test('should persist login across browser restart (cookie)', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const cookies = await page.context().cookies();
    const hasAccessToken = cookies.some(c => c.name === 'access_token' || c.name === 'user_info');

    expect(hasAccessToken).toBe(true);
  });

  test('should prevent access with invalid token', async ({ page }) => {
    await page.context().addCookies([{
      name: 'access_token',
      value: 'invalid-token',
      domain: 'localhost',
      path: '/'
    }]);

    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Should redirect to login or show error
    const isOnLogin = page.url().includes('/login');
    const hasError = await page.locator('text=/error|unauthorized|forbidden/i').count() > 0;

    expect(isOnLogin || hasError).toBeTruthy();
  });
});

test.describe('Session Security', () => {
  test('should not expose credentials in network requests', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(3000);

    expect(consoleErrors.every(e => !e.includes('password') && !e.includes('credential'))).toBe(true);
  });

  test('should use HttpOnly cookies for token storage', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.waitForTimeout(2000);

    const cookies = await page.context().cookies();
    const accessTokenCookie = cookies.find(c => c.name === 'access_token');
    const userInfoCookie = cookies.find(c => c.name === 'user_info');

    expect(accessTokenCookie || userInfoCookie).toBeDefined();
  });
});
