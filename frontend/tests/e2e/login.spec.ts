import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
  test('should login successfully', async ({ page }) => {
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

  test('should show error on failed login', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('#username', 'wronguser');
    await page.fill('#password', 'wrongpass');
    await page.click('button[type="submit"]');

    await expect(page.locator('.error-message')).toContainText('Incorrect username or password', { timeout: 5000 });
    await expect(page).toHaveURL('/login');
  });
});
