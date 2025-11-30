# Mazarbul Code Review and Improvements

This document captures a focused review of `requirements-codex.md` and the current codebase, with concrete, high‑impact recommendations.

## Biggest Gaps
- Record access revoke/update: Frontend calls `DELETE /record-access/{id}`, but backend lacks it. Add `DELETE /record-access/{id}` and `PUT /record-access/{id}` in `backend/app/routers/record_access.py`.
- CRUD completeness: Routers mostly expose list/get/create/delete. Add update endpoints across all entities and audit logging for UPDATE.
- Auth token handling: Spec calls for HTTP‑only cookies + refresh. Current flow returns token JSON and stores a readable cookie. Implement HttpOnly `Set-Cookie` on login, add refresh endpoint, and client retry on 401.

## Security
- Secrets: `backend/app/auth.py` hardcodes `SECRET_KEY`. Read `SECRET_KEY` and `ACCESS_TOKEN_EXPIRE_MINUTES` from env; fail fast if missing outside dev.
- CORS + credentials: `allow_origins=["*"]` with credentials is unsafe/invalid. Drive allowlist from `ALLOWED_ORIGINS` env; disable credentials for wildcard.
- Token storage: Use HttpOnly, Secure cookies (SameSite=Lax/Strict) set by backend instead of client-set cookies. Avoid exposing tokens to JS.
- Default admin: Startup creates `admin/Admin123!` and prints it. Replace with env‑driven bootstrap (or disable by default) and never log secrets.

## Access Control
- Department access & inheritance: Implement department scoping for `User` role and inheritance BC → WBS → Asset → PO → GR in all reads/writes. List endpoints currently return all rows to any authenticated user.
- Centralize checks: Provide a utility to compute effective access (role, creator, group/user grants, department) to eliminate duplication and drift.

## Audit Trail
- Update coverage: Decorator logs CREATE/DELETE only and does not capture `old_values`. For UPDATE/DELETE, fetch record before change; for UPDATE, store both old/new (consider diffs to reduce noise).
- Request context: Capture `ip_address` and `user_agent` consistently by passing FastAPI `Request` into the audit decorator or using middleware.
- Naming consistency: Ensure `record_type` and audit `table_name` match actual tables/entities consistently.

## Backend Engineering
- Datetimes: Store timestamps as `DateTime` (not strings); same for `expires_at`. String comparisons are brittle.
- Constraints: Add DB constraints matching the spec:
  - `user_group_membership`: unique `(user_id, group_id)` via `UniqueConstraint`.
  - `record_access`: check `(user_id IS NOT NULL OR group_id IS NOT NULL)`.
- Pagination/filtering: Add `limit`, `offset`, and basic filters to list endpoints; avoid returning entire tables.
- Migrations: Introduce Alembic for schema evolution instead of `Base.metadata.create_all`.
- SQLAlchemy API: Replace deprecated `query.get(id)` with `session.get(Model, id)` for 2.x compatibility.

## Frontend
- Auth flow: Centralize API calls with a composable/plugin to inject Authorization and handle 401 → refresh → retry. Remove per-component header plumbing.
- Role guards: Use route middleware for role‑gated routes (e.g., `/admin/...`); continue to enforce on the backend.
- Health endpoint: Keep `pages/health.vue`; consider a lightweight Nitro server route (`server/api/health.get.ts`) returning JSON for probes.
- UX coverage: Add PO detail with GRs and remaining calculation, an alerts page consuming `/alerts`, and inline editing for CRUD completeness.

## DevOps/CI/CD
- Helm chart: `helm/mazarbul/templates` is empty. Add Deployments, Services, Ingress, ConfigMaps/Secrets, and optional PVC for SQLite. Wire values from `values-*.yaml`.
- Config as env: Backend should read `DATABASE_URL`, `ALLOWED_ORIGINS`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`. Frontend already uses `NUXT_API_BASE` variants.
- Jenkinsfile: Solid structure, but it assumes a working Helm chart. Add templates or make the pipeline fail fast with clear messaging when templates are missing.
- Artifacts: `mazarbul.db` is committed. Remove it from repo; `.gitignore` already covers future DB files.

## Data Model
- Required fields: Enforce NOT NULL where implied (e.g., `po_number`, dates). Add indexes for frequent lookups (`po_number`, `wbs_code`, `asset_code`).
- Money handling: Consider `Decimal` for amounts to avoid float rounding issues; validate known currency set.

## Testing and Quality
- Minimal tests: Auth (happy/negative), access control for one entity, audit logging on create/update/delete, alerts edge cases.
- Lint/type checks: Add ruff/black/mypy for backend; ESLint/TypeScript strict for frontend. Integrate into Jenkins as fast‑fail steps.

## Quick Wins
- Env‑driven secrets and CORS in `auth.py` and `main.py`.
- Add `DELETE /record-access/{id}` and `PUT /record-access/{id}` to match frontend.
- Implement UPDATE + audit for one entity (e.g., PurchaseOrder) as a reference pattern.
- Add `UniqueConstraint` to `UserGroupMembership`; confirm duplicate handling.
- Add `limit`/`offset` and default sorting to list endpoints.

## Suggested Next Steps
1. Patch record access DELETE/PUT and fix CORS/secret env reading.
2. Add UPDATE endpoints + audit for PurchaseOrder and propagate to other entities.
3. Implement HttpOnly cookie login + refresh endpoint; add frontend retry on 401.
4. Introduce pagination on list endpoints; add basic filters.
5. Scaffold Helm templates for backend/frontend and wire Jenkins to validate charts.

