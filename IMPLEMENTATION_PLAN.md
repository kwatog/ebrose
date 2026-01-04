# Ebrose Implementation Plan

**Last Updated:** January 4, 2026

Based on the recommendations in `RECOMMENDATIONS.md` and updated requirements in `requirements-codex.md`, this plan tracks the implementation progress from MVP to production-ready state.

## 📊 Current State Summary

### Backend (FastAPI)
- **22 router files** with ~2,400 lines of code
- **58 tests** (55 passed, 2 skipped, 1 error)
- **All dependencies pinned** ✅

### Frontend (Nuxt 4)
- **15 pages** with ~6,500 lines of Vue code
- **84 unit tests passing** ✅
- **12 E2E test files** (need maintenance)

### Database
- **16 models** with proper relationships
- **All DateTime columns** using timezone-aware types
- **No Alembic migrations** yet

---

## 🎯 Priority Order

### 1. Testing (This Week)
- [ ] Audit and fix remaining E2E tests
- [ ] Add missing backend test coverage
- [ ] Fix test_admin_can_access_all_groups error (duplicate user)

### 2. Production Readiness (Next Week)
- [ ] Setup Alembic migrations
- [ ] Add missing database constraints
- [ ] Add frontend password strength to registration
- [ ] Configure production CORS/logging

---

## ✅ Completed Items (Jan 2, 2026)

### Access Control
- [x] RecordAccess role-caps (Viewers cannot receive Write/Full)
- [x] BusinessCase delete hybrid access check
- [x] Creator audit-only access (Read)
- [x] lead_group_id enforcement
- [x] Owner-group filtering on all list endpoints
- [x] Missing user-groups PUT/DELETE endpoints
- [x] Alerts scoped to user access

### Auth Enhancements
- [x] Password policy enforcement
- [x] /auth/password endpoint
- [x] /auth/me PUT endpoint
- [x] Password validation on registration

### Tests
- [x] 6 new auth tests (13 total)
- [x] 3 new access control tests (36 total backend tests)
- [x] Updated BusinessCase hybrid access tests
- [x] Alerts access control test

## ✅ Completed Items (Jan 4, 2026)

### Technical Debt Resolved
- [x] DateTime migration - All timestamp columns converted from String(32) to DateTime(timezone=True)
- [x] Deprecated datetime.utcnow() - Fixed 60+ instances to use datetime.now(timezone.utc)
- [x] Deprecated SQLAlchemy query.get() - Replaced with db.get(Model, id)
- [x] Deprecated @app.on_event - Converted to lifespan context manager
- [x] python-jose version fix - Pinned to 3.3.0
- [x] Dependencies pinning - All pinned in requirements.txt and package.json
- [x] v-model.number fix - Removed from ID fields, only fiscal_year uses it
- [x] Print statements removed - Replaced with proper logging
- [x] CORS security - Uses secure=IS_PRODUCTION
- [x] Frontend unit tests fixed - 84 tests passing
- [x] Database reset path fix - reset_and_seed.py now uses correct path

### E2E Tests
- [x] Made corporate certificate optional in run-playwright-tests.sh
- [x] access-control-ui.spec.ts created with 8 test scenarios

### Documentation
- [x] Created generic AI agent instructions (agents.md)
- [x] Renamed AGENTS.md to SETUP.md for clarity
- [x] Git history cleanup - Removed AI attribution footers
