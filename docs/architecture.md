# Architecture & Design Decisions

## High-Level Architecture

- **Frontend** (Nuxt 4): Vue 3 SPA with Pinia state management
- **Backend** (FastAPI): REST API with SQLAlchemy ORM
- **Database** (SQLite dev / PostgreSQL prod): Relational data storage

## Repository Layout

```
ebrose/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app, router registration, CORS
│   │   ├── models.py         # SQLAlchemy models (14 entities)
│   │   ├── schemas.py        # Pydantic schemas with validation
│   │   ├── auth.py           # JWT auth, access control, audit logging
│   │   ├── routers/          # Entity routers (budget_items, business_cases, etc.)
│   │   └── database.py       # DB connection and session management
│   ├── tests/                # Backend pytest tests
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── pages/                # Nuxt routes/pages (11 entity pages)
│   ├── components/           # Reusable Vue components
│   ├── composables/          # Shared API helpers (useApiFetch)
│   ├── middleware/           # Auth guards
│   └── tests/e2e/            # Playwright E2E tests
├── helm/ebrose/              # Kubernetes Helm charts
├── docs/                     # TechDocs documentation
└── catalog-info.yaml         # Backstage catalog entry
```

## Security Model

### Authentication
- JWT tokens stored in **HttpOnly cookies**
- Automatic token refresh on expiry
- Role-based access control (4 tiers)

### Role Hierarchy
```
Admin > Manager > User > Viewer
```

### Access Control
- **Owner-Group Scoping**: List/read filtered by group membership
- **Record-Level Grants**: Explicit permissions via RecordAccess
- **Hybrid BusinessCase Access**: Creator + Line Items + Explicit Grants

## Architecture Decision Records (ADRs)

### ADR-001: JWT Authentication with HttpOnly Cookies ✅
Secure SPA authentication preventing XSS attacks.

### ADR-002: Owner-Group Access Scoping ✅
Filter all records by owner_group_id membership.

### ADR-003: Hybrid BusinessCase Access Model ✅
3-path access: Creator → Line Items → Explicit Grants.

### ADR-004: Decimal Money Handling ✅
Numeric(10,2) for all currency fields with 2dp rounding.

### ADR-005: Owner Group Inheritance Chain ✅
Child records inherit owner_group_id from parent chain.

### ADR-006: Database Choice ✅
SQLite for dev, PostgreSQL for production.

## Entity Relationship Diagram

```
User ──┬── UserGroup ── UserGroupMembership
        │                      │
        └── RecordAccess ◄─────┤
                                │
BudgetItem ◄──── BusinessCaseLineItem ◄── BusinessCase
     │                     │                     ▲
     │                     └── WBS ─── Asset ────┘
     │                                         │
     │                                         ▼
     └────────────────────────────────► PurchaseOrder ──► GoodsReceipt
                                                    │
Resource ◄───────────────────── ResourcePOAllocation
     ▲                                     │
     │                                     ▼
     └───────────────────────────────── PurchaseOrder
```

## Data Flow

1. **Create BudgetItem** → assigned owner_group_id
2. **Create BusinessCase** → Draft status
3. **Create LineItem** → links BudgetItem to BusinessCase, inherits owner_group_id
4. **Create WBS** → inherits from LineItem
5. **Create Asset** → inherits from WBS
6. **Create PurchaseOrder** → inherits from Asset
7. **Create GoodsReceipt** → inherits from PurchaseOrder

Each step inherits owner_group_id from parent, ensuring access control chain integrity.

## Compliance & Audit

- All CRUD operations logged to AuditLog table
- Tracks: user, timestamp, old_values, new_values
- Admin-only access to full audit trail
- JSON diff viewing for changes

## Current Status

✅ **Production Ready** (100% MVP Complete)
- All 14 entities with full CRUD
- Complete access control implementation
- Comprehensive audit logging
- Owner-group inheritance
- Decimal money handling
- 58 E2E tests passing
