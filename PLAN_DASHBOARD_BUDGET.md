# Dashboard Budget Scope Plan

Goal: Make dashboard budget scope explicit by group and show current vs previous year budgets (calendar year). Spend should be based on PurchaseOrder.planned_commit_date.

## Steps
- [x] 1. Add `User.primary_group_id` (model, schema, migration), include in auth cookie, and expose in admin user management.
- [x] 2. Add backend dashboard summary endpoint that returns group options and year-scoped totals (budget + spend by planned commit date).
- [x] 3. Update dashboard UI to select group (default to primary group), show current vs previous year budgets, and scope spend/utilization to current year.
- [x] 4. Update seed data and tests to cover primary group and dashboard behavior.

## Progress Log
- Initialized plan.
- Step 1 complete: added `primary_group_id`, migration, cookie field, admin UI controls, and seed/test updates.
- Synced with remote (fetch + merge `origin/main`).
- Step 2 complete: added `/dashboard/summary` endpoint with group/year-scoped totals.
- Step 3 complete: dashboard UI now scopes by group and shows current vs previous year budgets and utilization.
- Step 4 complete: seed data updated for primary group; dashboard summary test added.
