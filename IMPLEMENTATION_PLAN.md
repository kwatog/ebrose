# Mazarbul Implementation Plan

Based on the recommendations in `RECOMMENDATIONS.md`, this plan addresses identified gaps in priority order from security critical to quality improvements.

## 🔴 Security Critical (Immediate)

### ✅ 1. Environment-driven CORS and Secrets
**Status:** Completed  
**Description:** Fixed hardcoded SECRET_KEY and CORS wildcard configuration  
**Impact:** Eliminates security vulnerabilities in production deployments

### 🔄 2. HttpOnly Cookie Authentication
**Status:** In Progress  
**Priority:** High  
**Description:** Implement secure token storage using HttpOnly cookies with refresh mechanism
- Replace client-side token storage with server-set HttpOnly cookies
- Add refresh token endpoint for seamless token renewal
- Implement automatic retry on 401 responses
**Files to modify:**
- `backend/app/routers/auth.py` - Add refresh endpoint, set HttpOnly cookies
- `frontend/middleware/auth.global.ts` - Remove client token handling
- `frontend/composables/useAuth.ts` - Add API retry logic

### 🔄 3. Record Access CRUD Endpoints
**Status:** Pending  
**Priority:** High  
**Description:** Frontend calls missing DELETE/PUT endpoints for record access management
- Add `DELETE /record-access/{id}` endpoint
- Add `PUT /record-access/{id}` endpoint for updating access permissions
**Files to modify:**
- `backend/app/routers/record_access.py`

### 🔄 4. Secure Admin Bootstrap
**Status:** Pending  
**Priority:** High  
**Description:** Remove password logging and use environment-driven admin creation
- Read initial admin credentials from environment variables
- Remove password printing to logs
- Disable default admin creation in production
**Files to modify:**
- `backend/app/main.py` - Startup admin creation logic

## 🟡 High Impact (Functionality)

### 🔄 5. UPDATE Endpoints with Audit Logging
**Status:** Pending  
**Priority:** Medium  
**Description:** Add missing UPDATE operations for all entities with proper audit trails
- Implement UPDATE endpoints for all 12 entities
- Capture old_values in audit logs for UPDATE operations
- Add consistent audit logging across all CRUD operations
**Files to modify:**
- All router files in `backend/app/routers/`
- `backend/app/auth.py` - Enhance audit decorator

### 🔄 6. Department-based Access Control
**Status:** Pending  
**Priority:** Medium  
**Description:** Implement department scoping for User role and data inheritance
- Add department filtering to list endpoints for User role
- Implement inheritance: BC → WBS → Asset → PO → GR
- Centralize access control logic
**Files to modify:**
- `backend/app/auth.py` - Access control functions
- All router files - Add department filtering

### 🔄 7. Pagination and Filtering
**Status:** Pending  
**Priority:** Medium  
**Description:** Add pagination and basic filtering to prevent performance issues
- Add `limit`, `offset`, and `skip` parameters to list endpoints
- Implement basic filtering by common fields
- Add default sorting for consistent results
**Files to modify:**
- All router files with list endpoints
- `backend/app/schemas.py` - Add pagination schemas

### 🔄 8. Centralized Access Control
**Status:** Pending  
**Priority:** Medium  
**Description:** Create utility function to compute effective access permissions
- Consolidate role, creator, group, and department access logic
- Eliminate duplication across routers
- Provide consistent access control behavior
**Files to modify:**
- `backend/app/auth.py` - New access control utility
- All router files - Use centralized utility

## 🟢 Quality & Technical Debt (Long-term)

### 🔄 9. DateTime Handling
**Status:** Pending  
**Priority:** Low  
**Description:** Convert string timestamps to proper DateTime objects
- Replace string timestamp fields with DateTime columns
- Update all models to use DateTime types
- Add proper timezone handling
**Files to modify:**
- `backend/app/models.py` - All timestamp fields
- Database migration required

### 🔄 10. Database Constraints
**Status:** Pending  
**Priority:** Low  
**Description:** Add missing database constraints and indexes
- Add `UniqueConstraint` for `(user_id, group_id)` in UserGroupMembership
- Add check constraint for RecordAccess (user_id OR group_id NOT NULL)
- Add indexes for frequent lookups (po_number, wbs_code, asset_code)
**Files to modify:**
- `backend/app/models.py` - Add constraints and indexes

### 🔄 11. SQLAlchemy API Upgrade
**Status:** Pending  
**Priority:** Low  
**Description:** Replace deprecated SQLAlchemy 1.x API with 2.x compatible code
- Replace `query.get(id)` with `session.get(Model, id)`
- Update query patterns for SQLAlchemy 2.x compatibility
**Files to modify:**
- All router files and auth.py

### 🔄 12. Testing Framework
**Status:** Pending  
**Priority:** Low  
**Description:** Add comprehensive testing infrastructure
- Set up pytest for backend with test database
- Add authentication and access control tests
- Add audit logging tests
- Set up frontend testing with Vitest
**Files to create:**
- `backend/tests/` directory structure
- `frontend/tests/` directory structure
- CI/CD integration

## 📊 Progress Tracking

| Task | Priority | Status | Completion |
|------|----------|--------|------------|
| Environment CORS/Secrets | High | ✅ Complete | 100% |
| HttpOnly Cookie Auth | High | 🔄 In Progress | 0% |
| Record Access CRUD | High | 🔄 Pending | 0% |
| Secure Admin Bootstrap | High | 🔄 Pending | 0% |
| UPDATE Endpoints | Medium | 🔄 Pending | 0% |
| Department Access Control | Medium | 🔄 Pending | 0% |
| Pagination/Filtering | Medium | 🔄 Pending | 0% |
| Centralized Access Control | Medium | 🔄 Pending | 0% |
| DateTime Handling | Low | 🔄 Pending | 0% |
| Database Constraints | Low | 🔄 Pending | 0% |
| SQLAlchemy Upgrade | Low | 🔄 Pending | 0% |
| Testing Framework | Low | 🔄 Pending | 0% |

## 🎯 Current Focus

Starting with **HttpOnly Cookie Authentication** as the highest security priority that significantly improves the application's security posture.

## 📋 Implementation Notes

- Each task includes specific file modifications needed
- Security critical items must be completed before production deployment
- High impact functionality items improve user experience and system completeness
- Quality improvements can be implemented incrementally over time
- All changes require thorough testing before deployment