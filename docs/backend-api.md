# Backend API

Base URL (local): `http://localhost:8000`

## Health

- `GET /health` — service health check.

## Authentication (`/auth`)

- `POST /auth/login` — login, sets cookies.
- `POST /auth/refresh` — refresh access token cookie.
- `POST /auth/logout` — clear cookies.
- `GET /auth/me` — current user.
- `POST /auth/register` — create user (Admin only).

## Users (`/users`)

- `GET /users/` — list users.
- `GET /users/{user_id}` — get user.
- `PUT /users/{user_id}` — update user.
- `DELETE /users/{user_id}` — delete user.

## User groups (`/user-groups`)

- `GET /user-groups/` — list groups.
- `POST /user-groups/` — create group.
- `GET /user-groups/{group_id}/members` — list group members.
- `POST /user-groups/{group_id}/members` — add member.
- `DELETE /user-groups/{group_id}/members/{user_id}` — remove member.

## Record access grants (`/record-access`)

- `GET /record-access/{record_type}/{record_id}` — list access grants.
- `POST /record-access/` — create grant.
- `PUT /record-access/{access_id}` — update grant.
- `DELETE /record-access/{access_id}` — delete grant.

## Audit logs (`/audit-logs`)

- `GET /audit-logs/` — list audit entries.
- `GET /audit-logs/{record_type}/{record_id}` — audit entries for record.

## Procurement entities

Business cases (`/business-cases`)

- `GET /business-cases/` — list.
- `GET /business-cases/{bc_id}` — get.
- `POST /business-cases/` — create.
- `DELETE /business-cases/{bc_id}` — delete.

WBS (`/wbs`)

- `GET /wbs/` — list.
- `GET /wbs/{wbs_id}` — get.
- `POST /wbs/` — create.
- `DELETE /wbs/{wbs_id}` — delete.

Assets (`/assets`)

- `GET /assets/` — list.
- `GET /assets/{asset_id}` — get.
- `POST /assets/` — create.
- `DELETE /assets/{asset_id}` — delete.

Purchase orders (`/purchase-orders`)

- `GET /purchase-orders/` — list.
- `GET /purchase-orders/{po_id}` — get.
- `POST /purchase-orders/` — create.
- `PUT /purchase-orders/{po_id}` — update.
- `DELETE /purchase-orders/{po_id}` — delete.

Goods receipts (`/goods-receipts`)

- `GET /goods-receipts/` — list.
- `GET /goods-receipts/{gr_id}` — get.
- `POST /goods-receipts/` — create.
- `DELETE /goods-receipts/{gr_id}` — delete.

Resources (`/resources`)

- `GET /resources/` — list.
- `GET /resources/{resource_id}` — get.
- `POST /resources/` — create.
- `DELETE /resources/{resource_id}` — delete.

Allocations (`/allocations`)

- `GET /allocations/` — list.
- `GET /allocations/{alloc_id}` — get.
- `POST /allocations/` — create.
- `DELETE /allocations/{alloc_id}` — delete.

## Alerts (`/alerts`)

- `GET /alerts/` — computed alerts.

## Notes

- Most routes require authentication; see Swagger at `GET /docs`.
- Current list routes generally return all records; access scoping is evolving.

