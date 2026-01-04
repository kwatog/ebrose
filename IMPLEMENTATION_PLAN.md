# Ebrose Implementation Plan

**Last Updated:** January 4, 2026

Based on the recommendations in `RECOMMENDATIONS.md` and updated requirements in `requirements-codex.md`, this plan tracks the implementation progress from MVP to production-ready state.

## 🔴 Critical Issues (Security & Data Integrity)

### 1. Frontend v-model.number Regression
**Status:** 🔴 HIGH PRIORITY  
**Description:** 5 instances of `v-model.number` found on monetary/ID fields, causing precision loss or type coercion:
- `budget-items.vue` - fiscal_year (number is OK here)
- `line-items.vue` - business_case_id, budget_item_id, owner_group_id (these should be strings for IDs too)
**Files:** `frontend/pages/budget-items.vue:387,447`, `frontend/pages/line-items.vue:453,460,467`
**Impact:** May cause type coercion issues with ID fields

---

## 🟠 High Priority Issues (Code Quality & Deprecations)

### 2. Unpinned Dependencies
**Status:** 🟠 
**Description:** `requirements.txt` and `package.json` don't pin versions, risking breaking changes
**Files:** `backend/requirements.txt`, `frontend/package.json`
**Impact:** `fastapi`, `pydantic`, `sqlalchemy`, `nuxt` all unpinned

---

## 🟡 Medium Priority Issues (Testing & Coverage)

### 3. Frontend Unit Tests Broken
**Status:** 🟡 
**Description:** `npm run test:unit` fails with module resolution error
```
ERR_MODULE_NOT_FOUND: Failed to load url list (resolved id: list)
```
**Files:** `frontend/vitest.config.ts`, test files
**Impact:** No working frontend unit tests

### 4. E2E Tests Need Maintenance
**Status:** 🟡 
**Description:** 12 E2E test files, but many may be outdated or flaky
**Files:** `frontend/tests/e2e/*.spec.ts`
**Action:** Audit and fix E2E test suite

### 5. Backend Test Coverage Gaps
**Status:** 🟡
**Current:** 42 tests passing
**Missing coverage:**
- Password policy enforcement on login
- RecordAccess group grants
- Parent access validation (WBS under line item)

---

## 🟢 Technical Debt (Long-term Improvements)

### 6. Database Migrations
**Status:** 🟢 Pending
**Current:** Uses `Base.metadata.create_all()` (destroys data)
**Needed:** Alembic migrations for production
**Files:** `backend/app/database.py`
**Impact:** Cannot upgrade production DB without data loss

### 7. Password Hash Iterations
**Status:** 🟢
**Current:** bcrypt rounds=12 (default)
**Consider:** Increase to 14 for stronger security (trade-off: slower)
**Files:** `backend/app/auth.py:23`

### 8. Print Statements in Production Code
**Status:** 🟢 
**Found:** 4 print statements in `backend/app/main.py:94,98,111,114`
**Fix:** Use logging module instead


### 9. Missing Database Indexes
**Status:** 🟢
**Current:** Only `workday_ref`, `wbs_code`, `asset_code`, `po_number`, `gr_number` indexed
**Missing indexes:** `created_by`, `status`, `owner_group_id` on most tables

### 10. CORS Security
**Status:** 🟢 
**Current:** `secure=False` for cookies in development
**Needed:** Set `secure=True` when `ENVIRONMENT=production`
**Files:** `backend/app/routers/auth.py:90-91,124-125`

### 11. Password in Logs
**Status:** 🟢 
**Current:** Weak passwords can be registered (no client-side validation)
**Fix:** Add frontend password strength indicator

---

## 📊 Current State Summary

### Backend (FastAPI)
- **22 router files** with 2,368 lines of code
- **42 tests passing** (2 skipped)
- **Issues:** Deprecated APIs, unpinned deps, missing test coverage

### Frontend (Nuxt 4)
- **15 pages** with 6,547 lines of Vue code
- **12 E2E tests**, 0 working unit tests
- **Issues:** v-model.number regression, broken test setup

### Database
- **16 models** with proper relationships
- **Issues:** String timestamps, no migrations, missing indexes

---

## 🎯 Recommended Priority Order

1. **Immediate: Critical Fixes**
   - [ ] Fix v-model.number issues (data integrity)
   - [ ] Pin backend dependencies
   - [ ] Pin frontend dependencies

2. **Week 1: Testing**
   - [ ] Fix frontend unit tests
   - [ ] Audit and fix E2E tests
   - [ ] Add missing backend tests

3. **Week 2: Production Readiness**
   - [ ] Setup Alembic migrations
   - [ ] Add missing database indexes
   - [ ] Add frontend password strength UI
   - [ ] Configure production CORS
   - [ ] Replace print with logging

---

## ✅ Completed Items (Jan 2, 2026)

### Access Control
- [x] RecordAccess role-caps (Viewers cannot receive Write/Full)
- [x] BusinessCase delete hybrid access check
- [x] Creator audit-only access (Read)
- [x] lead_group_id enforcement
- [x] Owner-group filtering on all list endpoints
- [x] Missing user-groups PUT/DELETE endpoints
- [x] Alerts scoped to user access (commit 61b2985)

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

### Documentation
- [x] Created generic AI agent instructions (agents.md)
- [x] Renamed AGENTS.md to SETUP.md for clarity
- [x] Git history cleanup - Removed AI attribution footers
