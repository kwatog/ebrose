# Deployment & Operations

## Environments

### Development
```bash
# Docker Compose (recommended)
docker-compose up --build

# Or manually
cd backend && source venv/bin/activate && uvicorn app.main:app --reload
cd frontend && npm run dev
```

**Configuration:** `values-development.yaml`

### Staging
```bash
helm upgrade --install ebrose-staging ./helm/ebrose \
  --namespace ebrose-staging \
  --create-namespace \
  -f ./helm/ebrose/values-staging.yaml
```

### Production
```bash
helm upgrade --install ebrose-prod ./helm/ebrose \
  --namespace ebrose-production \
  --create-namespace \
  -f ./helm/ebrose/values-production.yaml
```

**Required Environment Variables:**
```bash
SECRET_KEY=<strong-random-key>     # Required
ADMIN_PASSWORD=<admin-password>    # Required
ENVIRONMENT=production             # Required for strict mode
ALLOWED_ORIGINS=https://your-domain.com
DATABASE_URL=postgresql://...
```

---

## Kubernetes Architecture

```
┌────────────────────────────────────────────────────────────┐
│                 ebrose Namespace                            │
├────────────────────────────────────────────────────────────┤
│  ebrose-frontend                                           │
│  ├── Deployment: 2 replicas                                │
│  ├── Service: ClusterIP :3000                              │
│  └── Ingress: / -> ebrose-frontend:3000                    │
├────────────────────────────────────────────────────────────┤
│  ebrose-backend                                            │
│  ├── Deployment: 3 replicas                                │
│  ├── Service: ClusterIP :8000                              │
│  └── Ingress: /api -> ebrose-backend:8000                  │
├────────────────────────────────────────────────────────────┤
│  PersistentVolumeClaim                                     │
│  └── SQLite (dev) / PostgreSQL (prod)                      │
└────────────────────────────────────────────────────────────┘
```

---

## Helm Configuration

### Backend Values
```yaml
backend:
  replicaCount: 3
  image:
    repository: registry/ebrose/backend
    tag: v1.0.0
  env:
    SECRET_KEY: required-in-production
    ADMIN_PASSWORD: required-in-production
    ENVIRONMENT: production
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
```

### Frontend Values
```yaml
frontend:
  replicaCount: 2
  image:
    repository: registry/ebrose/frontend
    tag: v1.0.0
  env:
    API_URL: https://api.ebrose.local
```

---

## Health Checks

### Backend Endpoint
```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "database": "connected"}
```

### Kubernetes Probes
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
```

---

## Scaling

### Manual
```bash
kubectl scale deployment ebrose-backend --replicas=5 -n ebrose-production
```

### HPA
```bash
helm upgrade ebrose ./helm/ebrose \
  --reuse-values \
  --set backend.autoscaling.enabled=true
```

---

## Monitoring

### Recommended Stack
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **ELK Stack**: Logging
- **Jaeger**: Tracing

### Key Metrics
- Request latency (p50, p95, p99)
- Error rate (5xx)
- Database query time
- Auth success/failure rate
- Resource utilization

---

## Backup & Recovery

### Database Backup
```bash
# PostgreSQL
pg_dump -h localhost -U postgres ebrose > backup_$(date +%Y%m%d).sql

# Cron schedule (2 AM daily)
0 2 * * * pg_dump -h localhost -U postgres ebrose > /backups/ebrose_$(date +\%Y\%m\%d).sql
```

### Restore
```bash
psql -h localhost -U postgres -d ebrose < backup_20250101.sql
```

---

## Troubleshooting

### Pod Crashes
```bash
kubectl logs ebrose-backend-xxx -n ebrose-production --previous
```

### Database Issues
```bash
kubectl exec -it ebrose-backend-xxx -n ebrose-production -- sh
curl http://localhost:8000/health
```

### Auth Failures
- Verify `SECRET_KEY` is set
- Check `ADMIN_PASSWORD` env var
- Ensure `ENVIRONMENT=production`

---

## Security Checklist

- [ ] `SECRET_KEY` set to strong random value (32+ chars)
- [ ] `ADMIN_PASSWORD` set for initial admin
- [ ] `ENVIRONMENT=production` for strict mode
- [ ] TLS/SSL configured on ingress
- [ ] Database credentials in Kubernetes Secrets
- [ ] Network policies configured
- [ ] Regular database backups
- [ ] Audit logging enabled
- [ ] Access logs retained
- [ ] Dependency vulnerabilities addressed

---

## CI/CD Pipeline (Jenkins)

1. **Build**: Compile, run tests
2. **Security Scan**: Dependency vulnerabilities
3. **Containerize**: Build Docker images
4. **Push**: Push to registry
5. **Deploy Dev**: Development environment
6. **Integration Tests**: E2E tests
7. **Deploy Staging**: Staging environment
8. **Manual Approval**: Production gate
9. **Deploy Production**: Production environment
10. **Smoke Tests**: Verify health

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Production | JWT signing key |
| `ADMIN_PASSWORD` | Production | Initial admin password |
| `ENVIRONMENT` | Production | Set to "production" |
| `DATABASE_URL` | No | PostgreSQL connection |
| `ALLOWED_ORIGINS` | No | CORS origins (comma-separated) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token lifetime (default: 15) |
| `ADMIN_USERNAME` | No | Initial admin username |
| `ADMIN_EMAIL` | No | Initial admin email |
| `ADMIN_FULL_NAME` | No | Initial admin full name |
