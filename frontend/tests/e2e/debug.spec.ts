import { test, expect } from '@playwright/test';

test.describe('API Connectivity Debug', () => {
  test('should be able to call login API', async ({ page }) => {
    const responses: string[] = [];

    page.on('response', async (response) => {
      if (response.url().includes('/auth/login')) {
        responses.push(`${response.status()}: ${await response.text()}`);
      }
    });

    await page.goto('/login');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('button[type="submit"]');

    await page.waitForTimeout(3000);

    console.log('Responses:', responses);
  });
});
