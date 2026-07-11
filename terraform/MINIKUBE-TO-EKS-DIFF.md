# Minikube → AWS EKS Migration Differences

## Files Jo SAME rahtat (No Change)

| File | Reason |
|---|---|
| `helm/devops-platform/templates/*` | Kubernetes YAML — universal |
| `argocd/applications/*.yaml` | ArgoCD CRD — same everywhere |
| `argocd/projects/*.yaml` | AppProject — same |
| `k8s/namespaces/*.yaml` | Namespace YAML — same |
| `src/`, `app.py` | Application code — no change |
| `Dockerfile` | Container build — same |

## Files Jo CHANGE hotat

| File | Minikube | EKS |
|---|---|---|
| `values-prod.yaml` `image.repository` | `production-grade-devops-platform` | `<ACCOUNT>.dkr.ecr.ap-south-1.amazonaws.com/...` |
| `values-prod.yaml` `image.pullPolicy` | `Never` | `Always` |
| `values-prod.yaml` `ingress.enabled` | `false` | `true` |
| `argocd/applications/prod-application.yaml` `destination.server` | `https://kubernetes.default.svc` | EKS cluster endpoint |

## Commands Jo CHANGE hotat

| Action | Minikube | EKS |
|---|---|---|
| Cluster start | `minikube start` | `terraform apply` |
| kubeconfig | Auto (minikube) | `aws eks update-kubeconfig` |
| Image build | `eval $(minikube docker-env)` + local build | ECR push |
| App access | `kubectl port-forward` | ALB URL (public) |
| Cluster stop | `minikube stop` | `terraform destroy` |

## EKS-Only Components (Minikube madhe navhate)

| Component | Purpose |
|---|---|
| AWS ALB Controller | Ingress → Real Load Balancer |
| ECR | Private Docker Registry |
| IRSA | IAM Roles for Service Accounts |
| AWS Secrets Manager | Production secrets |
| CloudWatch | AWS-native logging |