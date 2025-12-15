# Ebrose – Codex Master Spec

> Feed this whole file to a code LLM and say:  
> **"Read through requirements-codex.md and generate the codebase for me."**

---

## 0. Project Overview

**Name:** Ebrose  
**Domain:** Procurement & Resource Tracking  

**Goal:** Replace Excel-based tracking of:
- Workday Budget Item → Business Case Line Item → WBS → Asset → SOW (future) → Purchase Order → Goods Receipt
- Resource ↔ Purchase Order allocation
- PO burn / remaining amount
- Alerts when POs are running out or data is missing

**Stack:**
- Frontend: Nuxt 4 (Vue 3, TypeScript allowed)
- Backend: FastAPI (Python)
- Database: SQLite (file-based, foreign keys ON)

### 0.1 Conventions (Important)

- **Dates vs datetimes:** Use ISO 8601 strings. Use `YYYY-MM-DD` for date-only fields (e.g., `start_date`, `end_date`, `gr_date`) and `YYYY-MM-DDTHH:MM:SSZ` (UTC) for audit fields (e.g., `created_at`, `updated_at`, `timestamp`).
- **Money fields:** `estimated_cost`, `requested_amount`, `budget_amount`, `total_amount`, `amount`, `cost_per_month`, `expected_monthly_burn` are currency amounts. **MVP choice:** store as SQLite `REAL` and use Python `Decimal` at the API boundary; round to 2dp on write and never rely on equality comparisons.
- **Currencies:** Use ISO 4217 codes (e.g., `SGD`, `USD`) in `currency`.
- **Record ownership:** Each access-scoped business record stores `owner_group_id` (FK → `UserGroup.id`). Users gain default access via `UserGroupMembership`. `BusinessCase` is special: it is not access-scoped; it is readable if the user can read at least one of its line items.
- **Enum-like fields:** Constrain `User.role` to `Admin|Manager|User|Viewer` and `RecordAccess.access_level` to `Read|Write|Full`.

---

## 1. Data Model (Entities)

### 1.1 User
- id: int PK
- username: string UNIQUE
- email: string UNIQUE  
- hashed_password: string
- full_name: string
- role: string (Admin, Manager, User, Viewer)
- is_active: bool (default True)
- created_at: string (ISO datetime)
- last_login: string (ISO datetime, nullable)

### 1.2 BusinessCase
- id: int PK  
- title: text  
- description: text  
- requestor: text  
- lead_group_id: int FK → UserGroup.id (the coordinating group that can edit BusinessCase-level metadata)
- estimated_cost: float (optional; may be computed as sum of line items)
- created_at: string (ISO datetime)  
- status: string (Draft, Submitted, Approved, Rejected, etc.)
- created_by: int FK → User.id (audit)
- updated_by: int FK → User.id (audit)
- updated_at: string (ISO datetime, audit)

### 1.3 BusinessCaseLineItem

Business cases can include multiple line items (often requested by different user groups). The line item is the unit that ties to Workday budget items and drives downstream procurement.

- id: int PK
- business_case_id: int FK → BusinessCase.id
- budget_item_id: int FK → BudgetItem.id
- owner_group_id: int FK → UserGroup.id (who owns this request)
- title: text
- description: text
- spend_category: string (CAPEX, OPEX)
- requested_amount: float
- currency: string
- planned_commit_date: string (ISO date)
- status: string (Draft, Submitted, Approved, Rejected, etc.)
- created_by: int FK → User.id (audit)
- updated_by: int FK → User.id (audit)
- created_at: string (ISO datetime, audit)
- updated_at: string (ISO datetime, audit)

### 1.4 WBS
- id: int PK  
- business_case_line_item_id: int FK → BusinessCaseLineItem.id
- wbs_code: string UNIQUE  
- description: text  
- owner_group_id: int FK → UserGroup.id
- status: string
- created_by: int FK → User.id (audit)
- updated_by: int FK → User.id (audit)
- created_at: string (ISO datetime, audit)
- updated_at: string (ISO datetime, audit)  

### 1.5 Asset
- id: int PK  
- wbs_id: int FK → WBS.id  
- asset_code: string UNIQUE  
- asset_type: string (CAPEX, OPEX; derived from line item)
- description: text  
- owner_group_id: int FK → UserGroup.id
- status: string
- created_by: int FK → User.id (audit)
- updated_by: int FK → User.id (audit)
- created_at: string (ISO datetime, audit)
- updated_at: string (ISO datetime, audit)  

### 1.6 PurchaseOrder
- id: int PK  
- asset_id: int FK → Asset.id  
- po_number: string UNIQUE  
- ariba_pr_number: string (nullable)
- supplier: string  
- po_type: string (T&M, Fixed, etc.)  
- start_date: string  
- end_date: string  
- total_amount: float  
- currency: string  
- spend_category: string (CAPEX, OPEX; derived from line item)
- planned_commit_date: string (ISO date)
- actual_commit_date: string (ISO date, nullable; set to PO approved date)
- owner_group_id: int FK → UserGroup.id
- status: string (Open, Closed, Exhausted, etc.)
- created_by: int FK → User.id (audit)
- updated_by: int FK → User.id (audit)
- created_at: string (ISO datetime, audit)
- updated_at: string (ISO datetime, audit)

### 1.7 GoodsReceipt
- id: int PK  
- po_id: int FK → PurchaseOrder.id  
- gr_number: string UNIQUE  
- gr_date: string  
- amount: float  
- description: text
- owner_group_id: int FK → UserGroup.id
- created_by: int FK → User.id (audit)
- updated_by: int FK → User.id (audit)
- created_at: string (ISO datetime, audit)
- updated_at: string (ISO datetime, audit)  

### 1.8 Resource
- id: int PK  
- name: string  
- vendor: string  
- role: string  
- start_date: string  
- end_date: string  
- cost_per_month: float  
- owner_group_id: int FK → UserGroup.id
- status: string (Active, Inactive, Left, etc.)
- created_by: int FK → User.id (audit)
- updated_by: int FK → User.id (audit)
- created_at: string (ISO datetime, audit)
- updated_at: string (ISO datetime, audit)

### 1.9 ResourcePOAllocation
- id: int PK  
- resource_id: int FK → Resource.id  
- po_id: int FK → PurchaseOrder.id  
- allocation_start: string  
- allocation_end: string  
- expected_monthly_burn: float
- owner_group_id: int FK → UserGroup.id
- created_by: int FK → User.id (audit)
- updated_by: int FK → User.id (audit)
- created_at: string (ISO datetime, audit)
- updated_at: string (ISO datetime, audit)  

### 1.10 UserGroup
- id: int PK
- name: string UNIQUE
- description: text
- created_by: int FK → User.id (audit)
- created_at: string (ISO datetime, audit)

### 1.11 UserGroupMembership
- id: int PK
- user_id: int FK → User.id
- group_id: int FK → UserGroup.id
- added_by: int FK → User.id (audit)
- added_at: string (ISO datetime, audit)

### 1.12 RecordAccess
- id: int PK
- record_type: string (BudgetItem, BusinessCase, BusinessCaseLineItem, WBS, Asset, PurchaseOrder, GoodsReceipt, Resource, ResourcePOAllocation)
- record_id: int (the ID of the specific record)
- user_id: int FK → User.id (nullable - for individual user access)
- group_id: int FK → UserGroup.id (nullable - for group access)
- access_level: string (Read, Write, Full)
- granted_by: int FK → User.id (who granted this access)
- granted_at: string (ISO datetime)
- expires_at: string (ISO datetime, nullable)

### 1.13 AuditLog
- id: int PK
- table_name: string (which table was affected)
- record_id: int (which record was affected)
- action: string (CREATE, UPDATE, DELETE)
- old_values: text (JSON of old values, null for CREATE)
- new_values: text (JSON of new values, null for DELETE)  
- user_id: int FK → User.id (who performed the action)
- timestamp: string (ISO datetime)
- ip_address: string (nullable)
- user_agent: string (nullable)

### 1.14 BudgetItem (Workday)

Represents a Workday budget line item / budget entry.

- id: int PK
- workday_ref: string UNIQUE
- title: text
- description: text
- budget_amount: float
- currency: string
- fiscal_year: int
- owner_group_id: int FK → UserGroup.id
- created_by: int FK → User.id (audit)
- updated_by: int FK → User.id (audit)
- created_at: string (ISO datetime, audit)
- updated_at: string (ISO datetime, audit)

---

## 2. Behaviors & Business Logic

### 2.1 PO Remaining Amount

For a given PurchaseOrder:

```text
remaining = purchase_order.total_amount
          - SUM(all goods_receipt.amount for that PO)
```

If no GRs exist, remaining = total_amount.

### 2.2 Alerts

Alerts are computed on request (no need to persist initially).

Alert types:

1. **Low PO balance**  
   - Condition: `remaining < threshold` (threshold configurable; % of total or fixed amount).

2. **No GR this month**  
   - Condition: PO has `status = 'Open'`  
   - AND there is no `GoodsReceipt` for that `po_id` with `gr_date` in current month.

3. **Resource without PO**  
   - Condition: Resource has `status = 'Active'`  
   - AND there is no `ResourcePOAllocation` such that  
     `allocation_start <= today <= allocation_end`.

4. **Missing chain**  
   - Condition: For a given PurchaseOrder:  
     - missing Asset, OR  
     - Asset missing WBS, OR  
     - WBS missing BusinessCaseLineItem, OR
     - BusinessCaseLineItem missing BusinessCase.

Expose alerts via `GET /alerts`.

### 2.3 Record-Level Access Control

**Default Access:**
- Records belong to an **owner user group** (`owner_group_id`) and are visible to all users in that group (not owned by an individual user)
- Creator of a record is captured for **audit only** (`created_by` / `updated_by`)
- Users with Manager/Admin roles have cross-group access based on role permissions
- Record-level grants (`RecordAccess`) can be used to share records across groups

**Ownership Assignment Rules:**
- For top-level records (`BudgetItem`, `BusinessCaseLineItem`, `Resource`), `owner_group_id` is required on create.
- For child records (`WBS`, `Asset`, `PurchaseOrder`, `GoodsReceipt`, `ResourcePOAllocation`), `owner_group_id` is inherited from the parent chain; if provided by the client it must either match or be ignored/overridden by the backend.
- If a normally-child record is created without its parent reference (e.g., `PurchaseOrder.asset_id` is null due to partial import), treat it as top-level for access purposes and require `owner_group_id` on create.
- `BusinessCase` is an umbrella object and is not used for access scoping. It should be readable by any user who can read at least one of its `BusinessCaseLineItem` records.
- `BusinessCase.lead_group_id` controls who can edit BusinessCase-level metadata (in addition to Manager/Admin).

**Access Levels:**
- **Read**: View record and its data
- **Write**: Read + Edit record data 
- **Full**: Write + Delete record + Grant access to others

**Access Resolution Logic:**
For any record access request:
1. Check if user is Admin → Full access to all records
2. Check if user is Manager → Full access to all records  
3. If record has `owner_group_id`: check if it is one of the user's groups → allow access per role (Viewer=Read-only; User=Read/Write; delete requires Manager+)
4. If record is `BusinessCase`: allow Read if user can Read any `BusinessCaseLineItem` where `business_case_id == BusinessCase.id`; allow Write only for `lead_group_id` members (role-capped)
5. Check explicit RecordAccess grants for user → use highest access level (still capped by role)
6. Check RecordAccess grants for user's groups → use highest access level (still capped by role)
7. Deny access

**Role Cap (Important):**
- A record-level grant must not elevate a user beyond what their role allows (e.g., Viewer remains read-only even if granted Write).

**Inheritance Rules:**
- Child records inherit access from parent where logical:
  - WBS inherits from BusinessCaseLineItem
  - Asset inherits from WBS
  - PurchaseOrder inherits from Asset
  - GoodsReceipt inherits from PurchaseOrder
  - ResourcePOAllocation requires access to both Resource and PurchaseOrder (intersection)

**Group Consistency (Important):**
- Child records must inherit the same `owner_group_id` as the parent, and writes must validate that `owner_group_id` values remain consistent across the chain.

### 2.4 Audit Trail

All create/update/delete operations must:
1. Record the user performing the action (created_by/updated_by)
2. Record the timestamp (created_at/updated_at)  
3. Log the action in audit trail (see AuditLog entity below)

---

## 3. Authentication & Authorization

### 3.1 Authentication System

**JWT Token-based Authentication:**
- Use JWT tokens for stateless authentication
- Access token expires in 15 minutes
- Refresh token expires in 7 days
- Store tokens in HTTP-only cookies for security (recommended names: `access_token`, `refresh_token`)
- Backend may optionally also accept `Authorization: Bearer <token>` (useful for Swagger/CLI), but the frontend should rely on cookies

### 3.2 Password Security
- Hash passwords using bcrypt with salt rounds >= 12
- Enforce minimum password requirements:
  - At least 8 characters
  - At least 1 uppercase letter
  - At least 1 lowercase letter  
  - At least 1 number
  - At least 1 special character

### 3.3 User Roles & Permissions

**Role Hierarchy:**
1. **Viewer** - Read-only access to all entities
2. **User** - Create/Edit records owned by their user group(s) + Viewer permissions
3. **Manager** - Create/Edit/Delete all data + User permissions  
4. **Admin** - User management + Manager permissions

**Permission Matrix:**
```
Entity          | Viewer | User | Manager | Admin
----------------|--------|------|---------|-------
Users           | Read   | Read | Read    | Full
UserGroups      | Read   | Read | Full    | Full
BudgetItem      | Read** | CRUD*| Full    | Full
BusinessCase    | Read** | CRUD*| Full    | Full
LineItem        | Read** | CRUD*| Full    | Full
WBS             | Read** | CRUD*| Full    | Full
Asset           | Read** | CRUD*| Full    | Full
PurchaseOrder   | Read** | CRUD*| Full    | Full
GoodsReceipt    | Read** | CRUD*| Full    | Full
Resource        | Read** | CRUD*| Full    | Full
Allocation      | Read** | CRUD*| Full    | Full
RecordAccess    | Read   | Grant+| Full    | Full
AuditLog        | Read   | Read | Read    | Full
Alerts          | Read   | Read | Read    | Read

* CRUD only for records in the user's group(s) + any records explicitly shared with them
** Subject to record-level access control
+ Grant access only for records in the user's group(s) (or where the user already has Full access)
```

### 3.4 Authentication & Access Management Endpoints

```
# Authentication
POST /auth/register     - Register new user (Admin only)
POST /auth/login        - Login with username/password
POST /auth/logout       - Logout (clear cookies; revoke refresh token if using server-side refresh storage)
POST /auth/refresh      - Refresh access token
GET  /auth/me          - Get current user info
PUT  /auth/me          - Update current user profile
PUT  /auth/password    - Change password

# User Groups
GET  /user-groups              - List all user groups
POST /user-groups              - Create new user group (Manager+)
GET  /user-groups/{id}         - Get user group details
PUT  /user-groups/{id}         - Update user group (Manager+)
DELETE /user-groups/{id}       - Delete user group (Manager+)
POST /user-groups/{id}/members - Add user to group (Manager+)
DELETE /user-groups/{id}/members/{user_id} - Remove user from group (Manager+)

# Record Access Management
GET  /record-access/{record_type}/{record_id}     - Get access list for record
POST /record-access/{record_type}/{record_id}     - Grant access to record
PUT  /record-access/{id}                          - Update access grant
DELETE /record-access/{id}                        - Revoke access grant

# Audit Trail
GET  /audit-logs                                  - Get audit logs (filterable)
GET  /audit-logs/{record_type}/{record_id}        - Get audit logs for specific record
```

### 3.5 Route Protection

All API routes except `/health` and `/auth/login` require authentication.
Use dependency injection to check:
1. Valid JWT token
2. User permissions for the requested operation
3. Group / record-level access control (owner group + `RecordAccess` grants)

### 3.6 Frontend Authentication

**Login Flow:**
1. User submits credentials to `/auth/login`
2. Backend validates and sets JWT tokens in HTTP-only cookies
3. Frontend redirects to dashboard
4. All API calls include cookies (`credentials: 'include'` if API is cross-origin)
5. Handle token refresh automatically on 401 responses

**Route Guards:**
- Redirect unauthenticated users to `/login`
- Show/hide UI elements based on user role
- Protect admin routes from non-admin users

---

## 4. Database Schema (SQLite)

### 4.1 SQL Schema

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  full_name TEXT NOT NULL,
  role TEXT DEFAULT 'User' CHECK (role IN ('Admin','Manager','User','Viewer')),
  is_active BOOLEAN DEFAULT 1,
  created_at TEXT,
  last_login TEXT
);

CREATE TABLE IF NOT EXISTS user_group (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  created_by INTEGER,
  created_at TEXT,
  FOREIGN KEY (created_by) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS user_group_membership (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  group_id INTEGER,
  added_by INTEGER,
  added_at TEXT,
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (group_id) REFERENCES user_group(id),
  FOREIGN KEY (added_by) REFERENCES user(id),
  UNIQUE(user_id, group_id)
);

CREATE TABLE IF NOT EXISTS business_case (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  requestor TEXT,
  lead_group_id INTEGER NOT NULL,
  estimated_cost REAL,
  created_at TEXT,
  status TEXT,
  created_by INTEGER,
  updated_by INTEGER,
  updated_at TEXT,
  FOREIGN KEY (lead_group_id) REFERENCES user_group(id),
  FOREIGN KEY (created_by) REFERENCES user(id),
  FOREIGN KEY (updated_by) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS budget_item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  workday_ref TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  budget_amount REAL NOT NULL,
  currency TEXT NOT NULL,
  fiscal_year INTEGER NOT NULL,
  owner_group_id INTEGER NOT NULL,
  created_by INTEGER,
  updated_by INTEGER,
  created_at TEXT,
  updated_at TEXT,
  FOREIGN KEY (owner_group_id) REFERENCES user_group(id),
  FOREIGN KEY (created_by) REFERENCES user(id),
  FOREIGN KEY (updated_by) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS business_case_line_item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  business_case_id INTEGER NOT NULL,
  budget_item_id INTEGER NOT NULL,
  owner_group_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  spend_category TEXT NOT NULL CHECK (spend_category IN ('CAPEX','OPEX')),
  requested_amount REAL NOT NULL,
  currency TEXT NOT NULL,
  planned_commit_date TEXT,
  status TEXT,
  created_by INTEGER,
  updated_by INTEGER,
  created_at TEXT,
  updated_at TEXT,
  FOREIGN KEY (business_case_id) REFERENCES business_case(id),
  FOREIGN KEY (budget_item_id) REFERENCES budget_item(id),
  FOREIGN KEY (owner_group_id) REFERENCES user_group(id),
  FOREIGN KEY (created_by) REFERENCES user(id),
  FOREIGN KEY (updated_by) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS wbs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  business_case_line_item_id INTEGER NOT NULL,
  wbs_code TEXT UNIQUE,
  description TEXT,
  owner_group_id INTEGER NOT NULL,
  status TEXT,
  created_by INTEGER,
  updated_by INTEGER,
  created_at TEXT,
  updated_at TEXT,
  FOREIGN KEY (business_case_line_item_id) REFERENCES business_case_line_item(id),
  FOREIGN KEY (owner_group_id) REFERENCES user_group(id),
  FOREIGN KEY (created_by) REFERENCES user(id),
  FOREIGN KEY (updated_by) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS asset (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  wbs_id INTEGER,
  asset_code TEXT UNIQUE,
  asset_type TEXT,
  description TEXT,
  owner_group_id INTEGER NOT NULL,
  status TEXT,
  created_by INTEGER,
  updated_by INTEGER,
  created_at TEXT,
  updated_at TEXT,
  FOREIGN KEY (wbs_id) REFERENCES wbs(id),
  FOREIGN KEY (owner_group_id) REFERENCES user_group(id),
  FOREIGN KEY (created_by) REFERENCES user(id),
  FOREIGN KEY (updated_by) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS purchase_order (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  asset_id INTEGER,
  po_number TEXT UNIQUE,
  supplier TEXT,
  po_type TEXT,
  start_date TEXT,
  end_date TEXT,
  total_amount REAL,
  currency TEXT,
  spend_category TEXT NOT NULL CHECK (spend_category IN ('CAPEX','OPEX')),
  planned_commit_date TEXT,
  actual_commit_date TEXT,
  ariba_pr_number TEXT,
  owner_group_id INTEGER NOT NULL,
  status TEXT,
  created_by INTEGER,
  updated_by INTEGER,
  created_at TEXT,
  updated_at TEXT,
  FOREIGN KEY (asset_id) REFERENCES asset(id),
  FOREIGN KEY (owner_group_id) REFERENCES user_group(id),
  FOREIGN KEY (created_by) REFERENCES user(id),
  FOREIGN KEY (updated_by) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS goods_receipt (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  po_id INTEGER,
  gr_number TEXT UNIQUE,
  gr_date TEXT,
  amount REAL,
  description TEXT,
  owner_group_id INTEGER NOT NULL,
  created_by INTEGER,
  updated_by INTEGER,
  created_at TEXT,
  updated_at TEXT,
  FOREIGN KEY (po_id) REFERENCES purchase_order(id),
  FOREIGN KEY (owner_group_id) REFERENCES user_group(id),
  FOREIGN KEY (created_by) REFERENCES user(id),
  FOREIGN KEY (updated_by) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS resource (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  vendor TEXT,
  role TEXT,
  start_date TEXT,
  end_date TEXT,
  cost_per_month REAL,
  owner_group_id INTEGER NOT NULL,
  status TEXT,
  created_by INTEGER,
  updated_by INTEGER,
  created_at TEXT,
  updated_at TEXT,
  FOREIGN KEY (owner_group_id) REFERENCES user_group(id),
  FOREIGN KEY (created_by) REFERENCES user(id),
  FOREIGN KEY (updated_by) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS resource_po_allocation (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  resource_id INTEGER,
  po_id INTEGER,
  allocation_start TEXT,
  allocation_end TEXT,
  expected_monthly_burn REAL,
  owner_group_id INTEGER NOT NULL,
  created_by INTEGER,
  updated_by INTEGER,
  created_at TEXT,
  updated_at TEXT,
  FOREIGN KEY (resource_id) REFERENCES resource(id),
  FOREIGN KEY (po_id) REFERENCES purchase_order(id),
  FOREIGN KEY (owner_group_id) REFERENCES user_group(id),
  FOREIGN KEY (created_by) REFERENCES user(id),
  FOREIGN KEY (updated_by) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS record_access (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  record_type TEXT NOT NULL,
  record_id INTEGER NOT NULL,
  user_id INTEGER,
  group_id INTEGER,
  access_level TEXT NOT NULL CHECK (access_level IN ('Read','Write','Full')),
  granted_by INTEGER,
  granted_at TEXT,
  expires_at TEXT,
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (group_id) REFERENCES user_group(id),
  FOREIGN KEY (granted_by) REFERENCES user(id),
  CHECK ((user_id IS NOT NULL AND group_id IS NULL) OR (user_id IS NULL AND group_id IS NOT NULL))
);

CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  table_name TEXT NOT NULL,
  record_id INTEGER NOT NULL,
  action TEXT NOT NULL,
  old_values TEXT,
  new_values TEXT,
  user_id INTEGER,
  timestamp TEXT NOT NULL,
  ip_address TEXT,
  user_agent TEXT,
  FOREIGN KEY (user_id) REFERENCES user(id)
);
```

---

## 5. Backend – FastAPI + SQLAlchemy

### 5.1 Database Setup (`backend/app/database.py`)

```python
import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ebrose.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

@event.listens_for(engine, "connect")
def enable_sqlite_fk(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

### 5.2 SQLAlchemy Models (`backend/app/models.py`)

```python
from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(Text, unique=True, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    full_name = Column(Text, nullable=False)
    role = Column(Text, nullable=False, default="User")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(Text)
    last_login = Column(Text)


class UserGroup(Base):
    __tablename__ = "user_group"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(Text)


class UserGroupMembership(Base):
    __tablename__ = "user_group_membership"
    __table_args__ = (UniqueConstraint("user_id", "group_id", name="uq_user_group_membership"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    group_id = Column(Integer, ForeignKey("user_group.id"))
    added_by = Column(Integer, ForeignKey("user.id"))
    added_at = Column(Text)


class BusinessCase(Base):
    __tablename__ = "business_case"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    requestor = Column(Text)
    lead_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False)
    estimated_cost = Column(Float)
    created_at = Column(Text)
    status = Column(Text)
    created_by = Column(Integer, ForeignKey("user.id"))
    updated_by = Column(Integer, ForeignKey("user.id"))
    updated_at = Column(Text)

    line_items = relationship("BusinessCaseLineItem", back_populates="business_case")


class BudgetItem(Base):
    __tablename__ = "budget_item"

    id = Column(Integer, primary_key=True, index=True)
    workday_ref = Column(Text, unique=True, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    budget_amount = Column(Float, nullable=False)
    currency = Column(Text, nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("user.id"))
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(Text)
    updated_at = Column(Text)

    line_items = relationship("BusinessCaseLineItem", back_populates="budget_item")


class BusinessCaseLineItem(Base):
    __tablename__ = "business_case_line_item"
    __table_args__ = (
        CheckConstraint("spend_category IN ('CAPEX','OPEX')", name="ck_bcli_spend_category"),
    )

    id = Column(Integer, primary_key=True, index=True)
    business_case_id = Column(Integer, ForeignKey("business_case.id"), nullable=False)
    budget_item_id = Column(Integer, ForeignKey("budget_item.id"), nullable=False)
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    spend_category = Column(Text, nullable=False)
    requested_amount = Column(Float, nullable=False)
    currency = Column(Text, nullable=False)
    planned_commit_date = Column(Text)
    status = Column(Text)
    created_by = Column(Integer, ForeignKey("user.id"))
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(Text)
    updated_at = Column(Text)

    business_case = relationship("BusinessCase", back_populates="line_items")
    budget_item = relationship("BudgetItem", back_populates="line_items")
    wbs_items = relationship("WBS", back_populates="line_item")


class WBS(Base):
    __tablename__ = "wbs"

    id = Column(Integer, primary_key=True, index=True)
    business_case_line_item_id = Column(Integer, ForeignKey("business_case_line_item.id"), nullable=False)
    wbs_code = Column(Text, unique=True)
    description = Column(Text)
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False)
    status = Column(Text)
    created_by = Column(Integer, ForeignKey("user.id"))
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(Text)
    updated_at = Column(Text)

    line_item = relationship("BusinessCaseLineItem", back_populates="wbs_items")
    assets = relationship("Asset", back_populates="wbs")


class Asset(Base):
    __tablename__ = "asset"

    id = Column(Integer, primary_key=True, index=True)
    wbs_id = Column(Integer, ForeignKey("wbs.id"))
    asset_code = Column(Text, unique=True)
    asset_type = Column(Text)
    description = Column(Text)
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False)
    status = Column(Text)
    created_by = Column(Integer, ForeignKey("user.id"))
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(Text)
    updated_at = Column(Text)

    wbs = relationship("WBS", back_populates="assets")
    purchase_orders = relationship("PurchaseOrder", back_populates="asset")


class PurchaseOrder(Base):
    __tablename__ = "purchase_order"
    __table_args__ = (
        CheckConstraint("spend_category IN ('CAPEX','OPEX')", name="ck_po_spend_category"),
    )

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("asset.id"))
    po_number = Column(Text, unique=True)
    supplier = Column(Text)
    po_type = Column(Text)
    start_date = Column(Text)
    end_date = Column(Text)
    total_amount = Column(Float)
    currency = Column(Text)
    spend_category = Column(Text, nullable=False)
    planned_commit_date = Column(Text)
    actual_commit_date = Column(Text)
    ariba_pr_number = Column(Text)
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False)
    status = Column(Text)
    created_by = Column(Integer, ForeignKey("user.id"))
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(Text)
    updated_at = Column(Text)

    asset = relationship("Asset", back_populates="purchase_orders")
    goods_receipts = relationship("GoodsReceipt", back_populates="po")
    allocations = relationship("ResourcePOAllocation", back_populates="po")


class GoodsReceipt(Base):
    __tablename__ = "goods_receipt"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_order.id"))
    gr_number = Column(Text, unique=True)
    gr_date = Column(Text)
    amount = Column(Float)
    description = Column(Text)
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("user.id"))
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(Text)
    updated_at = Column(Text)

    po = relationship("PurchaseOrder", back_populates="goods_receipts")


class Resource(Base):
    __tablename__ = "resource"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    vendor = Column(Text)
    role = Column(Text)
    start_date = Column(Text)
    end_date = Column(Text)
    cost_per_month = Column(Float)
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False)
    status = Column(Text)
    created_by = Column(Integer, ForeignKey("user.id"))
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(Text)
    updated_at = Column(Text)

    allocations = relationship("ResourcePOAllocation", back_populates="resource")


class ResourcePOAllocation(Base):
    __tablename__ = "resource_po_allocation"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resource.id"))
    po_id = Column(Integer, ForeignKey("purchase_order.id"))
    allocation_start = Column(Text)
    allocation_end = Column(Text)
    expected_monthly_burn = Column(Float)
    owner_group_id = Column(Integer, ForeignKey("user_group.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("user.id"))
    updated_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(Text)
    updated_at = Column(Text)

    resource = relationship("Resource", back_populates="allocations")
    po = relationship("PurchaseOrder", back_populates="allocations")


class RecordAccess(Base):
    __tablename__ = "record_access"
    __table_args__ = (
        CheckConstraint(
            "(user_id IS NOT NULL AND group_id IS NULL) OR (user_id IS NULL AND group_id IS NOT NULL)",
            name="ck_record_access_target",
        ),
        CheckConstraint("access_level IN ('Read','Write','Full')", name="ck_record_access_level"),
    )

    id = Column(Integer, primary_key=True, index=True)
    record_type = Column(Text, nullable=False)
    record_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    group_id = Column(Integer, ForeignKey("user_group.id"))
    access_level = Column(Text, nullable=False)
    granted_by = Column(Integer, ForeignKey("user.id"))
    granted_at = Column(Text)
    expires_at = Column(Text)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(Text, nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Column(Text, nullable=False)
    old_values = Column(Text)
    new_values = Column(Text)
    user_id = Column(Integer, ForeignKey("user.id"))
    timestamp = Column(Text, nullable=False)
    ip_address = Column(Text)
    user_agent = Column(Text)
```

### 5.3 Pydantic Schemas Example (`backend/app/schemas.py` – PurchaseOrder)

```python
from pydantic import BaseModel
from typing import Optional


class PurchaseOrderBase(BaseModel):
    asset_id: Optional[int] = None
    owner_group_id: Optional[int] = None
    po_number: str
    supplier: Optional[str] = None
    po_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_amount: float
    currency: str
    spend_category: str  # CAPEX|OPEX
    planned_commit_date: Optional[str] = None
    actual_commit_date: Optional[str] = None
    ariba_pr_number: Optional[str] = None
    status: Optional[str] = "Open"


class PurchaseOrderCreate(PurchaseOrderBase):
    pass


class PurchaseOrder(PurchaseOrderBase):
    id: int

    class Config:
        orm_mode = True
```

Note: `owner_group_id` is stored on `PurchaseOrder` in the database. When `asset_id` is present, derive/override `owner_group_id` from the parent `Asset` during create/update to keep the chain consistent.

If `asset_id` is null (partial import), require `owner_group_id` from the client and treat the PurchaseOrder as top-level for access control.

If using Pydantic v2, replace `class Config: orm_mode = True` with `model_config = ConfigDict(from_attributes=True)`.

### 5.4 Main App (`backend/app/main.py`)

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from . import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ebrose API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ebrose"}


@app.post("/purchase-orders", response_model=schemas.PurchaseOrder)
def create_po(po: schemas.PurchaseOrderCreate, db: Session = Depends(get_db)):
    db_po = models.PurchaseOrder(**po.dict())
    db.add(db_po)
    db.commit()
    db.refresh(db_po)
    return db_po
```

### 5.5 CRUD Router Pattern

Routers should follow this pattern per entity:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/purchase-orders", tags=["purchase-orders"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[schemas.PurchaseOrder])
def list_purchase_orders(db: Session = Depends(get_db)):
    return db.query(models.PurchaseOrder).all()


@router.get("/{po_id}", response_model=schemas.PurchaseOrder)
def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    po = db.query(models.PurchaseOrder).get(po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PurchaseOrder not found")
    return po


@router.post("/", response_model=schemas.PurchaseOrder)
def create_purchase_order(po: schemas.PurchaseOrderCreate, db: Session = Depends(get_db)):
    db_po = models.PurchaseOrder(**po.dict())
    db.add(db_po)
    db.commit()
    db.refresh(db_po)
    return db_po


@router.delete("/{po_id}")
def delete_purchase_order(po_id: int, db: Session = Depends(get_db)):
    po = db.query(models.PurchaseOrder).get(po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PurchaseOrder not found")
    db.delete(po)
    db.commit()
    return {"status": "deleted"}
```

Routers needed: budget-items, business-cases, business-case-line-items, wbs, assets, purchase-orders, goods-receipts, resources, allocations, alerts, auth, user-groups, record-access, audit-logs.

### 5.6 Authentication Dependencies (`backend/app/auth.py`)

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import or_
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_token(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    # Prefer Authorization header when present (Swagger/CLI), otherwise fall back to HttpOnly cookie.
    if credentials and credentials.scheme.lower() == "bearer":
        return credentials.credentials
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(required_role: str):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        role_hierarchy = {"Viewer": 0, "User": 1, "Manager": 2, "Admin": 3}
        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(required_role, 3)
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

def check_record_access(record_type: str, record_id: int, required_access: str):
    """
    Check if current user has required access to specific record.
    Access levels: Read < Write < Full
    """
    def access_checker(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
        # Admin has full access to everything
        if current_user.role == "Admin":
            return current_user
            
        # Manager has full access to everything  
        if current_user.role == "Manager":
            return current_user

        record = db.query(getattr(models, record_type)).get(record_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

        user_groups = db.query(models.UserGroupMembership).filter(
            models.UserGroupMembership.user_id == current_user.id
        ).all()

        user_group_ids = {m.group_id for m in user_groups}

        # BusinessCase is not access-scoped; Read is allowed if the user can read at least one line item.
        # (For a complete implementation, include cases where line items are readable via RecordAccess grants.)
        # Write is allowed only for members of BusinessCase.lead_group_id (still role-capped).
        if record_type == "BusinessCase":
            if required_access == "Read":
                has_owned_line_item = db.query(models.BusinessCaseLineItem.id).filter(
                    models.BusinessCaseLineItem.business_case_id == record_id,
                    models.BusinessCaseLineItem.owner_group_id.in_(user_group_ids),
                ).first()
                if has_owned_line_item:
                    return current_user

            if required_access in ["Write", "Full"] and record.lead_group_id in user_group_ids:
                return current_user
            
        # Check explicit record access grants
        access_levels = {"Read": 0, "Write": 1, "Full": 2}
        required_level = access_levels.get(required_access, 2)
        
        # Check direct user access
        user_access = db.query(models.RecordAccess).filter(
            models.RecordAccess.record_type == record_type,
            models.RecordAccess.record_id == record_id,
            models.RecordAccess.user_id == current_user.id,
            or_(models.RecordAccess.expires_at.is_(None), models.RecordAccess.expires_at > datetime.utcnow().isoformat())
        ).first()
        
        if user_access and access_levels.get(user_access.access_level, 0) >= required_level:
            return current_user
            
        # Check group access
        for membership in user_groups:
            group_access = db.query(models.RecordAccess).filter(
                models.RecordAccess.record_type == record_type,
                models.RecordAccess.record_id == record_id,
                models.RecordAccess.group_id == membership.group_id,
                or_(models.RecordAccess.expires_at.is_(None), models.RecordAccess.expires_at > datetime.utcnow().isoformat())
            ).first()
            
            if group_access and access_levels.get(group_access.access_level, 0) >= required_level:
                return current_user

        # Default group access: records belong to an owning group, not an individual user
        if hasattr(record, 'owner_group_id') and record.owner_group_id in user_group_ids:
            if current_user.role == "Viewer" and required_access == "Read":
                return current_user
            if current_user.role == "User" and required_access in ["Read", "Write"]:
                return current_user
                
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient {required_access} access to {record_type} {record_id}"
        )
        
    return access_checker

def audit_log_change(action: str, table_name: str, record_id: int, old_values: dict = None, new_values: dict = None):
    """Middleware to log all changes to audit trail"""
    def audit_decorator(func):
        async def wrapper(*args, **kwargs):
            # Get current user and db from kwargs
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if current_user and db:
                audit_entry = models.AuditLog(
                    table_name=table_name,
                    record_id=record_id,
                    action=action,
                    old_values=json.dumps(old_values) if old_values else None,
                    new_values=json.dumps(new_values) if new_values else None,
                    user_id=current_user.id,
                    timestamp=datetime.utcnow().isoformat(),
                    ip_address=kwargs.get('request').client.host if kwargs.get('request') else None
                )
                db.add(audit_entry)
                db.commit()
                
            return await func(*args, **kwargs)
        return wrapper
    return audit_decorator
```

---

## 6. Frontend – Nuxt 4

### 6.1 Nuxt Config (`frontend/nuxt.config.ts`)

```ts
export default defineNuxtConfig({
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      title: 'Ebrose',
      meta: [
        { name: 'description', content: 'Ebrose - procurement and budget tracking' }
      ]
    }
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || process.env.API_BASE || 'http://localhost:8000'
    }
  }
})
```

### 6.2 Global Styles (`frontend/assets/css/main.css`)

```css
:root {
  --color-primary: #1ED760;
  --color-bg: #F7F7F7;
  --color-text: #333333;
  --color-muted: #666666;
  --color-card: #FFFFFF;
  --shadow-soft: 0 10px 25px rgba(0,0,0,0.06);
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  background-color: var(--color-bg);
  color: var(--color-text);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

a {
  color: var(--color-primary);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.header {
  background-color: #ffffff;
  box-shadow: var(--shadow-soft);
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-title {
  font-size: 1.5rem;
  font-weight: 700;
}

.header-sub {
  font-size: 0.85rem;
  color: var(--color-muted);
}

.btn-primary {
  background-color: var(--color-primary);
  color: #ffffff;
  border: none;
  padding: 0.6rem 1.3rem;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primary:hover {
  filter: brightness(0.95);
}

.main-container {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem 3rem;
}

.card {
  background-color: var(--color-card);
  border-radius: 12px;
  box-shadow: var(--shadow-soft);
  padding: 1.5rem;
}

.card-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.card-sub {
  font-size: 0.85rem;
  color: var(--color-muted);
  margin-bottom: 1rem;
}

.grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 1.2fr);
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
```

### 6.3 Layout (`frontend/layouts/default.vue`)

```vue
<template>
  <div>
    <header class="header">
      <div>
        <div class="header-title">Ebrose</div>
        <div class="header-sub">Chamber of Spend Records</div>
      </div>
      <nav>
        <NuxtLink to="/" class="mr-4">Dashboard</NuxtLink>
        <NuxtLink to="/purchase-orders">Purchase Orders</NuxtLink>
      </nav>
    </header>
    <main class="main-container">
      <slot />
    </main>
  </div>
</template>
```

### 6.4 Root App (`frontend/app.vue`)

```vue
<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
```

### 6.5 Dashboard Page (`frontend/pages/index.vue`)

```vue
<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const health = ref<{ status: string; service: string } | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const res = await $fetch(`${apiBase}/health`, { credentials: 'include' })
    health.value = res as any
  } catch (e) {
    console.error(e)
    error.value = 'Failed to reach backend API.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="grid">
    <div class="card">
      <h1 class="card-title">Welcome to Ebrose</h1>
      <p class="card-sub">
        Track Business Cases, Purchase Orders, Resources, and Goods Receipts — without fighting Excel.
      </p>
      <p>
        This is your StarHub-inspired command center for procurement and resource tracking.
      </p>
      <button class="btn-primary" style="margin-top: 1rem;">
        Create Purchase Order
      </button>
    </div>

    <div class="card">
      <h2 class="card-title">Backend status</h2>
      <p class="card-sub">FastAPI + SQLite</p>

      <p v-if="loading">Checking backend health…</p>
      <p v-else-if="error" style="color: #cc0000;">{{ error }}</p>
      <div v-else-if="health">
        <p><strong>Status:</strong> {{ health.status }}</p>
        <p><strong>Service:</strong> {{ health.service }}</p>
      </div>
      <p v-else>Unknown state.</p>
    </div>
  </section>
</template>
```

### 6.6 Purchase Orders Page (`frontend/pages/purchase-orders.vue`)

```vue
<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

interface PurchaseOrder {
  id: number
  po_number: string
  supplier?: string
  total_amount: number
  currency: string
  status?: string
}

const pos = ref<PurchaseOrder[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const fetchPOs = async () => {
  try {
    const res = await $fetch<PurchaseOrder[]>(`${apiBase}/purchase-orders`, { credentials: 'include' })
    pos.value = res
  } catch (e) {
    console.error(e)
    error.value = 'Failed to load purchase orders.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchPOs)
</script>

<template>
  <section class="card">
    <h1 class="card-title">Purchase Orders</h1>
    <p class="card-sub">List of all POs from the backend API.</p>

    <p v-if="loading">Loading…</p>
    <p v-else-if="error" style="color: #cc0000;">{{ error }}</p>
    <table v-else class="po-table" style="width:100%; border-collapse:collapse; font-size:0.9rem;">
      <thead>
        <tr>
          <th style="text-align:left; padding:0.5rem 0;">PO Number</th>
          <th style="text-align:left; padding:0.5rem 0;">Supplier</th>
          <th style="text-align:left; padding:0.5rem 0;">Amount</th>
          <th style="text-align:left; padding:0.5rem 0;">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="po in pos" :key="po.id">
          <td style="padding:0.4rem 0;">{{ po.po_number }}</td>
          <td style="padding:0.4rem 0;">{{ po.supplier || '-' }}</td>
          <td style="padding:0.4rem 0;">
            {{ po.total_amount }} {{ po.currency }}
          </td>
          <td style="padding:0.4rem 0;">{{ po.status || 'Open' }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
```

### 6.7 Login Page (`frontend/pages/login.vue`)

```vue
<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const form = ref({
  username: '',
  password: ''
})
const loading = ref(false)
const error = ref<string | null>(null)

const login = async () => {
  loading.value = true
  error.value = null
  
  try {
    await $fetch(`${apiBase}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      credentials: 'include',
      body: new URLSearchParams({
        username: form.value.username,
        password: form.value.password
      })
    })

    await navigateTo('/')
  } catch (e: any) {
    error.value = e.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="card-title">Welcome to Ebrose</h1>
      <p class="card-sub">Please sign in to continue</p>
      
      <form @submit.prevent="login" class="login-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input 
            id="username" 
            v-model="form.username" 
            type="text" 
            required 
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <input 
            id="password" 
            v-model="form.password" 
            type="password" 
            required 
            class="form-input"
          />
        </div>
        
        <p v-if="error" class="error-message">{{ error }}</p>
        
        <button 
          type="submit" 
          :disabled="loading" 
          class="btn-primary login-btn"
        >
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
}

.login-card {
  background: var(--color-card);
  border-radius: 12px;
  box-shadow: var(--shadow-soft);
  padding: 2rem;
  width: 100%;
  max-width: 400px;
}

.login-form {
  margin-top: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(30, 215, 96, 0.1);
}

.login-btn {
  width: 100%;
  margin-top: 1rem;
}

.error-message {
  color: #dc2626;
  font-size: 0.875rem;
  margin: 0.5rem 0;
}
</style>
```

---

## 7. Meta Instructions to the Code LLM

When using this file, you can instruct the LLM:

> You are a coding assistant.  
> Read the file `requirements-codex.md`.  
> - Generate the full backend (FastAPI + SQLAlchemy) based on the spec.  
> - Implement JWT-based authentication with role-based access control.
> - Implement comprehensive audit tracking for all record changes.
> - Implement user groups and record-level access control.
> - Generate CRUD routers for all entities with proper authentication and access control.
> - Add audit logging middleware to track all database changes.
> - Generate the Nuxt 4 frontend, including pages for login, dashboard, purchase orders, and access management.
> - Implement frontend authentication with route guards and role-based UI.
> - Add user group management and record access sharing features in the UI.
> - Ensure the backend runs with `uvicorn app.main:app --reload`.  
> - Ensure the frontend runs with `npm run dev`.  
> - Use the StarHub-inspired CSS theme from the spec.

End of file.
