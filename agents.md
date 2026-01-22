# AI Agent Instructions for Ebrose Project

This file contains instructions for AI assistants (Claude, ChatGPT, Copilot, etc.) working on the Ebrose codebase.

## Git Commit Guidelines

### Commit Message Format

Use conventional commit format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Maintenance tasks

### Commit Message Footer

**DO NOT** add AI attribution footers to commit messages. Keep commits clean and professional:

```
# ✅ GOOD - Clean commit message
feat: Add user profile management

Implement user profile editing with password change functionality.
Includes validation and security checks.
```

```
# ❌ BAD - Don't add AI attribution
feat: Add user profile management

Implement user profile editing with password change functionality.

🤖 Generated with [AI Tool]
Co-Authored-By: AI Assistant <...>
```

## Code Style Guidelines

### Python (Backend)
- Use type hints for all function parameters and return types
- Follow PEP 8 naming conventions
- Use descriptive variable names
- Add docstrings for complex functions
- Prefer Pydantic v2 APIs: `model_dump()`, `model_validate()`, `ConfigDict`

### TypeScript/Vue (Frontend)
- Use Composition API for all Vue components
- Use TypeScript interfaces for complex types
- Follow Vue 3 best practices
- Use Heroicons for all icons (no emojis)
- Prefer `composables/` for shared logic

## Testing Requirements

### Backend Tests
- Run tests before committing: `pytest tests/ -v`
- Maintain test coverage for new features
- Use fixtures for database setup
- Test access control for all endpoints

### Frontend Tests
- Unit tests: `npm run test:unit`
- E2E tests: Use Docker Compose for consistency
- Update snapshots when UI changes

## Security Guidelines

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Follow password policy requirements (8+ chars, mixed case, numbers, special chars)
- Implement proper access control checks
- Validate all user inputs

## Database Changes

- Update models in `backend/app/models.py`
- Update Pydantic schemas in `backend/app/schemas.py`
- Recreate database with `python reset_and_seed.py`
- Use timezone-aware datetime objects (`datetime.now(timezone.utc)`)

## Common Patterns

### Creating API Endpoints
1. Define Pydantic schemas
2. Add router endpoint with proper access control
3. Implement CRUD logic with audit logging
4. Add tests for all access scenarios
5. Update frontend API client

### Adding Frontend Pages
1. Create page in `pages/` directory
2. Use base components from `components/base/`
3. Implement API calls with `useApiFetch` composable
4. Add proper error handling
5. Update navigation if needed

## Container Image Management

### Building Images

The system uses **Podman** (not Docker) for container operations:

```bash
# Build backend image
podman build -t ebrose-backend:latest -f backend/Dockerfile backend/

# Build frontend image
podman build -t ebrose-frontend:latest -f frontend/Dockerfile frontend/
```

### Deploying to Worker Nodes

When deploying to Kubernetes worker nodes:

1. **Save images to tar files:**
   ```bash
   podman save -o /tmp/ebrose-backend.tar localhost/ebrose-backend:latest
   podman save -o /tmp/ebrose-frontend.tar localhost/ebrose-frontend:latest
   ```

2. **Transfer to worker nodes (use IP addresses):**
   ```bash
   scp /tmp/ebrose-backend.tar /tmp/ebrose-frontend.tar 192.168.18.66:/tmp/
   scp /tmp/ebrose-backend.tar /tmp/ebrose-frontend.tar 192.168.18.68:/tmp/
   ```

3. **Load images on worker nodes:**
   - Ensure user is in `containerd` group: `sudo usermod -aG containerd <username>`
   - Start new shell session to activate group: `newgrp containerd`
   - Import images:
     ```bash
     ctr -n k8s.io images import /tmp/ebrose-backend.tar
     ctr -n k8s.io images import /tmp/ebrose-frontend.tar
     ```

4. **Verify images:**
   ```bash
   ctr -n k8s.io images ls | grep ebrose
   ```

### Worker Node Permissions

The containerd socket (`/run/containerd/containerd.sock`) is owned by `root:containerd`. Users need:
- Group membership: `sudo usermod -aG containerd <username>`
- New shell session after group change: `newgrp containerd` or logout/login

## Kubernetes Deployment

### Helm Deployment

```bash
# Deploy to specific environment
helm upgrade --install ebrose ./helm/ebrose \
  -n ebrose --create-namespace \
  -f ./helm/ebrose/values-<environment>.yaml

# Available environments:
# - values-development.yaml
# - values-staging.yaml
# - values-production.yaml
# - values-minikube.yaml
```

### Current Worker Nodes

- **k8s-worker-01**: 192.168.18.66 (containerd 2.2.1)
- **k8s-worker-04**: 192.168.18.68 (containerd 2.2.1)
- **k8s-ctrl**: 192.168.18.73 (control plane)

## Helpful Commands

```bash
# Backend development
source backend/venv/bin/activate
cd backend
python -m uvicorn app.main:app --reload

# Frontend development
cd frontend
npm run dev

# Database reset
cd backend
python reset_and_seed.py

# Run all tests
cd backend && pytest tests/ -v
cd frontend && npm run test:unit

# Kubernetes operations
kubectl get nodes -o wide
kubectl get pods -n ebrose
kubectl logs -n ebrose <pod-name>
```

## Notes for AI Assistants

- Read existing code patterns before implementing new features
- Ask for clarification on ambiguous requirements
- Prioritize code consistency with existing patterns
- Update documentation when adding major features
- Keep commits focused and atomic
- For Claude Code CLI: See `claude.md` for specific workflows and best practices
