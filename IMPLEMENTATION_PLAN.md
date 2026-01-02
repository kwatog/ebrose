# Ebrose Implementation Plan

**Last Updated:** January 2, 2026

Based on the recommendations in `RECOMMENDATIONS.md` and updated requirements in `requirements-codex.md`, this plan tracks the implementation progress from MVP to production-ready state.

## 🔴 Critical Issues (Security & Data Integrity)

### 1. Alerts Not Scoped to User Access
**Status:** 🔴 HIGH PRIORITY
**Description:** The `/alerts` endpoint returns alerts for ALL records, not just records the user has access to. This is a security/privacy issue.
- Currently: `db.query(models.PurchaseOrder).all()` - returns all POs
- Should: Filter to only accessible records per owner_group_id
**Files:** `backend/app/routers/alerts.py:23`
**Impact:** Users can see alerts for records they shouldn't have access to

### 2. Frontend v-model.number Regression
**Status:** 🔴 HIGH PRIORITY  
**Description:** 5 instances of `v-model.number` found on monetary/ID fields, causing precision loss or type coercion:
- `budget-items.vue` - fiscal_year (number is OK here)
- `line-items.vue` - business_case_id, budget_item_id, owner_group_id (these should be strings for IDs too)
**Files:** `frontend/pages/budget-items.vue:387,447`, `frontend/pages/line-items.vue:453,460,467`
**Impact:** May cause type coercion issues with ID fields

---

## 🟠 High Priority Issues (Code Quality & Deprecations)

### 3. Deprecated datetime.utcnow()
**Status:** 🟠 60 instances
**Description:** Python's `datetime.utcnow()` is deprecated and scheduled for removal in Python 3.12+
**Files:** Throughout `backend/app/`
**Fix:** Replace with `datetime.now(UTC)` or `datetime.now(timezone.utc)`

### 4. Deprecated SQLAlchemy query.get()
**Status:** 🟠 ~20+ instances
**Description:** `db.query(Model).get(id)` is legacy in SQLAlchemy 1.x, removed in 2.0
**Files:** `backend/app/routers/*.py` (users, purchase_orders, wbs, record_access, business_cases, assets)
**Fix:** Use `db.get(Model, id)` instead

### 5. Deprecated FastAPI @app.on_event
**Status:** 🟠 1 instance
**Description:** `@app.on_event("startup")` is deprecated, use lifespan context managers
**Files:** `backend/app/main.py:74`
**Fix:** Convert to `@app.lifespan("startup")`

### 6. Unpinned Dependencies
**Status:** 🟠 
**Description:** `requirements.txt` and `package.json` don't pin versions, risking breaking changes
**Files:** `backend/requirements.txt`, `frontend/package.json`
**Impact:** `fastapi`, `pydantic`, `sqlalchemy`, `nuxt` all unpinned

---

## 🟡 Medium Priority Issues (Testing & Coverage)

### 7. Frontend Unit Tests Broken
**Status:** 🟡 
**Description:** `npm run test:unit` fails with module resolution error
```
ERR_MODULE_NOT_FOUND: Failed to load url list (resolved id: list)
```
**Files:** `frontend/vitest.config.ts`, test files
**Impact:** No working frontend unit tests

### 8. E2E Tests Need Maintenance
**Status:** 🟡 
**Description:** 12 E2E test files, but many may be outdated or flaky
**Files:** `frontend/tests/e2e/*.spec.ts`
**Action:** Audit and fix E2E test suite

### 9. Backend Test Coverage Gaps
**Status:** 🟡 
**Current:** 42 tests passing
**Missing coverage:**
- Alerts endpoint access control
- Password policy enforcement on login
- RecordAccess group grants
- Parent access validation (WBS under line item)

---

## 🟢 Technical Debt (Long-term Improvements)

### 10. Database Migrations
**Status:** 🟢 Pending
**Current:** Uses `Base.metadata.create_all()` (destroys data)
**Needed:** Alembic migrations for production
**Files:** `backend/app/database.py`
**Impact:** Cannot upgrade production DB without data loss

### 11. Password Hash Iterations
**Status:** 🟢 
**Current:** bcrypt rounds=12 (default)
**Consider:** Increase to 14 for stronger security (trade-off: slower)
**Files:** `backend/app/auth.py:23`

### 12. Print Statements in Production Code
**Status:** 🟢 
**Found:** 4 print statements in `backend/app/main.py:94,98,111,114`
**Fix:** Use logging module instead

### 13. String-based Timestamps
**Status:** 🟢 
**Current:** All timestamps are `String(32)`, not DateTime
**Impact:** No timezone awareness, sorting issues
**Files:** All models

### 14. Missing Database Indexes
**Status:** 🟢 
**Current:** Only `workday_ref`, `wbs_code`, `asset_code`, `po_number`, `gr_number` indexed
**Missing indexes:** `created_by`, `status`, `owner_group_id` on most tables

### 15. CORS Security
**Status:** 🟢 
**Current:** `secure=False` for cookies in development
**Needed:** Set `secure=True` when `ENVIRONMENT=production`
**Files:** `backend/app/routers/auth.py:90-91,124-125`

### 16. Password in Logs
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

1. **Week 1: Critical Fixes**
   - [ ] Fix alerts access control (security)
   - [ ] Fix v-model.number issues (data integrity)
   - [ ] Pin backend dependencies
   - [ ] Pin frontend dependencies

2. **Week 2: Technical Debt**
   - [ ] Fix deprecated datetime usage
   - [ ] Fix deprecated SQLAlchemy query.get()
   - [ ] Convert @app.on_event to lifespan
   - [ ] Replace print with logging

3. **Week 3: Testing**
   - [ ] Fix frontend unit tests
   - [ ] Audit and fix E2E tests
   - [ ] Add missing backend tests

4. **Week 4: Production Readiness**
   - [ ] Setup Alembic migrations
   - [ ] Add missing database indexes
   - [ ] Add frontend password strength UI
   - [ ] Configure production CORS

---

## ✅ Completed Items (Jan 2, 2026)

### Access Control
- [x] RecordAccess role-caps (Viewers cannot receive Write/Full)
- [x] BusinessCase delete hybrid access check
- [x] Creator audit-only access (Read)
- [x] lead_group_id enforcement
- [x] Owner-group filtering on all list endpoints
- [x] Missing user-groups PUT/DELETE endpoints

### Auth Enhancements
- [x] Password policy enforcement
- [x] /auth/password endpoint
- [x] /auth/me PUT endpoint
- [x] Password validation on registration

### Tests
- [x] 6 new auth tests (13 total)
- [x] 3 new access control tests (36 total backend tests)
- [x] Updated BusinessCase hybrid access tests
