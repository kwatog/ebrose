# Minimal ArgoCD Setup

Headless ArgoCD for GitOps without UI/API.

## Quick Install

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm install argocd argo/argo-cd \
  --namespace argocd --create-namespace \
  --set server.replicas=0 \
  --set redis.enabled=true \
  --set applicationsetController.enabled=false \
  --set notificationsController.enabled=false \
  --set dex.enabled=false
```

## After Installation Fix

The controller needs `server.secretkey` for Redis authentication:

```bash
SECRET_KEY=$(openssl rand -base64 16)
kubectl delete secret argocd-secret -n argocd
kubectl create secret generic argocd-secret -n argocd --from-literal=server.secretkey="$SECRET_KEY"
kubectl rollout restart statefulset argocd-application-controller -n argocd
```

## Create AppProject

Required to allow resources in the project:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: default
  namespace: argocd
spec:
  destinations:
    - namespace: '*'
      server: https://kubernetes.default.svc
  sourceRepos:
    - '*'
  clusterResourceWhitelist:
    - group: ''
      kind: PersistentVolume
```

```bash
kubectl apply -f default-project.yaml
```

## Create Application

Monitor a helm chart or kustomize app:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ebrose
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/kwatog/ebrose
    targetRevision: HEAD
    path: helm/ebrose
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

```bash
kubectl apply -f ebrose-app.yaml
```

## Pods

- `argocd-application-controller` - reconciles applications
- `argocd-repo-server` - fetches git/helm and generates manifests
- `argocd-redis` - caching

## Usage

Without the API/UI, all management is done via `kubectl`:

```bash
# View applications
kubectl get application -n argocd

# View application status
kubectl get application ebrose -n argocd

# Sync manually
kubectl patch application ebrose -n argocd \
  --type merge -p '{"operation":{"sync":{}}}'

# Delete application
kubectl delete application ebrose -n argocd
```

## Auto-Sync

With `automated` sync policy enabled:
- Push to git → ArgoCD syncs automatically
- `selfHeal: true` → reverts drift automatically
- `prune: true` → deletes resources removed from git
