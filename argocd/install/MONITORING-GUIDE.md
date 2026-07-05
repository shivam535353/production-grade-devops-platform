# ArgoCD Monitoring Guide

## Quick Health Check Commands

```bash
# All apps status
argocd app list

# Specific app detailed health
argocd app get devops-platform-dev

# Resource-level health
argocd app resources devops-platform-dev

# Deployment history (audit trail)
argocd app history devops-platform-dev

# Kubernetes events
kubectl get events -n dev --sort-by='.lastTimestamp'

# Notification logs
kubectl logs -n argocd deployment/argocd-notifications-controller --tail=20
```

## Health Status Reference

| Status | Meaning | Action |
|---|---|---|
| `Healthy` | सगळं ठीक | Nothing |
| `Progressing` | Deploy होतंय | थांब |
| `Degraded` | कुठेतरी problem | Logs check |
| `Suspended` | Manually paused | Resume if needed |
| `Missing` | Resource नाही | Sync कर |

## Sync Status Reference

| Status | Meaning | Action |
|---|---|---|
| `Synced` | Git == Cluster | Nothing |
| `OutOfSync` | Drift detected | Review + Sync |
| `Unknown` | Cannot compare | ArgoCD check |

## Notification Triggers Configured

- `on-sync-succeeded` → ✅ Deploy success
- `on-sync-failed` → ❌ Deploy failure  
- `on-health-degraded` → ⚠️ App unhealthy
- `on-deployed` → 🚀 New deployment complete