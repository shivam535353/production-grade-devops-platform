# AWS EKS Deployment Guide
# Run these commands during Final AWS Week

## Phase 1: Infrastructure (Terraform)

```bash
cd terraform/environments/prod

# Initialize
terraform init

# Preview
terraform plan -out=tfplan

# Apply (approx 15-20 min)
terraform apply tfplan
```

## Phase 2: kubeconfig Update

```bash
aws eks update-kubeconfig \
  --region ap-south-1 \
  --name devops-platform-cluster
```

## Phase 3: Verify EKS Connection

```bash
kubectl get nodes
kubectl get namespaces
```

## Phase 4: ECR — Docker Image Push

```bash
# ECR repository create
aws ecr create-repository \
  --repository-name production-grade-devops-platform \
  --region ap-south-1

# ECR login
aws ecr get-login-password --region ap-south-1 | \
  docker login --username AWS \
  --password-stdin \
  <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com

# Image build + tag
docker build -t production-grade-devops-platform:latest .
docker tag production-grade-devops-platform:latest \
  <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/production-grade-devops-platform:latest

# Push
docker push \
  <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/production-grade-devops-platform:latest
```

## Phase 5: AWS ALB Controller Install

```bash
# IAM Policy for ALB Controller
curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.7.2/docs/install/iam_policy.json

aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json

# Helm install ALB Controller
helm repo add eks https://aws.github.io/eks-charts
helm repo update

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=devops-platform-cluster \
  --set serviceAccount.create=true \
  --set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"=<ALB_ROLE_ARN>
```

## Phase 6: ArgoCD Install on EKS (Same as Minikube!)

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods
kubectl get pods -n argocd -w
```

## Phase 7: values-prod.yaml Update

Update these fields:
```yaml
image:
  repository: <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/production-grade-devops-platform
  tag: "latest"

ingress:
  enabled: true
  className: alb
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
```

## Phase 8: ArgoCD Application Update

```bash
# Connect GitHub repo (same as Minikube)
argocd repo add https://github.com/shivam535353/production-grade-devops-platform.git \
  --username shivam535353 \
  --password <PAT>

# Apply applications (same YAML — only cluster URL different)
kubectl apply -f argocd/applications/prod-application.yaml
argocd app sync devops-platform-prod
```

## Phase 9: Verify + Demo Video

```bash
# ALB URL milel
kubectl get ingress -n production

# Browser madhe open kar
# Demo video record kar

# Cleanup (MANDATORY — cost avoid)
terraform destroy
```

## ⚠️ COST WARNING
EKS cluster running aslyavar charges:
- Control plane: ~$0.10/hour
- t3.medium nodes (2): ~$0.09/hour each
- Total: ~$0.30/hour

Demo complete IMMEDIATELY run kara:
terraform destroy