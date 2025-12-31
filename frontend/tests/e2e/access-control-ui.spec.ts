import { test, expect } from '@playwright/test';

test.describe('Access Control UI Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Create screenshots directory if it doesn't exist
    await page.goto('/');
  });

  test('Admin user can see all budget items', async ({ page }) => {
    // Mock admin login
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

    // Mock budget items list (admin sees all)
    await page.route('**/budget-items*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            workday_ref: 'WD-001',
            title: 'Budget from Group A',
            budget_amount: 100000,
            currency: 'USD',
            fiscal_year: 2025,
            owner_group_id: 1
          },
          {
            id: 2,
            workday_ref: 'WD-002',
            title: 'Budget from Group B',
            budget_amount: 200000,
            currency: 'USD',
            fiscal_year: 2025,
            owner_group_id: 2
          }
        ])
      });
    });

    // Login
    await page.goto('/login');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to budget items
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');

    // Take screenshot
    await page.screenshot({
      path: 'tests/screenshots/admin-sees-all-budgets.png',
      fullPage: true
    });

    // Verify both items are visible
    await expect(page.locator('text=WD-001')).toBeVisible();
    await expect(page.locator('text=WD-002')).toBeVisible();
  });

  test('Regular user only sees accessible budget items', async ({ page }) => {
    // Mock regular user login
    await page.route('**/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Login successful',
          user: { id: 2, username: 'regularuser', role: 'User' }
        })
      });
    });

    // Mock budget items list (filtered by access)
    await page.route('**/budget-items*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            workday_ref: 'WD-001',
            title: 'Budget from My Group',
            budget_amount: 100000,
            currency: 'USD',
            fiscal_year: 2025,
            owner_group_id: 1
          }
          // WD-002 is not accessible, so it's filtered out
        ])
      });
    });

    // Login
    await page.goto('/login');
    await page.fill('#username', 'regularuser');
    await page.fill('#password', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to budget items
    await page.goto('/budget-items');
    await page.waitForLoadState('networkidle');

    // Take screenshot
    await page.screenshot({
      path: 'tests/screenshots/user-filtered-budgets.png',
      fullPage: true
    });

    // Verify only accessible item is visible
    await expect(page.locator('text=WD-001')).toBeVisible();
    await expect(page.locator('text=WD-002')).not.toBeVisible();
  });

  test('User denied access to specific budget item', async ({ page }) => {
    // Mock regular user login
    await page.route('**/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Login successful',
          user: { id: 2, username: 'regularuser', role: 'User' }
        })
      });
    });

    // Mock 403 response for budget item detail
    await page.route('**/budget-items/999', async route => {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Insufficient Read access to BudgetItem 999'
        })
      });
    });

    // Login
    await page.goto('/login');
    await page.fill('#username', 'regularuser');
    await page.fill('#password', 'password123');
    await page.click('button[type="submit"]');

    // Try to access denied budget item
    await page.goto('/budget-items/999');
    await page.waitForLoadState('networkidle');

    // Take screenshot
    await page.screenshot({
      path: 'tests/screenshots/access-denied-403.png',
      fullPage: true
    });

    // Verify error message is shown
    await expect(page.locator('text=/403|Forbidden|access denied/i')).toBeVisible();
  });

  test('Business case hybrid access - creator view', async ({ page }) => {
    // Mock regular user login
    await page.route('**/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Login successful',
          user: { id: 2, username: 'regularuser', role: 'User' }
        })
      });
    });

    // Mock business cases list (creator sees their own)
    await page.route('**/business-cases*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            title: 'My Draft Business Case',
            description: 'Created by me',
            status: 'Draft',
            created_by: 2,
            created_at: new Date().toISOString()
          }
        ])
      });
    });

    // Login
    await page.goto('/login');
    await page.fill('#username', 'regularuser');
    await page.fill('#password', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to business cases
    await page.goto('/business-cases');
    await page.waitForLoadState('networkidle');

    // Take screenshot
    await page.screenshot({
      path: 'tests/screenshots/bc-creator-access.png',
      fullPage: true
    });

    // Verify creator can see their BC
    await expect(page.locator('text=My Draft Business Case')).toBeVisible();
  });

  test('Business case status transition validation', async ({ page }) => {
    // Mock regular user login
    await page.route('**/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Login successful',
          user: { id: 2, username: 'regularuser', role: 'User' }
        })
      });
    });

    // Mock business case detail
    await page.route('**/business-cases/1', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 1,
            title: 'Empty Draft BC',
            description: 'No line items yet',
            status: 'Draft',
            created_by: 2,
            created_at: new Date().toISOString()
          })
        });
      } else if (route.request().method() === 'PUT') {
        // Mock 400 error when trying to transition without line items
        await route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: 'Cannot transition from Draft status without at least one line item'
          })
        });
      }
    });

    // Login
    await page.goto('/login');
    await page.fill('#username', 'regularuser');
    await page.fill('#password', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to business case edit
    await page.goto('/business-cases/1/edit');
    await page.waitForLoadState('networkidle');

    // Try to change status to Submitted
    await page.selectOption('select[name="status"]', 'Submitted');
    await page.click('button:has-text("Save")');

    // Wait for error
    await page.waitForTimeout(1000);

    // Take screenshot
    await page.screenshot({
      path: 'tests/screenshots/bc-transition-validation-error.png',
      fullPage: true
    });

    // Verify error message
    await expect(page.locator('text=/line item/i')).toBeVisible();
  });

  test('User groups management - Admin view', async ({ page }) => {
    // Mock admin login
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

    // Mock groups list
    await page.route('**/user-groups*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            name: 'Engineering Team',
            description: 'Engineering department group',
            created_by: 1
          },
          {
            id: 2,
            name: 'Finance Team',
            description: 'Finance department group',
            created_by: 1
          }
        ])
      });
    });

    // Login
    await page.goto('/login');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to user groups management
    await page.goto('/admin/groups');
    await page.waitForLoadState('networkidle');

    // Take screenshot
    await page.screenshot({
      path: 'tests/screenshots/admin-user-groups.png',
      fullPage: true
    });

    // Verify groups are visible
    await expect(page.locator('text=Engineering Team')).toBeVisible();
    await expect(page.locator('text=Finance Team')).toBeVisible();
  });

  test('Dashboard health check display', async ({ page }) => {
    // Mock admin login
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

    // Mock health check
    await page.route('**/health', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'healthy',
          database: 'connected',
          timestamp: new Date().toISOString()
        })
      });
    });

    // Login
    await page.goto('/login');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'password123');
    await page.click('button[type="submit"]');

    // Should be on dashboard
    await page.waitForLoadState('networkidle');

    // Take screenshot
    await page.screenshot({
      path: 'tests/screenshots/dashboard-health-check.png',
      fullPage: true
    });

    // Verify health status
    await expect(page.locator('text=/healthy|connected/i')).toBeVisible();
  });

  test('Access sharing modal - record level permissions', async ({ page }) => {
    // Mock admin login
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

    // Mock budget item detail
    await page.route('**/budget-items/1', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          workday_ref: 'WD-001',
          title: 'Shareable Budget',
          budget_amount: 100000,
          currency: 'USD',
          fiscal_year: 2025,
          owner_group_id: 1,
          created_by: 1
        })
      });
    });

    // Mock record access grants list
    await page.route('**/record-access?record_type=BudgetItem&record_id=1', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            record_type: 'BudgetItem',
            record_id: 1,
            user_id: 2,
            access_level: 'Read',
            granted_by: 1
          }
        ])
      });
    });

    // Login
    await page.goto('/login');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to budget item
    await page.goto('/budget-items/1');
    await page.waitForLoadState('networkidle');

    // Click share button
    await page.click('button:has-text("Share")');
    await page.waitForTimeout(500);

    // Take screenshot
    await page.screenshot({
      path: 'tests/screenshots/access-sharing-modal.png',
      fullPage: true
    });

    // Verify modal is visible
    await expect(page.locator('text=/Share Access|Grant Access/i')).toBeVisible();
  });
});
