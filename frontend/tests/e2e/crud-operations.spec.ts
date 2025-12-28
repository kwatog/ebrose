import { test, expect } from '@playwright/test';

test.describe('CRUD Operations', () => {
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

    // Login
    await page.goto('/login');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
  });

  test('should create, edit, and delete a resource', async ({ page }) => {
    let resources = [];

    // Mock groups
    await page.route('**/groups', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, name: 'Finance' }
        ])
      });
    });

    // Mock resources API
    await page.route('**/resources', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(resources)
        });
      } else if (route.request().method() === 'POST') {
        const newResource = {
          id: 1,
          name: 'John Doe',
          vendor: 'Acme Corp',
          role: 'Developer',
          cost_per_month: 10000,
          owner_group_id: 1,
          status: 'Active',
          created_by: 1
        };
        resources.push(newResource);
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(newResource)
        });
      } else if (route.request().method() === 'DELETE') {
        resources = [];
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ message: 'Deleted' })
        });
      }
    });

    // Mock PUT for edit
    await page.route('**/resources/*', async route => {
      if (route.request().method() === 'PUT') {
        resources[0].name = 'Jane Doe';
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(resources[0])
        });
      }
    });

    await page.goto('/resources');

    // CREATE
    await page.click('button:has-text("Create Resource")');
    await page.fill('input[placeholder*="Resource name"]', 'John Doe');
    await page.fill('input[placeholder*="Vendor"]', 'Acme Corp');
    await page.fill('input[placeholder*="Developer"]', 'Developer');
    await page.fill('input[type="number"]', '10000');
    await page.selectOption('select[required]', '1');
    await page.click('button:has-text("Create")');

    // Verify created
    await page.reload();
    await expect(page.locator('text=John Doe')).toBeVisible();

    // EDIT
    await page.click('button:has-text("Edit")');
    await page.fill('input[value="John Doe"]', 'Jane Doe');
    await page.click('button:has-text("Update")');

    // DELETE
    page.on('dialog', dialog => dialog.accept());
    await page.click('button:has-text("Delete")');
  });

  test('should show validation errors on empty required fields', async ({ page }) => {
    await page.route('**/groups', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([{ id: 1, name: 'Finance' }])
      });
    });

    await page.route('**/budget-items', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await page.goto('/budget-items');
    await page.click('button:has-text("Create Budget Item")');

    // Try to submit without filling required fields
    await page.click('button:has-text("Create")');

    // Should show alert or validation message
    // Note: Current implementation uses alert(), which Playwright can catch with dialog events
  });

  test('should navigate through entity chain', async ({ page }) => {
    // Mock all required APIs
    const mockApis = async () => {
      await page.route('**/budget-items', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([{ id: 1, workday_ref: 'WD-001', title: 'Budget', budget_amount: 100000, fiscal_year: 2025, owner_group_id: 1 }])
        });
      });

      await page.route('**/business-cases', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([{ id: 1, title: 'BC-001', status: 'Draft', owner_group_id: 1 }])
        });
      });

      await page.route('**/business-case-line-items', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([{ id: 1, business_case_id: 1, budget_item_id: 1, title: 'Line Item', owner_group_id: 1 }])
        });
      });

      await page.route('**/wbs', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([{ id: 1, business_case_line_item_id: 1, wbs_code: 'WBS-001', owner_group_id: 1 }])
        });
      });

      await page.route('**/assets', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([{ id: 1, wbs_id: 1, asset_code: 'ASSET-001', owner_group_id: 1 }])
        });
      });
    };

    await mockApis();

    // Navigate through chain
    await page.goto('/budget-items');
    await expect(page.locator('text=WD-001')).toBeVisible();

    await page.goto('/business-cases');
    await expect(page.locator('text=BC-001')).toBeVisible();

    await page.goto('/line-items');
    await expect(page.locator('text=Line Item')).toBeVisible();

    await page.goto('/wbs');
    await expect(page.locator('text=WBS-001')).toBeVisible();

    await page.goto('/assets');
    await expect(page.locator('text=ASSET-001')).toBeVisible();
  });
});
