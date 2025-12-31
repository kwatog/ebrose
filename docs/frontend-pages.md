# Frontend Pages

Base URL (local): `http://localhost:3000`

## Public Pages

| Route | Description |
|-------|-------------|
| `/login` | Login page with username/password |
| `/health` | Frontend health status page |

---

## Main Application Pages

### Dashboard (`/`)
- System health indicator
- Navigation to all entity pages
- Quick stats summary

### Budget Items (`/budget-items`)
- List all accessible budgets
- Create/Edit/Delete budgets
- Filter by fiscal year
- Share budget with users/groups

**Columns:**
- Workday Ref
- Title
- Budget Amount (2dp formatting)
- Fiscal Year
- Owner Group
- Created By
- Actions (Edit, Share, Delete)

---

### Business Cases (`/business-cases`)
- List business cases (hybrid access)
- Create new business case
- Status workflow: Draft → Submitted → Review → Approved/Rejected
- Add line items
- View linked budgets

---

### Line Items (`/line-items`)
- List line items (budget-to-BC linking)
- Create line item
- Select budget item and business case
- Set spend category (CAPEX/OPEX)
- Set requested amount

---

### WBS (`/wbs`)
- Work Breakdown Structure items
- Create WBS linked to line item
- Inherits owner_group_id from parent

---

### Assets (`/assets`)
- Fixed assets tracking
- Create asset linked to WBS
- Inherits owner_group_id from WBS
- Asset codes and types

---

### Purchase Orders (`/purchase-orders`)
- PO management
- Create PO linked to asset
- Inherits owner_group_id from asset
- Status tracking (Open, Issued, Closed)

---

### Goods Receipts (`/goods-receipts`)
- Receipt tracking
- Create GR linked to PO
- Inherits owner_group_id from PO
- Amount and date tracking

---

### Resources (`/resources`)
- Vendor resource management
- Create resource with monthly cost
- Cost per month with 2dp formatting

---

### Allocations (`/allocations`)
- Resource-to-PO allocations
- Create allocation linked to resource and PO
- Expected monthly burn rate

---

## Admin Pages

### User Groups (`/admin/groups`)
**Requires:** Admin or Manager role

- List all user groups
- Create/Edit/Delete groups
- Add/Remove group members
- View member list

---

### Audit Logs (`/admin/audit`)
**Requires:** Admin role only

- View complete audit trail
- Filter by user
- Filter by date range
- Expand to see old/new values (JSON diff)
- Export audit data

---

## Authentication Flow

1. User navigates to `/login`
2. Enters credentials
3. Backend sets HttpOnly cookies
4. User redirected to `/`
5. Middleware checks `user_info` cookie
6. Access granted/denied based on role

---

## Navigation Structure

```
┌─────────────────────────────────────────┐
│  Logo    │  Budgets  BCs  LineItems... │  [User Menu]
├─────────────────────────────────────────┤
│                                         │
│           Page Content                  │
│                                         │
└─────────────────────────────────────────┘
```

### Admin Dropdown (Admin/Manager only)
- User Groups
- Audit Logs

---

## Record Sharing Modal

Accessed from any record detail page via "Share" button.

**Features:**
- Grant access to specific user
- Grant access to group
- Set access level (Read/Write/Full)
- Set expiration date
- View existing grants
- Revoke access

---

## Shared Components

### RecordAccessModal.vue
- Grant/revoke record access
- User/group selection
- Access level dropdown
- Expiration date picker

### useApiFetch.ts
- Wrapper around fetch with automatic cookies
- Refresh-on-401 behavior
- Consistent error handling

### auth.global.ts
- Global route guard
- Checks user_info cookie
- Redirects to /login if not authenticated

---

## Role-Based UI

| Role | Admin Panel | Delete Records | See All Records |
|------|-------------|----------------|-----------------|
| Admin | ✅ | ✅ | ✅ |
| Manager | ✅ (Groups only) | ✅ | ✅ |
| User | ❌ | ❌ | Own + Group + Shared |
| Viewer | ❌ | ❌ | Read only |

---

## Currency Formatting

All monetary values displayed with:
- 2 decimal places
- Locale-formatted numbers (1,000,000.00)
- Currency symbol (USD by default)

---

## Loading States

- Skeleton loaders on data fetching
- Button spinners during form submission
- Toast notifications for success/error

---

## Form Validation

- Required field validation
- Numeric range validation
- Date format validation
- Duplicate reference checking
