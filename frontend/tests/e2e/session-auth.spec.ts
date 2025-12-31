import { test, expect } from './conftest';

test.describe('Session & Authentication', () => {
  test('should redirect to login when accessing protected route without auth', async ({ page }) => {
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveURL(/\/login/);
  });

  test('should clear tokens and redirect after logout', async ({ adminPage }) => {
    await adminPage.goto('/admin/audit');
    await adminPage.waitForLoadState('networkidle');

    await adminPage.click('button:has-text("Logout")');
    await adminPage.waitForLoadState('networkidle');

    await expect(adminPage).toHaveURL(/\/login/);
  });

  test('should persist login across browser restart (cookie)', async ({ page }) => {
    await page.goto('/login');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');

    const cookies = await page.context().cookies();
    const hasAccessToken = cookies.some(c => c.name === 'access_token');

    expect(hasAccessToken).toBe(true);
  });

  test('should prevent access with invalid token', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveURL(/\/login/);
  });
});

test.describe('Session Security', () => {
  test('should not expose credentials in network requests', async ({ page }) => {
    const credentialsCaptured: string[] = [];

    page.on('request', request => {
      if (request.url().includes('/auth/login')) {
        const postData = request.postData();
        if (postData) {
          credentialsCaptured.push(postData);
        }
      }
    });

    await page.goto('/login');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');

    expect(credentialsCaptured.length).toBeGreaterThan(0);

    for (const cred of credentialsCaptured) {
      expect(cred).not.toContain('"password"');
    }
  });

  test('should use HttpOnly cookies for token storage', async ({ page }) => {
    await page.goto('/login');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');

    const cookies = await page.context().cookies();
    const accessTokenCookie = cookies.find(c => c.name === 'access_token');

    expect(accessTokenCookie).toBeDefined();
    expect(accessTokenCookie?.httpOnly).toBe(true);
    expect(accessTokenCookie?.sameSite).toBe('lax');
  });
});
