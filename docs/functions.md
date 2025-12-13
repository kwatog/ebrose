# Functions (capabilities)

This is a user-facing catalog of what the system does today.

## Authentication

- Login/logout with HttpOnly cookie-based sessions.
- Token refresh endpoint for silent re-auth.
- Current-user identity endpoint.

## User and group management

- Create and manage user groups.
- Add/remove users from groups.

## Record access sharing

- Grant record access to a specific user or group.
- Set access levels: `Read`, `Write`, `Full`.
- Optional expiry for temporary grants.

## Procurement tracking

- Business cases, WBS, assets.
- Purchase orders with total amount + status.
- Goods receipts recorded against a PO.
- Resource tracking and PO allocations.

## Audit and compliance

- Audit log entries recorded for create/update/delete actions.
- Audit log viewer in the admin UI.

## Alerts

- Computed alerts endpoint (low balance, missing receipts, missing chain, etc.).

## Planned (requirements)

In `requirements-codex.md`, the next major capability is a Workday-style budget dashboard:

- Workday budget item tracking.
- Business case line items tied to budget items.
- Planned vs actual PO commit dates.
- CAPEX/OPEX categorization and rollups.

