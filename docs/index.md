# Ebrose (TechDocs)

Ebrose is a procurement and budget tracking system:

- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: Nuxt (Vue)
- Security: cookie-based auth, role-based access control, record sharing
- Compliance: audit log for CRUD changes

## Quick links

- Backend API reference: `docs/backend-api.md`
- Frontend pages: `docs/frontend-pages.md`
- Functional capabilities: `docs/functions.md`

## Current status

The repository contains working backend routers and a Nuxt UI with admin pages.

Planned evolution (in `requirements-codex.md`) includes Workday-style budget items and business-case line items; align the implementation to the updated spec before building the budget dashboard.
