# ArgoCD GitOps Configuration

This directory contains all ArgoCD manifests for the production-grade-devops-platform project.

## Directory Structure
argocd/
├── install/          → ArgoCD installation reference documentation
├── projects/         → ArgoCD AppProject definitions (RBAC, access control)
└── applications/     → ArgoCD Application definitions (dev + prod)

## Repository Strategy

This project uses a **Mono-Repo** strategy where:
- `app.py`, `Dockerfile`, `src/` → Application code (CI responsibility)
- `helm/` → Helm chart (packaging)
- `argocd/` → GitOps manifests (ArgoCD watches this + helm/)

In production, these would typically be split into 2-3 separate repositories.

## Environments

| Environment | Namespace | Values File | ArgoCD App |
|---|---|---|---|
| Development | dev | values-dev.yaml | dev-application.yaml |
| Production | production | values-prod.yaml | prod-application.yaml |

## How to Apply

```bash
# Apply AppProject first
kubectl apply -f argocd/projects/devops-platform-project.yaml

# Apply Applications
kubectl apply -f argocd/applications/dev-application.yaml
kubectl apply -f argocd/applications/prod-application.yaml
```

## ArgoCD UI Access

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
Open: https://localhost:8080