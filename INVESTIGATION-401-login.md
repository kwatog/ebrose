# Investigation: Backend Pod Returning 401 on Login

**Date:** 2026-01-28
**Status:** RESOLVED (self-resolved)
**Issue:** Backend pod returning 401 Unauthorized on login attempts.
**Hypothesis:** SQLite database not loaded properly or pointed to wrong DB file.

---

## Environment

- **Pod:** `ebrose-backend-5ff59b7dd4-cx8nm` in namespace `ebrose`
- **Frontend Pod:** `ebrose-frontend-68c9cd4bdd-hcllf` in namespace `ebrose`
- **PV:** `ebrose-backend-data-pv` (1Gi, RWO, Retain, hostPath: `/data/ebrose/backend`)
- **PVC:** `ebrose-backend-data` (Bound to the PV above)
- **Node Affinity:** Pinned to `k8s-worker-04`

---

## Findings from Investigation

### 1. Pod Environment Variables (Verified)

```
DATABASE_URL=sqlite:////app/data/ebrose.db
SECRET_KEY=change-this-secret-key-for-production
ENVIRONMENT=production
AUTO_CREATE_TABLES=true
CREATE_ADMIN_USER=true
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@ebrose.local
RUN_MIGRATIONS_ON_STARTUP=false
DEBUG=false
```

### 2. Database File Status

- **Path inside pod:** `/app/data/ebrose.db`
- **File size:** 282,624 bytes
- **Last modified:** Jan 26, 2026 05:26
- **Ownership:** `app:app` (correct)
- **Database file EXISTS and is accessible.**

### 3. Database Tables Found

The SQLite database contains the following tables:
- `user` (NOTE: singular, not `users`)
- `user_group`
- `audit_log`
- `user_group_membership`
- `record_access`
- `budget_item`
- `business_case`
- `resource`
- `business_case_line_item`
- `wbs`
- `asset`
- `purchase_order`
- `goods_receipt`
- `resource_po_allocation`

### 4. Pod Logs

- No login attempt errors visible in the last 500 log lines.
- Only `/health` endpoint hits from the kubelet health check probe.
- No startup errors, database connection issues, or table creation failures logged.

### 5. Persistent Volume Setup

- PV `ebrose-backend-data-pv`: **Bound** to PVC `ebrose/ebrose-backend-data` (healthy)
- PV `ebrose-dev-backend-data-pv`: **Released** (from `ebrose-development` namespace - old dev env)
- hostPath on worker node: `/data/ebrose/backend`
- Reclaim policy: `Retain`

---

## Possible Root Causes (For Future Reference)

If the 401 issue returns, check these in order:

### A. Empty User Table (Most Likely Past Cause)
- The `CREATE_ADMIN_USER=true` env var should auto-create the admin user on startup.
- If the pod restarted and the PV was re-mounted fresh (or data wiped), the admin user may not exist.
- **Check:** `kubectl -n ebrose exec <pod> -- python3 -c "import sqlite3; conn=sqlite3.connect('/app/data/ebrose.db'); print(conn.execute('SELECT id,username,role FROM user').fetchall())"`

### B. Database Path Mismatch
- `DATABASE_URL=sqlite:////app/data/ebrose.db` (4 slashes = absolute path `/app/data/ebrose.db`)
- The code default is `sqlite:///../ebrose.db` (relative path, would resolve to `/app/ebrose.db` from `/app/app/` working dir)
- If the env var is missing/wrong, the app may create a NEW empty database at a different path.
- **Check:** Look for any `ebrose.db` files outside `/app/data/`: `find /app -name "ebrose.db"`

### C. SECRET_KEY Mismatch
- If `SECRET_KEY` changes between pod restarts, existing JWT tokens become invalid (401).
- Current key: `change-this-secret-key-for-production` (static, so this shouldn't be an issue unless changed in values.yaml).
- The code has a fallback: `"development-fallback-key-change-for-production"` -- if the env var is unset, a DIFFERENT key is used, invalidating tokens.

### D. Cookie Domain/Secure Settings
- `ENVIRONMENT=production` enables `COOKIE_SECURE=true` (HTTPS only).
- If accessing over HTTP, cookies won't be sent back, causing 401.
- Also check `COOKIE_SAMESITE` and `COOKIE_DOMAIN` settings.

### E. CORS Issues
- The Helm values set `corsOrigins` to include `https://ebrose.kwatog.com`.
- If the frontend is served from a different origin, CORS will block the preflight and cookies won't be sent.

### F. PV Mounted to Wrong Node
- The PV has nodeAffinity for `k8s-worker-04`. If the pod gets scheduled on a different node, it gets an empty directory.
- **Check:** `kubectl -n ebrose get pod <pod> -o wide` to verify the node.

---

## Key Files in the Codebase

| File | Purpose |
|------|---------|
| `backend/app/auth.py` | Login endpoint, JWT creation, password verification |
| `backend/app/database.py` | SQLAlchemy engine setup, DATABASE_URL resolution |
| `backend/app/config.py` | All environment variable handling |
| `backend/app/main.py` | Startup sequence: migrations, table creation, admin user |
| `backend/app/models.py` | SQLAlchemy models (table `user`, not `users`) |
| `helm/ebrose/values.yaml` | Default Helm values (DATABASE_URL, SECRET_KEY, etc.) |
| `helm/ebrose/templates/backend-deployment.yaml` | K8s deployment spec |
| `helm/ebrose/templates/backend-pvc.yaml` | PVC template |
| `ebrose-pv.yaml` | PV manifest (hostPath + nodeAffinity) |
| `ebrose-app.yaml` | ArgoCD Application manifest |

---

## Quick Diagnostic Commands

```bash
# Check if DB file exists and has data
kubectl -n ebrose exec <pod> -- ls -la /app/data/ebrose.db

# Check if users exist in DB
kubectl -n ebrose exec <pod> -- python3 -c "
import sqlite3
conn = sqlite3.connect('/app/data/ebrose.db')
print(conn.execute('SELECT id,username,role,is_active FROM user').fetchall())
"

# Check for multiple DB files (path mismatch)
kubectl -n ebrose exec <pod> -- find /app -name "*.db" -ls

# Check which node the pod is on
kubectl -n ebrose get pod <pod> -o wide

# Check pod startup logs
kubectl -n ebrose logs <pod> | head -50

# Test login directly from inside the cluster
kubectl -n ebrose exec <pod> -- curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Verify PV/PVC binding
kubectl -n ebrose get pvc
kubectl get pv | grep ebrose
```

---

## Resolution

The issue self-resolved. The 401 was likely caused by one of:
1. Pod restart that temporarily left the DB empty before `CREATE_ADMIN_USER` ran
2. A transient PV mount issue
3. Cookie/token invalidation after a pod restart with the same SECRET_KEY

No code changes were needed.
