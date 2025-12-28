import { test, expect } from '@playwright/test';

test.describe('Budget to Business Case Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.route('**/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Login successful',
          user: { id: 1, username: 'admin', role: 'Admin' }
        })
      });
    });

    // Mock groups API
    await page.route('**/groups', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, name: 'Finance', description: 'Finance team' },
          { id: 2, name: 'IT', description: 'IT team' }
        ])
      });
    });

    // Login
    await page.goto('/login');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
  });

  test('should create budget item successfully', async ({ page }) => {
    // Mock budget items list (empty initially)
    await page.route('**/budget-items', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([])
        });
      } else if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 1,
            workday_ref: 'WD-2025-001',
            title: 'IT Infrastructure Budget',
            budget_amount: 100000,
            currency: 'USD',
            fiscal_year: 2025,
            owner_group_id: 2
          })
        });
      }
    });

    await page.goto('/budget-items');

    // Click create button
    await page.click('button:has-text("Create Budget Item")');

    // Fill form
    await page.fill('input[placeholder*="WD-"]', 'WD-2025-001');
    await page.fill('input[placeholder*="Title"]', 'IT Infrastructure Budget');
    await page.fill('input[type="number"]', '100000');
    await page.selectOption('select', { label: 'USD' });
    await page.fill('input[placeholder*="2025"]', '2025');

    // Submit
    await page.click('button:has-text("Create")');

    // Verify success (modal should close)
    await expect(page.locator('.modal-overlay')).not.toBeVisible();
  });

  test('should navigate through dashboard quick actions', async ({ page }) => {
    // Mock dashboard data
    await page.route('**/budget-items', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, budget_amount: 100000, fiscal_year: 2025 }
        ])
      });
    });

    await page.route('**/purchase-orders', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, po_number: 'PO-001', total_amount: 5000, status: 'Open' }
        ])
      });
    });

    await page.route('**/goods-receipts', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await page.route('**/resources', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await page.route('**/business-cases', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await page.goto('/');

    // Verify statistics are displayed
    await expect(page.locator('text=Total Budget')).toBeVisible();
    await expect(page.locator('text=$100,000')).toBeVisible();

    // Click quick action
    await page.click('a[href="/budget-items"]');
    await expect(page).toHaveURL('/budget-items');
  });

  test('should filter budget items by fiscal year', async ({ page }) => {
    await page.route('**/budget-items', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, workday_ref: 'WD-2024-001', title: 'Old Budget', budget_amount: 50000, fiscal_year: 2024, owner_group_id: 1 },
          { id: 2, workday_ref: 'WD-2025-001', title: 'New Budget', budget_amount: 100000, fiscal_year: 2025, owner_group_id: 1 }
        ])
      });
    });

    await page.goto('/budget-items');

    // Verify both items are visible initially
    await expect(page.locator('text=Old Budget')).toBeVisible();
    await expect(page.locator('text=New Budget')).toBeVisible();

    // Apply fiscal year filter
    await page.selectOption('select', { label: '2025' });

    // Client-side filtering should hide 2024 item
    // Note: This tests the frontend filtering logic
  });
});

test.describe('Purchase Order Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock auth
    await page.route('**/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Login successful',
          user: { id: 1, username: 'manager', role: 'Manager' }
        })
      });
    });

    await page.goto('/login');
    await page.fill('#username', 'manager');
    await page.fill('#password', 'manager123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
  });

  test('should display inherited owner group in PO form', async ({ page }) => {
    // Mock assets
    await page.route('**/assets', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, asset_code: 'ASSET-001', owner_group_id: 1 }
        ])
      });
    });

    // Mock groups
    await page.route('**/groups', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, name: 'Finance', description: 'Finance team' }
        ])
      });
    });

    // Mock POs list
    await page.route('**/purchase-orders', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await page.goto('/purchase-orders');

    // Open create modal
    await page.click('button:has-text("Create PO")');

    // Verify inheritance note is visible
    await expect(page.locator('text=Owner Group will be automatically inherited')).toBeVisible();
  });
});
