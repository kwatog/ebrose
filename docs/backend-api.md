# Backend API Reference

Base URL (local): `http://localhost:8000`
Interactive Docs: `http://localhost:8000/docs`

## Authentication (`/auth`)

### POST /auth/login
Authenticate user and receive JWT token.

**Request:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "Admin"
  }
}
```

**Cookies Set:**
- `access_token`: HttpOnly JWT (15 min)
- `refresh_token`: HttpOnly JWT (7 days)

---

### POST /auth/logout
Clear authentication cookies.

---

### GET /auth/me
Get current authenticated user.

---

## Users (`/users`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/` | List users (Admin only) |
| GET | `/users/{id}` | Get user by ID |
| PUT | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user (Admin only) |

---

## User Groups (`/user-groups`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/user-groups/` | List groups |
| POST | `/user-groups/` | Create group |
| GET | `/user-groups/{id}` | Get group |
| PUT | `/user-groups/{id}` | Update group |
| DELETE | `/user-groups/{id}` | Delete group |
| GET | `/user-groups/{id}/members` | List members |
| POST | `/user-groups/{id}/members` | Add member |
| DELETE | `/user-groups/{id}/members/{user_id}` | Remove member |

---

## Budget Items (`/budget-items`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/budget-items/` | List (filtered by access) |
| POST | `/budget-items/` | Create |
| GET | `/budget-items/{id}` | Get by ID |
| PUT | `/budget-items/{id}` | Update |
| DELETE | `/budget-items/` | Delete (Manager+) |

**Query Parameters:**
- `skip`, `limit`: Pagination
- `fiscal_year`: Filter by year
- `owner_group_id`: Filter by group

---

## Business Cases (`/business-cases`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/business-cases/` | List (hybrid access) |
| POST | `/business-cases/` | Create |
| GET | `/business-cases/{id}` | Get by ID |
| PUT | `/business-cases/{id}` | Update |
| DELETE | `/business-cases/{id}` | Delete |

**Hybrid Access:**
- Creator has Read always, Write for Draft only
- Access via linked line items (budget items)
- Explicit RecordAccess grants

---

## Business Case Line Items (`/business-case-line-items`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/business-case-line-items/` | List |
| POST | `/business-case-line-items/` | Create |
| GET | `/business-case-line-items/{id}` | Get by ID |
| PUT | `/business-case-line-items/{id}` | Update |
| DELETE | `/business-case-line-items/{id}` | Delete |

Links BudgetItem to BusinessCase.

---

## WBS (`/wbs`)

Work Breakdown Structure items.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/wbs/` | List |
| POST | `/wbs/` | Create |
| GET | `/wbs/{id}` | Get by ID |
| PUT | `/wbs/{id}` | Update |
| DELETE | `/wbs/{id}` | Delete |

**Inherits:** owner_group_id from BusinessCaseLineItem

---

## Assets (`/assets`)

Fixed assets tracking.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/assets/` | List |
| POST | `/assets/` | Create |
| GET | `/assets/{id}` | Get by ID |
| PUT | `/assets/{id}` | Update |
| DELETE | `/assets/{id}` | Delete |

**Inherits:** owner_group_id from WBS

---

## Purchase Orders (`/purchase-orders`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/purchase-orders/` | List |
| POST | `/purchase-orders/` | Create |
| GET | `/purchase-orders/{id}` | Get by ID |
| PUT | `/purchase-orders/{id}` | Update |
| DELETE | `/purchase-orders/{id}` | Delete |

**Inherits:** owner_group_id from Asset

---

## Goods Receipts (`/goods-receipts`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/goods-receipts/` | List |
| POST | `/goods-receipts/` | Create |
| GET | `/goods-receipts/{id}` | Get by ID |
| PUT | `/goods-receipts/{id}` | Update |
| DELETE | `/goods-receipts/{id}` | Delete |

**Inherits:** owner_group_id from PurchaseOrder

---

## Resources (`/resources`)

Vendor resources for allocation.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/resources/` | List |
| POST | `/resources/` | Create |
| GET | `/resources/{id}` | Get by ID |
| PUT | `/resources/{id}` | Update |
| DELETE | `/resources/{id}` | Delete |

---

## Resource Allocations (`/allocations`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/allocations/` | List |
| POST | `/allocations/` | Create |
| GET | `/allocations/{id}` | Get by ID |
| PUT | `/allocations/{id}` | Update |
| DELETE | `/allocations/{id}` | Delete |

---

## Record Access (`/record-access`)

Grant/revoke permissions.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/record-access/` | List grants |
| POST | `/record-access/` | Create grant |
| GET | `/record-access/{id}` | Get grant |
| PUT | `/record-access/{id}` | Update grant |
| DELETE | `/record-access/{id}` | Delete grant |

**Access Levels:** Read, Write, Full

---

## Audit Logs (`/audit-logs`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/audit-logs/` | List (Admin only) |
| GET | `/audit-logs/{id}` | Get entry |

**Query Parameters:**
- `user_id`: Filter by user
- `table_name`: Filter by entity
- `start_date`, `end_date`: Date range

---

## Health (`/health`)

Service health check.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-01-01T00:00:00"
}
```

---

## Error Responses

| Status | Meaning | Response |
|--------|---------|----------|
| 401 | Unauthorized | `{"detail": "Invalid credentials"}` |
| 403 | Forbidden | `{"detail": "Insufficient permissions"}` |
| 404 | Not Found | `{"detail": "Record not found"}` |
| 400 | Bad Request | `{"detail": "Error message"}` |

---

## Rate Limiting

No rate limiting currently implemented. Consider adding for production.
