# Ebrose - Procurement Tracking System

Ebrose is an enterprise-grade procurement and budget tracking system built with **FastAPI** (backend) and **Nuxt 4** (frontend). It provides comprehensive audit logging, role-based access control, and owner-group inheritance for secure data management.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Ebrose System                             │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (Nuxt 4)                                              │
│  ├── Vue 3 Composition API                                      │
│  ├── Pinia State Management                                     │
│  ├── Vue Router with Auth Guards                                │
│  └── 10 Entity Pages (Budget → Allocation)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend (FastAPI)                                              │
│  ├── 14 Data Models with Audit Tracking                         │
│  ├── JWT Authentication (HttpOnly Cookies)                      │
│  ├── Owner-Group Access Scoping                                 │
│  ├── Hybrid BusinessCase Access (Creator + Line Items)          │
│  └── Comprehensive Record-Level Permissions                     │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │   SQLite     │ │   Redis      │ │  CI/CD       │
      │   (Dev)      │ │  (Session)   │ │  Jenkins     │
      └──────────────┘ └──────────────┘ └──────────────┘
```

## Key Features

### 🔐 Security & Access Control
- **JWT Authentication** with HttpOnly cookies
- **4-Tier Roles**: Admin, Manager, User, Viewer
- **Owner-Group Access Scoping**: Filter records by group membership
- **Record-Level Permissions**: Grant explicit access to users/groups
- **Hybrid BusinessCase Access**: Creator + Line Items + Explicit Grants

### 📊 Data Model (14 Entities)
| Entity | Purpose | Parent |
|--------|---------|--------|
| BudgetItem | Annual budget allocations | - |
| BusinessCase | Procurement requests | - |
| BusinessCaseLineItem | Budget-to-BC linking | BudgetItem, BusinessCase |
| WBS | Work breakdown structure | BusinessCaseLineItem |
| Asset | Fixed assets tracking | WBS |
| PurchaseOrder | PO management | Asset |
| GoodsReceipt | Receipt tracking | PurchaseOrder |
| Resource | Vendor resources | - |
| ResourcePOAllocation | Resource-to-PO linking | Resource, PurchaseOrder |
| User | System users | - |
| UserGroup | Group management | - |
| RecordAccess | Permission grants | - |
| AuditLog | Change tracking | - |
| Alert | System notifications | - |

### 💰 Money Handling
All currency fields use **Decimal(Numeric(10,2))** with automatic 2dp rounding:
- `budget_amount` (BudgetItem)
- `requested_amount` (BusinessCaseLineItem)
- `total_amount` (PurchaseOrder)
- `amount` (GoodsReceipt)
- `cost_per_month` (Resource)
- `expected_monthly_burn` (ResourcePOAllocation)

## Quick Links

- [Backend API Reference](backend-api.md)
- [Frontend Pages](frontend-pages.md)
- [Architecture & ADRs](architecture.md)
- [Deployment & Operations](operations.md)

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- SQLite (dev) or PostgreSQL (prod)

### Installation

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
npm run dev
```

### Environment Variables

```bash
# Required for production
SECRET_KEY=<your-secret-key>
ADMIN_PASSWORD=<admin-password>
ENVIRONMENT=production

# Optional
ALLOWED_ORIGINS=http://localhost:3000
ACCESS_TOKEN_EXPIRE_MINUTES=15
DATABASE_URL=postgresql://user:pass@localhost:5432/ebrose
```

## API Documentation

Access interactive API docs at: **http://localhost:8000/docs**

## Testing

```bash
# Backend tests
cd backend
source venv/bin/activate
python3 -m pytest tests/ -v

# Frontend E2E tests
cd frontend
npm run test:e2e:playwright
```

## Deployment

- **Local**: `docker-compose up --build`
- **Kubernetes**: See [Operations](operations.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.
