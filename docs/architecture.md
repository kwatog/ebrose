# Architecture

## High-level

- **Frontend** (Nuxt): UI pages and admin tools.
- **Backend** (FastAPI): JSON API, auth, access control, audit logging.
- **Database** (SQLite): single-file database used by the backend.

## Repository layout

- `backend/app/main.py`: FastAPI app, router registration, CORS.
- `backend/app/models.py`: SQLAlchemy models.
- `backend/app/schemas.py`: Pydantic schemas.
- `backend/app/auth.py`: authentication + authorization helpers.
- `backend/app/routers/*`: entity routers.
- `frontend/pages/*`: Nuxt routes/pages.
- `frontend/components/*`: reusable components.
- `frontend/composables/*`: shared API helpers.

## Security model (as implemented today)

- Cookie-based authentication (`access_token` HttpOnly + `user_info` readable cookie).
- Role levels: Viewer < User < Manager < Admin.
- Record sharing via `RecordAccess` for per-user or per-group grants.

Note: `requirements-codex.md` has newer ownership semantics (group-owned records and line-item budgeting). Align code to the spec before relying on access rules for production use.

