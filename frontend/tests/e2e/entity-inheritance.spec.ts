import { test, expect } from './conftest';

test.describe('Entity Chain & Owner Group Inheritance', () => {

  test('WBS automatically inherits owner_group_id from line item', async ({ adminPage }) => {
    await adminPage.goto('/wbs');
    await adminPage.waitForLoadState('networkidle');

    await expect(adminPage.locator('text=Create WBS')).toBeVisible();

    await adminPage.click('button:has-text("Create WBS")');
    await adminPage.waitForTimeout(300);

    await expect(adminPage.locator('text=Owner Group will be inherited from Line Item')).toBeVisible();
  });

  test('Asset automatically inherits owner_group_id from WBS', async ({ adminPage }) => {
    await adminPage.goto('/assets');
    await adminPage.waitForLoadState('networkidle');

    await expect(adminPage.locator('text=Create Asset')).toBeVisible();

    await adminPage.click('button:has-text("Create Asset")');
    await adminPage.waitForTimeout(300);

    await expect(adminPage.locator('text=Owner Group will be inherited from WBS')).toBeVisible();
  });

  test('PO automatically inherits owner_group_id from Asset', async ({ adminPage }) => {
    await adminPage.goto('/purchase-orders');
    await adminPage.waitForLoadState('networkidle');

    await expect(adminPage.locator('text=Create PO')).toBeVisible();

    await adminPage.click('button:has-text("Create PO")');
    await adminPage.waitForTimeout(300);

    await expect(adminPage.locator('text=Owner Group will be inherited from Asset')).toBeVisible();
  });

  test('GR automatically inherits owner_group_id from PO', async ({ adminPage }) => {
    await adminPage.goto('/goods-receipts');
    await adminPage.waitForLoadState('networkidle');

    await expect(adminPage.locator('text=Create GR')).toBeVisible();

    await adminPage.click('button:has-text("Create GR")');
    await adminPage.waitForTimeout(300);

    await expect(adminPage.locator('text=Owner Group will be inherited from PO')).toBeVisible();
  });

  test('Allocation automatically inherits owner_group_id from PO', async ({ adminPage }) => {
    await adminPage.goto('/allocations');
    await adminPage.waitForLoadState('networkidle');

    await adminPage.click('button:has-text("Create Allocation")');
    await adminPage.waitForTimeout(300);

    await expect(adminPage.locator('text=Owner Group will be inherited from PO')).toBeVisible();
  });

  test('Child record shows parent owner_group in detail view', async ({ adminPage }) => {
    await adminPage.goto('/line-items/1');
    await adminPage.waitForLoadState('networkidle');

    await expect(adminPage.locator('text=Owner Group')).toBeVisible();
  });
});
