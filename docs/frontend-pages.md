# Frontend pages

Base URL (local): `http://localhost:3000`

## Public

- `/login` — login page.
- `/health` — frontend health/status page.

## Main

- `/` — dashboard (backend health + navigation).
- `/purchase-orders` — purchase orders list + record access modal.

## Admin

- `/admin/groups` — user group management.
- `/admin/audit` — audit log viewer.

## Shared UI building blocks

- `frontend/components/RecordAccessModal.vue` — grant/revoke record access to users/groups.
- `frontend/composables/useApiFetch.ts` — API helper (always includes cookies; refresh-on-401 behavior).
- `frontend/middleware/auth.global.ts` — route guard using `user_info` cookie.

