# ArgoCD Patterns Guide

## Pattern 1: App of Apps

### Structure
root-app (watches argocd/applications/)
├── devops-platform-dev
└── devops-platform-prod

### When to Use
- Different apps (frontend, backend, database) same cluster वर
- Team-wise separation (team A cha app, team B cha app)
- Manual control per app हवं (प्रत्येक app independently manage)

### How to Add New App
1. `argocd/applications/new-app.yaml` create kar
2. `git push` कर
3. root-app automatically new Application create करेल

---

## Pattern 2: ApplicationSet

### Structure
devops-platform-appset
generators: [dev, staging, prod]
→ automatically 3 Applications generate करतो

### When to Use
- Same app, multiple environments
- Multiple clusters (cluster generator)
- Dynamic environment provisioning (PR-based environments)

### How to Add New Environment
1. `generators.list.elements` मध्ये नवीन entry add कर
2. `git push` + `kubectl apply` कर
3. नवीन Application automatically created!

---

## Pattern 3: Progressive Delivery (Introduction)

### Blue-Green Deployment
Blue (current v1) → 100% traffic
Green (new v2) → 0% traffic (testing)
Switch → Green 100%, Blue 0%
Rollback → Switch back instantly

### Canary Deployment
v1 → 90% traffic
v2 → 10% traffic (canary)
Monitor metrics
Gradually increase v2 traffic
Full rollout if healthy

**Tools:** Argo Rollouts (ArgoCD ecosystem), Flagger, Istio
**Phase:** Advanced topic — AWS EKS final week मध्ये cover करू

---

## Interview Reference

| Pattern | Scale | Complexity | Best For |
|---|---|---|---|
| Manual apply | 1-5 apps | Low | Learning |
| App of Apps | 5-50 apps | Medium | Small teams |
| ApplicationSet | 50+ apps | Medium | Platform teams |
| App of Apps + AppSet | Enterprise | High | Large orgs |