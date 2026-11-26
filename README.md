# Production-Grade DevOps Platform

<p align="center">
  <strong>Multi-environment CI/CD, GitOps delivery, Kubernetes orchestration and cloud-native observability</strong>
</p>

<p align="center">
  <a href="https://github.com/shivam535353/production-grade-devops-platform"><img src="https://img.shields.io/badge/GitHub-Repository-181717?logo=github" alt="GitHub repository"></a>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12">
  <img src="https://img.shields.io/badge/Flask-3.1-000000?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Docker-Multi--stage-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Kubernetes-EKS%20%7C%20Minikube-326CE5?logo=kubernetes&logoColor=white" alt="Kubernetes">
  <img src="https://img.shields.io/badge/Helm-Charts-0F1689?logo=helm" alt="Helm">
  <img src="https://img.shields.io/badge/Argo%20CD-GitOps-EF7B4D?logo=argo" alt="Argo CD">
  <img src="https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?logo=githubactions&logoColor=white" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform&logoColor=white" alt="Terraform">
  <img src="https://img.shields.io/badge/Prometheus-Monitoring-E6522C?logo=prometheus&logoColor=white" alt="Prometheus">
  <img src="https://img.shields.io/badge/Grafana-Dashboards-F46800?logo=grafana&logoColor=white" alt="Grafana">
</p>

**Author:** Shivam Gadilkar  
**Repository:** [shivam535353/production-grade-devops-platform](https://github.com/shivam535353/production-grade-devops-platform)  
**Cloud region used for the EKS demonstration:** `ap-south-1` (Asia Pacific — Mumbai)

---

## Table of contents

- [Overview](#overview)
- [Problem statement](#problem-statement)
- [Architecture](#architecture)
- [End-to-end workflow](#end-to-end-workflow)
- [Technology stack](#technology-stack)
- [Repository structure](#repository-structure)
- [Implementation phases and proof of work](#implementation-phases-and-proof-of-work)
- [Application endpoints](#application-endpoints)
- [Run locally](#run-locally)
- [Run with Docker](#run-with-docker)
- [Kubernetes and Helm deployment](#kubernetes-and-helm-deployment)
- [AWS deployment notes](#aws-deployment-notes)
- [Security design](#security-design)
- [Engineering challenges and learnings](#engineering-challenges-and-learnings)
- [Future improvements](#future-improvements)
- [Cost and lifecycle note](#cost-and-lifecycle-note)
- [License](#license)

## Overview

The **Production-Grade DevOps Platform** is an end-to-end engineering project that demonstrates how to package a Python web application, validate it through CI, scan source code and container artifacts, publish versioned images, and deploy Kubernetes workloads using Helm and Argo CD.

The platform was developed incrementally: first as a Flask application and Docker container, then on local Kubernetes (Minikube), and finally as an AWS EKS demonstration. It includes GitOps-managed development/production application definitions, infrastructure-as-code, application metrics, Prometheus/Grafana observability, horizontal pod autoscaling and Kubernetes network-policy validation.

The project emphasizes repeatable delivery, explicit configuration, least-privilege cloud access, health checks, and operational evidence rather than a one-command demo.

## Problem statement

A working application is only one part of a reliable delivery platform. Teams also need a repeatable way to:

- build consistent container images;
- catch code and security issues before publishing;
- promote immutable image references through environments;
- keep Kubernetes desired state in version control;
- observe service health and workload behavior;
- scale application replicas as demand changes; and
- provision cloud infrastructure in a reproducible, reviewable way.

This repository brings those practices together in one demonstrable workflow.

## Architecture

The diagram below shows the main delivery path and the two runtime targets used in the project: a local Minikube environment and an AWS EKS demonstration environment.

```mermaid
flowchart TB
    DEV["Developer"] --> GIT["Git repository<br/>GitHub"]
    GIT --> CI["GitHub Actions<br/>CI workflow"]

    subgraph PIPELINE["Continuous integration and image delivery"]
      CI --> TEST["Lint + Flask endpoint tests<br/>Python 3.12"]
      TEST --> SEC["Security checks<br/>Gitleaks + Trivy filesystem scan"]
      SEC --> BUILD["Reusable Docker build<br/>Buildx + OCI labels"]
      BUILD --> GHCR["GitHub Container Registry"]
      BUILD --> OIDC["GitHub OIDC identity"]
      OIDC --> IAM["AWS IAM role<br/>short-lived credentials"]
      IAM --> ECR["Amazon ECR"]
      GHCR --> VERIFY["Pull image + container health smoke test"]
      ECR --> VERIFY
    end

    subgraph GITOPS["GitOps configuration and reconciliation"]
      CI --> VALUES["Helm values in Git<br/>values-dev.yaml / values-eks.yaml"]
      VALUES --> ARGO["Argo CD"]
      ARGO --> HELM["Helm chart<br/>desired Kubernetes state"]
    end

    subgraph LOCAL["Local validation"]
      MINI["Minikube cluster"] --> HELMLOCAL["Helm release"]
      HELMLOCAL --> APPLOCAL["Flask application Pods"]
    end

    subgraph AWS["AWS EKS demonstration environment"]
      TF["Terraform"] --> VPC["VPC / subnets / routing"]
      TF --> EKS["Amazon EKS cluster"]
      TF --> STATE["Amazon S3<br/>Terraform remote state"]
      EKS --> ALBCTRL["AWS Load Balancer Controller"]
      ALBCTRL --> ALB["Application Load Balancer<br/>HTTP listener"]
      HELM --> DEPLOY["Kubernetes Deployment"]
      DEPLOY --> PODS["Flask Pods<br/>Gunicorn :5000"]
      ALB --> SVC["Kubernetes Service"]
      SVC --> PODS
      HPA["Horizontal Pod Autoscaler<br/>CPU target 60%, 2–6 replicas"] --> DEPLOY
      SECRET["Kubernetes Secret<br/>created outside Helm values"] --> PODS
      NETPOL["NetworkPolicy"] --> PODS
      PROM["Prometheus"] --> PODS
      GRAF["Grafana dashboards"] --> PROM
      SM["ServiceMonitor"] --> PROM
    end

    HELM --> HELMLOCAL
    HELM --> DEPLOY
    VERIFY -. "image publication verified" .-> VALUES
    PODS --> METRICS["/metrics/prometheus"]
    METRICS --> PROM
```

### Architecture notes

- **CI is the quality gate:** the workflow runs Python lint/format checks and Flask endpoint tests before the security and image-delivery stages.
- **Image publication:** the reusable Docker workflow builds a Linux AMD64 image and publishes to GHCR and, when configured, Amazon ECR. AWS authentication uses GitHub's OIDC identity to assume a scoped IAM role rather than storing long-lived AWS access keys in GitHub secrets.
- **GitOps:** Argo CD observes the repository and reconciles the Helm chart into Kubernetes. The current `gitops-update` job updates `helm/devops-platform/values-dev.yaml` on a push to `main`; the EKS demo configuration is represented separately by `values-eks.yaml`.
- **Runtime:** the Flask application runs in Kubernetes Pods behind a Service. The EKS demo used an AWS Application Load Balancer through the AWS Load Balancer Controller.
- **Observability and scaling:** a ServiceMonitor exposes application metrics to Prometheus; Grafana visualizes the metrics; the HPA uses CPU utilization to adjust replicas.
- **Infrastructure state:** Terraform remote state is stored in an S3 backend. The EKS demo stack was destroyed after validation to avoid ongoing cloud charges; see [Cost and lifecycle note](#cost-and-lifecycle-note).

## End-to-end workflow

1. A developer pushes code or opens a pull request against `main`.
2. GitHub Actions checks out the repository, installs Python dependencies, runs `flake8`, checks formatting with Black and tests the Flask endpoints.
3. The security job scans repository history with Gitleaks and the filesystem with Trivy (CRITICAL severity, ignoring unfixed findings).
4. The reusable Docker workflow builds the image with Buildx. For push events it authenticates to GHCR and uses GitHub OIDC to assume the configured AWS role for ECR publishing.
5. The verification job pulls the SHA-tagged image, starts a container and checks `/health`.
6. On a push to `main`, the GitOps update job changes the image tag in `helm/devops-platform/values-dev.yaml` and pushes the change. Argo CD can then reconcile the updated development Helm release.
7. The EKS demonstration used a separate EKS Helm values file and Argo CD application configuration. The EKS image/configuration update should be treated as a separately controlled deployment step, not as an automatic result of the `values-dev.yaml` update job.

## Technology stack

| Area | Technologies | Purpose |
|---|---|---|
| Application | Python 3.12, Flask 3.1, Werkzeug | Web application and API endpoints |
| Production serving | Gunicorn | WSGI application server |
| Containerization | Docker, multi-stage Dockerfile | Reproducible, smaller runtime image; non-root execution |
| Local orchestration | Kubernetes, Minikube | Local cluster development and validation |
| Packaging | Helm | Parameterized Kubernetes manifests and environment-specific values |
| GitOps | Argo CD | Continuous reconciliation from Git |
| CI/CD | GitHub Actions, reusable workflow, Docker Buildx | Tests, security checks, image build and publishing |
| Image registries | GHCR, Amazon ECR | Versioned container image storage |
| Infrastructure as code | Terraform | AWS infrastructure and IAM/ECR provisioning |
| AWS | EKS, VPC, IAM, S3, ECR, Application Load Balancer | Managed Kubernetes and cloud networking |
| Ingress | AWS Load Balancer Controller | ALB provisioning from Kubernetes Ingress |
| Metrics | Prometheus, prometheus-flask-exporter, ServiceMonitor | Application and cluster metrics collection |
| Dashboards | Grafana | Operational dashboards and visualization |
| Security | Gitleaks, Trivy, Kubernetes SecurityContext, NetworkPolicy | Secret scanning, vulnerability scanning and workload/network hardening |
| Secret workflow | Kubernetes Secret / Sealed Secrets tooling | Keep runtime secret values out of Helm values and ordinary source configuration |

## Repository structure

The following is a focused map of the repository's main implementation areas.

```text
production-grade-devops-platform/
├── .github/
│   └── workflows/
│       ├── ci-cd.yml
│       └── reusable-docker-build.yml
├── argocd/                   # Argo CD Application and GitOps configuration
├── charts/
│   └── templates/            # Kubernetes chart/template assets
├── docs/
│   ├── evidence/             # Captured CLI evidence and resource snapshots
│   └── screenshots/          # Phase-by-phase implementation screenshots
├── eks-addons/               # EKS add-on configuration
├── helm/
│   └── devops-platform/      # Application Helm chart and values files
├── k8s/                      # Kubernetes manifests and supporting resources
├── loadtest/                 # Load-test assets
├── monitoring/               # Prometheus/Grafana and monitoring values/rules
├── src/
│   ├── config.py             # Environment-specific Flask configuration
│   ├── routes/               # Flask route blueprints
│   ├── static/               # Static frontend assets
│   └── templates/             # Application templates
├── terraform/
│   ├── bootstrap/             # Remote-state/bootstrap resources
│   ├── ci/                    # ECR and GitHub OIDC IAM resources
│   └── eks-demo/              # EKS demonstration infrastructure
├── tests/                     # Application tests
├── app.py                     # Flask application factory entry point
├── Dockerfile                 # Multi-stage, non-root container image
├── requirements.txt           # Python dependencies
└── README.md
```

## Implementation phases and proof of work

The screenshots below are the supplied project evidence files. Each image is linked using its exact filename under `docs/screenshots/`. Expand a phase to view its evidence. The captions describe the visible activity at a practical level; the screenshots are historical captures, not claims that the associated cloud resources are still running.

### Phase 1 — Flask application and Docker foundation

Initial Flask application, repository bootstrap, Docker image build, container execution and browser-based smoke checks.

<details>
<summary>View 9 screenshot(s) for this phase</summary>


**Evidence 001 — VS Code view of the initial Flask application source.**

![VS Code view of the initial Flask application source.](docs/screenshots/Screenshot%202026-06-24%20170406.png)


**Evidence 002 — GitHub repository view showing the first application files.**

![GitHub repository view showing the first application files.](docs/screenshots/Screenshot%202026-06-24%20170855.png)


**Evidence 003 — Docker Desktop showing the locally built/running application containers.**

![Docker Desktop showing the locally built/running application containers.](docs/screenshots/Screenshot%202026-06-24%20172102.png)


**Evidence 004 — Browser smoke test reaching the application through the host network.**

![Browser smoke test reaching the application through the host network.](docs/screenshots/Screenshot%202026-06-24%20172718.png)


**Evidence 005 — Docker image build output, including dependency installation and image creation.**

![Docker image build output, including dependency installation and image creation.](docs/screenshots/Screenshot%202026-06-24%20174236.png)


**Evidence 006 — Localhost browser smoke test showing the Flask application response.**

![Localhost browser smoke test showing the Flask application response.](docs/screenshots/Screenshot%202026-06-24%20174555.png)


**Evidence 007 — Flask development server startup and request log output.**

![Flask development server startup and request log output.](docs/screenshots/Screenshot%202026-06-24%20174753.png)


**Evidence 008 — Docker CLI container listing/status check.**

![Docker CLI container listing/status check.](docs/screenshots/Screenshot%202026-06-24%20174854.png)


**Evidence 009 — GitHub source view of the Flask application implementation.**

![GitHub source view of the Flask application implementation.](docs/screenshots/Screenshot%202026-06-24%20175049.png)


</details>

### Phase 2 — Kubernetes fundamentals with Minikube

Local Kubernetes environment setup, cluster startup, Deployment/Pod/Service inspection and application access through a local NodePort.

<details>
<summary>View 7 screenshot(s) for this phase</summary>


**Evidence 010 — Local Windows terminal verification of Kubernetes tooling versions.**

![Local Windows terminal verification of Kubernetes tooling versions.](docs/screenshots/Screenshot%202026-06-26%20105314.png)


**Evidence 011 — Minikube cluster startup and local Kubernetes node initialization.**

![Minikube cluster startup and local Kubernetes node initialization.](docs/screenshots/Screenshot%202026-06-26%20113244.png)


**Evidence 012 — Kubernetes deployment/pod state after the first application rollout.**

![Kubernetes deployment/pod state after the first application rollout.](docs/screenshots/Screenshot%202026-06-26%20123709.png)


**Evidence 013 — Application response through a local forwarded/NodePort browser endpoint.**

![Application response through a local forwarded/NodePort browser endpoint.](docs/screenshots/Screenshot%202026-06-26%20124807.png)


**Evidence 014 — Kubernetes Service and Deployment inspection, including exposed application port.**

![Kubernetes Service and Deployment inspection, including exposed application port.](docs/screenshots/Screenshot%202026-06-26%20124905.png)


**Evidence 015 — Second local application access check through a forwarded browser port.**

![Second local application access check through a forwarded browser port.](docs/screenshots/Screenshot%202026-06-26%20130958.png)


**Evidence 016 — Application request logs confirming successful HTTP requests.**

![Application request logs confirming successful HTTP requests.](docs/screenshots/Screenshot%202026-06-26%20135132.png)


</details>

### Phase 3 — Helm chart packaging and configuration

Helm chart creation, templates and values inspection, lint/render/install workflow, and validation of Kubernetes resources generated from the chart.

<details>
<summary>View 27 screenshot(s) for this phase</summary>


**Evidence 017 — Docker Desktop/Minikube runtime state during Kubernetes setup.**

![Docker Desktop/Minikube runtime state during Kubernetes setup.](docs/screenshots/Screenshot%202026-06-28%20122327.png)


**Evidence 018 — Project landing page rendered in the browser.**

![Project landing page rendered in the browser.](docs/screenshots/Screenshot%202026-06-28%20123901.png)


**Evidence 019 — Helm chart metadata and chart packaging inspection.**

![Helm chart metadata and chart packaging inspection.](docs/screenshots/Screenshot%202026-06-28%20125053.png)


**Evidence 020 — Helm chart command output during chart validation.**

![Helm chart command output during chart validation.](docs/screenshots/Screenshot%202026-06-28%20125139.png)


**Evidence 021 — Helm chart source/configuration inspection.**

![Helm chart source/configuration inspection.](docs/screenshots/Screenshot%202026-06-28%20125241.png)


**Evidence 022 — Helm chart repository/image inventory in Docker Desktop.**

![Helm chart repository/image inventory in Docker Desktop.](docs/screenshots/Screenshot%202026-06-28%20151234.png)


**Evidence 023 — Helm chart source tree and template implementation.**

![Helm chart source tree and template implementation.](docs/screenshots/Screenshot%202026-06-28%20151610.png)


**Evidence 024 — Helm chart template rendering and resource configuration review.**

![Helm chart template rendering and resource configuration review.](docs/screenshots/Screenshot%202026-06-28%20181833.png)


**Evidence 025 — Helm chart lint/install command output.**

![Helm chart lint/install command output.](docs/screenshots/Screenshot%202026-06-28%20181852.png)


**Evidence 026 — Rendered Kubernetes resource definitions from the Helm chart.**

![Rendered Kubernetes resource definitions from the Helm chart.](docs/screenshots/Screenshot%202026-06-28%20183931.png)


**Evidence 027 — Helm values/configuration validation.**

![Helm values/configuration validation.](docs/screenshots/Screenshot%202026-06-28%20191922.png)


**Evidence 028 — Helm template output showing Kubernetes resource metadata.**

![Helm template output showing Kubernetes resource metadata.](docs/screenshots/Screenshot%202026-06-28%20191943.png)


**Evidence 029 — Deployment/Service template configuration review.**

![Deployment/Service template configuration review.](docs/screenshots/Screenshot%202026-06-28%20194543.png)


**Evidence 030 — Helm values and generated Kubernetes configuration inspection.**

![Helm values and generated Kubernetes configuration inspection.](docs/screenshots/Screenshot%202026-06-28%20201446.png)


**Evidence 031 — Ingress and service template configuration review.**

![Ingress and service template configuration review.](docs/screenshots/Screenshot%202026-06-28%20215053.png)


**Evidence 032 — Helm selector/port and workload template inspection.**

![Helm selector/port and workload template inspection.](docs/screenshots/Screenshot%202026-06-28%20224337.png)


**Evidence 033 — Git history showing incremental Helm chart implementation.**

![Git history showing incremental Helm chart implementation.](docs/screenshots/Screenshot%202026-06-28%20231200.png)


**Evidence 034 — Rendered chart resources and configuration review.**

![Rendered chart resources and configuration review.](docs/screenshots/Screenshot%202026-06-28%20234503.png)


**Evidence 035 — ConfigMap template and application environment configuration.**

![ConfigMap template and application environment configuration.](docs/screenshots/Screenshot%202026-06-28%20235444.png)


**Evidence 036 — Kubernetes Secret template structure (secret values should never be committed in plaintext).**

![Kubernetes Secret template structure (secret values should never be committed in plaintext).](docs/screenshots/Screenshot%202026-06-29%20000037.png)


**Evidence 037 — ServiceAccount template and workload identity configuration.**

![ServiceAccount template and workload identity configuration.](docs/screenshots/Screenshot%202026-06-29%20002650.png)


**Evidence 038 — GitHub commit history documenting Helm chart milestones.**

![GitHub commit history documenting Helm chart milestones.](docs/screenshots/Screenshot%202026-06-29%20135013.png)


**Evidence 039 — Rendered chart resources, including workload configuration.**

![Rendered chart resources, including workload configuration.](docs/screenshots/Screenshot%202026-06-29%20140112.png)


**Evidence 040 — Helm installation/deployment output and application release validation.**

![Helm installation/deployment output and application release validation.](docs/screenshots/Screenshot%202026-06-29%20140528.png)


**Evidence 041 — Application Deployment/Pod status after Helm installation.**

![Application Deployment/Pod status after Helm installation.](docs/screenshots/Screenshot%202026-06-29%20151418.png)


**Evidence 042 — Application health endpoint response from the deployed workload.**

![Application health endpoint response from the deployed workload.](docs/screenshots/Screenshot%202026-06-29%20151658.png)


**Evidence 043 — Kubernetes application deployment and endpoint verification.**

![Kubernetes application deployment and endpoint verification.](docs/screenshots/Screenshot%202026-06-29%20152017.png)


</details>

### Phase 4 — Argo CD GitOps and secret handling

Argo CD installation and UI, Application resources, repository connection, automated sync/health checks, GitOps demo endpoint, and Sealed Secrets workflow.

<details>
<summary>View 52 screenshot(s) for this phase</summary>


**Evidence 044 — Argo CD components running in the local Kubernetes cluster.**

![Argo CD components running in the local Kubernetes cluster.](docs/screenshots/Screenshot%202026-07-02%20111149.png)


**Evidence 045 — Argo CD namespace resources and controller status.**

![Argo CD namespace resources and controller status.](docs/screenshots/Screenshot%202026-07-02%20112740.png)


**Evidence 046 — Argo CD CLI/repository access setup.**

![Argo CD CLI/repository access setup.](docs/screenshots/Screenshot%202026-07-02%20125140.png)


**Evidence 047 — Argo CD initial web UI/login screen.**

![Argo CD initial web UI/login screen.](docs/screenshots/Screenshot%202026-07-02%20130001.png)


**Evidence 048 — Argo CD Applications page before application registration.**

![Argo CD Applications page before application registration.](docs/screenshots/Screenshot%202026-07-02%20130052.png)


**Evidence 049 — Argo CD CLI installation/context setup evidence.**

![Argo CD CLI installation/context setup evidence.](docs/screenshots/Screenshot%202026-07-02%20163743.png)


**Evidence 050 — GitHub personal access token settings used for repository integration; token values must remain private.**

![GitHub personal access token settings used for repository integration; token values must remain private.](docs/screenshots/Screenshot%202026-07-02%20221909.png)


**Evidence 051 — Argo CD repository connection/status check.**

![Argo CD repository connection/status check.](docs/screenshots/Screenshot%202026-07-02%20225637.png)


**Evidence 052 — Argo CD Applications list after initial setup.**

![Argo CD Applications list after initial setup.](docs/screenshots/Screenshot%202026-07-02%20225841.png)


**Evidence 053 — Application status and local Kubernetes resource inspection.**

![Application status and local Kubernetes resource inspection.](docs/screenshots/Screenshot%202026-07-03%20115710.png)


**Evidence 054 — Application health endpoint response showing runtime metadata.**

![Application health endpoint response showing runtime metadata.](docs/screenshots/Screenshot%202026-07-03%20115830.png)


**Evidence 055 — Deployment/pod rollout and resource status verification.**

![Deployment/pod rollout and resource status verification.](docs/screenshots/Screenshot%202026-07-03%20121858.png)


**Evidence 056 — Argo CD application resource graph and health overview.**

![Argo CD application resource graph and health overview.](docs/screenshots/Screenshot%202026-07-03%20122231.png)


**Evidence 057 — Argo CD Applications view showing development and production application entries.**

![Argo CD Applications view showing development and production application entries.](docs/screenshots/Screenshot%202026-07-03%20133333.png)


**Evidence 058 — Git commit/push used to update the GitOps-managed configuration.**

![Git commit/push used to update the GitOps-managed configuration.](docs/screenshots/Screenshot%202026-07-03%20135930.png)


**Evidence 059 — Argo CD application sync status after repository changes.**

![Argo CD application sync status after repository changes.](docs/screenshots/Screenshot%202026-07-03%20142426.png)


**Evidence 060 — GitOps demo endpoint response describing the commit-to-deployment workflow.**

![GitOps demo endpoint response describing the commit-to-deployment workflow.](docs/screenshots/Screenshot%202026-07-03%20143435.png)


**Evidence 061 — Development namespace pod rollout after a GitOps change.**

![Development namespace pod rollout after a GitOps change.](docs/screenshots/Screenshot%202026-07-03%20144526.png)


**Evidence 062 — Argo CD Application manifest/configuration review.**

![Argo CD Application manifest/configuration review.](docs/screenshots/Screenshot%202026-07-03%20145057.png)


**Evidence 063 — Argo CD revision/history evidence for successive GitOps updates.**

![Argo CD revision/history evidence for successive GitOps updates.](docs/screenshots/Screenshot%202026-07-03%20145141.png)


**Evidence 064 — Kubernetes resource quota configuration for the production namespace.**

![Kubernetes resource quota configuration for the production namespace.](docs/screenshots/Screenshot%202026-07-03%20190156.png)


**Evidence 065 — GitOps/Helm configuration update and validation.**

![GitOps/Helm configuration update and validation.](docs/screenshots/Screenshot%202026-07-03%20191309.png)


**Evidence 066 — Environment-specific configuration output for development and production.**

![Environment-specific configuration output for development and production.](docs/screenshots/Screenshot%202026-07-03%20193205.png)


**Evidence 067 — Kubernetes resource inventory during environment comparison.**

![Kubernetes resource inventory during environment comparison.](docs/screenshots/Screenshot%202026-07-03%20194428.png)


**Evidence 068 — Pod/resource state across development and production namespaces.**

![Pod/resource state across development and production namespaces.](docs/screenshots/Screenshot%202026-07-03%20195201.png)


**Evidence 069 — Argo CD application health view after synchronization.**

![Argo CD application health view after synchronization.](docs/screenshots/Screenshot%202026-07-03%20195854.png)


**Evidence 070 — Argo CD application details and source/destination configuration.**

![Argo CD application details and source/destination configuration.](docs/screenshots/Screenshot%202026-07-03%20235129.png)


**Evidence 071 — Argo CD project configuration and repository permissions.**

![Argo CD project configuration and repository permissions.](docs/screenshots/Screenshot%202026-07-03%20235454.png)


**Evidence 072 — Helm/Argo CD generated resource configuration review.**

![Helm/Argo CD generated resource configuration review.](docs/screenshots/Screenshot%202026-07-03%20235634.png)


**Evidence 073 — Argo CD application history and sync event evidence.**

![Argo CD application history and sync event evidence.](docs/screenshots/Screenshot%202026-07-03%20235710.png)


**Evidence 074 — Argo CD resource tree showing managed Kubernetes resources.**

![Argo CD resource tree showing managed Kubernetes resources.](docs/screenshots/Screenshot%202026-07-03%20235833.png)


**Evidence 075 — Sealed Secrets controller and encrypted-secret workflow configuration.**

![Sealed Secrets controller and encrypted-secret workflow configuration.](docs/screenshots/Screenshot%202026-07-03%20235951.png)


**Evidence 076 — Sealed Secrets controller pod running in the development cluster.**

![Sealed Secrets controller pod running in the development cluster.](docs/screenshots/Screenshot%202026-07-04%20002345.png)


**Evidence 077 — kubeseal public certificate / encrypted secret material handling; no private key is shown as a deployment credential.**

![kubeseal public certificate / encrypted secret material handling; no private key is shown as a deployment credential.](docs/screenshots/Screenshot%202026-07-04%20002740.png)


**Evidence 078 — Applying a SealedSecret manifest and verifying the generated Kubernetes Secret.**

![Applying a SealedSecret manifest and verifying the generated Kubernetes Secret.](docs/screenshots/Screenshot%202026-07-04%20003327.png)


**Evidence 079 — Application pod status after the secret integration.**

![Application pod status after the secret integration.](docs/screenshots/Screenshot%202026-07-04%20011604.png)


**Evidence 080 — GitOps application details after secret-related configuration changes.**

![GitOps application details after secret-related configuration changes.](docs/screenshots/Screenshot%202026-07-04%20140800.png)


**Evidence 081 — Argo CD source and destination configuration for the managed application.**

![Argo CD source and destination configuration for the managed application.](docs/screenshots/Screenshot%202026-07-04%20143424.png)


**Evidence 082 — GitOps demo endpoint error encountered during troubleshooting.**

![GitOps demo endpoint error encountered during troubleshooting.](docs/screenshots/Screenshot%202026-07-04%20224628.png)


**Evidence 083 — GitOps demo endpoint response and HTTP headers after the fix.**

![GitOps demo endpoint response and HTTP headers after the fix.](docs/screenshots/Screenshot%202026-07-04%20232809.png)


**Evidence 084 — Argo CD application details and synchronization state.**

![Argo CD application details and synchronization state.](docs/screenshots/Screenshot%202026-07-05%20000133.png)


**Evidence 085 — Argo CD application comparison/health state.**

![Argo CD application comparison/health state.](docs/screenshots/Screenshot%202026-07-05%20133959.png)


**Evidence 086 — Argo CD application history and deployed revision.**

![Argo CD application history and deployed revision.](docs/screenshots/Screenshot%202026-07-05%20142330.png)


**Evidence 087 — Kubernetes resources and rollout status after a GitOps sync.**

![Kubernetes resources and rollout status after a GitOps sync.](docs/screenshots/Screenshot%202026-07-05%20143120.png)


**Evidence 088 — Argo CD application resource status and health checks.**

![Argo CD application resource status and health checks.](docs/screenshots/Screenshot%202026-07-05%20143249.png)


**Evidence 089 — Argo CD resource tree and child resources.**

![Argo CD resource tree and child resources.](docs/screenshots/Screenshot%202026-07-05%20151146.png)


**Evidence 090 — Argo CD project/application configuration evidence.**

![Argo CD project/application configuration evidence.](docs/screenshots/Screenshot%202026-07-05%20151319.png)


**Evidence 091 — Argo CD application resource graph and health status.**

![Argo CD application resource graph and health status.](docs/screenshots/Screenshot%202026-07-05%20151749.png)


**Evidence 092 — Argo CD application details after the repository update.**

![Argo CD application details after the repository update.](docs/screenshots/Screenshot%202026-07-05%20151859.png)


**Evidence 093 — Terminal evidence of GitOps configuration/revision work.**

![Terminal evidence of GitOps configuration/revision work.](docs/screenshots/Screenshot%202026-07-10%20203722.png)


**Evidence 094 — Terminal evidence of repository synchronization and deployment workflow.**

![Terminal evidence of repository synchronization and deployment workflow.](docs/screenshots/Screenshot%202026-07-10%20204641.png)


**Evidence 095 — Terminal evidence of the final GitOps configuration checks.**

![Terminal evidence of the final GitOps configuration checks.](docs/screenshots/Screenshot%202026-07-10%20205923.png)


</details>

### Phase 5 — GitHub Actions CI/CD and image delivery

GitHub Actions pipeline runs, Docker build/push summaries, image verification and workflow execution evidence.

<details>
<summary>View 8 screenshot(s) for this phase</summary>


**Evidence 096 — GitHub Actions CI workflow run with successful job stages.**

![GitHub Actions CI workflow run with successful job stages.](docs/screenshots/Screenshot%202026-10-11%20172522.png)


**Evidence 097 — GitHub Actions workflow execution details for the CI/CD pipeline.**

![GitHub Actions workflow execution details for the CI/CD pipeline.](docs/screenshots/Screenshot%202026-10-11%20221514.png)


**Evidence 098 — Docker build and push summary showing the produced image metadata.**

![Docker build and push summary showing the produced image metadata.](docs/screenshots/Screenshot%202026-10-11%20222307.png)


**Evidence 099 — Image verification job and workflow log evidence.**

![Image verification job and workflow log evidence.](docs/screenshots/Screenshot%202026-10-11%20222418.png)


**Evidence 100 — GitHub Actions pipeline run showing the multi-job workflow progression.**

![GitHub Actions pipeline run showing the multi-job workflow progression.](docs/screenshots/Screenshot%202026-10-11%20231204.png)


**Evidence 101 — GitHub Actions run list showing repeated pipeline executions.**

![GitHub Actions run list showing repeated pipeline executions.](docs/screenshots/Screenshot%202026-10-13%20235807.png)


**Evidence 102 — Git commit history showing automated GitOps image-tag updates.**

![Git commit history showing automated GitOps image-tag updates.](docs/screenshots/Screenshot%202026-10-14%20000430.png)


**Evidence 103 — GitHub Actions commit/change evidence for the pipeline implementation.**

![GitHub Actions commit/change evidence for the pipeline implementation.](docs/screenshots/Screenshot%202026-10-14%20000919.png)


</details>

### Phase 6 — Prometheus and Grafana observability

Prometheus installation and target discovery, ServiceMonitor configuration, Grafana dashboards and application/service metrics.

<details>
<summary>View 12 screenshot(s) for this phase</summary>


**Evidence 104 — Argo CD application state during the observability integration phase.**

![Argo CD application state during the observability integration phase.](docs/screenshots/Screenshot%202026-10-22%20194004.png)


**Evidence 105 — Argo CD sync/health status during monitoring configuration changes.**

![Argo CD sync/health status during monitoring configuration changes.](docs/screenshots/Screenshot%202026-10-23%20183015.png)


**Evidence 106 — GitHub Actions workflow run for the monitoring-related project revision.**

![GitHub Actions workflow run for the monitoring-related project revision.](docs/screenshots/Screenshot%202026-10-26%20213227.png)


**Evidence 107 — Kubernetes monitoring namespace pods and service endpoints.**

![Kubernetes monitoring namespace pods and service endpoints.](docs/screenshots/Screenshot%202026-10-27%20150922.png)


**Evidence 108 — Grafana dashboard catalogue showing installed dashboards.**

![Grafana dashboard catalogue showing installed dashboards.](docs/screenshots/Screenshot%202026-10-27%20151101.png)


**Evidence 109 — Prometheus Targets page showing discovered scrape targets and health.**

![Prometheus Targets page showing discovered scrape targets and health.](docs/screenshots/Screenshot%202026-10-27%20155518.png)


**Evidence 110 — Grafana dashboard panels for application and cluster metrics.**

![Grafana dashboard panels for application and cluster metrics.](docs/screenshots/Screenshot%202026-10-27%20203722.png)


**Evidence 111 — Prometheus ServiceMonitor configuration and scrape settings.**

![Prometheus ServiceMonitor configuration and scrape settings.](docs/screenshots/Screenshot%202026-10-27%20221147.png)


**Evidence 112 — Prometheus query/UI validation for application metrics.**

![Prometheus query/UI validation for application metrics.](docs/screenshots/Screenshot%202026-10-27%20221633.png)


**Evidence 113 — Prometheus target/metric inspection during observability validation.**

![Prometheus target/metric inspection during observability validation.](docs/screenshots/Screenshot%202026-10-27%20221956.png)


**Evidence 114 — Prometheus/Grafana configuration review from the project repository.**

![Prometheus/Grafana configuration review from the project repository.](docs/screenshots/Screenshot%202026-10-28%20110140.png)


**Evidence 115 — Grafana dashboard showing time-series application and workload metrics.**

![Grafana dashboard showing time-series application and workload metrics.](docs/screenshots/Screenshot%202026-10-29%20181834.png)


</details>

### Phase 7 — Alert rules, HPA and load validation

Prometheus alert-rule configuration and UI, Kubernetes resource/HPA observations, workload/load-test activity and scaling evidence.

<details>
<summary>View 14 screenshot(s) for this phase</summary>


**Evidence 116 — Prometheus alert-rule configuration in the repository.**

![Prometheus alert-rule configuration in the repository.](docs/screenshots/Screenshot%202026-11-05%20134442.png)


**Evidence 117 — Prometheus alerting rules and alert state in the UI.**

![Prometheus alerting rules and alert state in the UI.](docs/screenshots/Screenshot%202026-11-05%20134527.png)


**Evidence 118 — Alertmanager UI showing configured alert routing state.**

![Alertmanager UI showing configured alert routing state.](docs/screenshots/Screenshot%202026-11-06%20000055.png)


**Evidence 119 — Alertmanager notification/receiver configuration review.**

![Alertmanager notification/receiver configuration review.](docs/screenshots/Screenshot%202026-11-06%20000328.png)


**Evidence 120 — Prometheus alert rule state and monitoring configuration validation.**

![Prometheus alert rule state and monitoring configuration validation.](docs/screenshots/Screenshot%202026-11-06%20001156.png)


**Evidence 121 — Kubernetes pod resource usage output during HPA/load testing.**

![Kubernetes pod resource usage output during HPA/load testing.](docs/screenshots/Screenshot%202026-11-06%20112911.png)


**Evidence 122 — HPA/deployment configuration review showing autoscaling parameters.**

![HPA/deployment configuration review showing autoscaling parameters.](docs/screenshots/Screenshot%202026-11-06%20123931.png)


**Evidence 123 — HPA and Kubernetes resource configuration validation.**

![HPA and Kubernetes resource configuration validation.](docs/screenshots/Screenshot%202026-11-06%20124201.png)


**Evidence 124 — Grafana dashboard showing request/error/latency or workload metrics during load activity.**

![Grafana dashboard showing request/error/latency or workload metrics during load activity.](docs/screenshots/Screenshot%202026-11-10%20185643.png)


**Evidence 125 — Deployment and HPA status showing replica count and scaling observations.**

![Deployment and HPA status showing replica count and scaling observations.](docs/screenshots/Screenshot%202026-11-10%20192029.png)


**Evidence 126 — Grafana/cluster UI evidence during load testing and autoscaling validation.**

![Grafana/cluster UI evidence during load testing and autoscaling validation.](docs/screenshots/Screenshot%202026-11-10%20233814.png)


**Evidence 127 — Terminal output from a security/configuration validation step.**

![Terminal output from a security/configuration validation step.](docs/screenshots/Screenshot%202026-11-11%20151842.png)


**Evidence 128 — Terminal output showing security/configuration validation results.**

![Terminal output showing security/configuration validation results.](docs/screenshots/Screenshot%202026-11-11%20224511.png)


**Evidence 129 — Terminal output showing additional scan/configuration results.**

![Terminal output showing additional scan/configuration results.](docs/screenshots/Screenshot%202026-11-11%20224758.png)


</details>

### Phase 8 — Supply-chain and repository security

Gitleaks repository-history scan evidence. The CI workflow also runs a Trivy filesystem scan for CRITICAL, unfixed vulnerabilities.

<details>
<summary>View 1 screenshot(s) for this phase</summary>


**Evidence 130 — Gitleaks repository scan output reporting no leaks found in the scanned content.**

![Gitleaks repository scan output reporting no leaks found in the scanned content.](docs/screenshots/Screenshot%202026-11-19%20122236.png)


</details>

### Phase 9 — AWS EKS, Terraform and cloud validation

Terraform planning/apply evidence, AWS/EKS setup, load balancer/controller and metrics-server checks, Argo CD application health, Prometheus targets, network-policy checks, HPA scaling and Grafana load dashboards.

<details>
<summary>View 23 screenshot(s) for this phase</summary>


**Evidence 131 — Terraform configuration/apply workflow evidence for the EKS demo environment.**

![Terraform configuration/apply workflow evidence for the EKS demo environment.](docs/screenshots/Screenshot%202026-11-22%20142932.png)


**Evidence 132 — Terraform plan output showing the proposed AWS infrastructure changes.**

![Terraform plan output showing the proposed AWS infrastructure changes.](docs/screenshots/Screenshot%202026-11-22%20153135.png)


**Evidence 133 — Terraform plan review for the EKS/VPC infrastructure resources.**

![Terraform plan review for the EKS/VPC infrastructure resources.](docs/screenshots/Screenshot%202026-11-24%20125851.png)


**Evidence 134 — AWS/EKS node and cluster resource inventory during the deployment session.**

![AWS/EKS node and cluster resource inventory during the deployment session.](docs/screenshots/Screenshot%202026-11-25%20141815.png)


**Evidence 135 — GitHub Actions pipeline run associated with the AWS/ECR integration.**

![GitHub Actions pipeline run associated with the AWS/ECR integration.](docs/screenshots/Screenshot%202026-11-25%20160801.png)


**Evidence 136 — AWS console evidence for the cloud-side project integration/configuration.**

![AWS console evidence for the cloud-side project integration/configuration.](docs/screenshots/Screenshot%202026-11-25%20162442.png)


**Evidence 137 — Terraform output values used to identify the EKS/VPC and load-balancer controller resources.**

![Terraform output values used to identify the EKS/VPC and load-balancer controller resources.](docs/screenshots/Screenshot%202026-11-25%20170124.png)


**Evidence 138 — AWS Load Balancer Controller installation and Kubernetes deployment verification.**

![AWS Load Balancer Controller installation and Kubernetes deployment verification.](docs/screenshots/Screenshot%202026-11-25%20170804.png)


**Evidence 139 — Metrics Server installation and resource metrics availability in the EKS cluster.**

![Metrics Server installation and resource metrics availability in the EKS cluster.](docs/screenshots/Screenshot%202026-11-25%20171656.png)


**Evidence 140 — Argo CD Applications view before the EKS application was registered.**

![Argo CD Applications view before the EKS application was registered.](docs/screenshots/Screenshot%202026-11-25%20172924.png)


**Evidence 141 — Prometheus and monitoring pods running in the EKS monitoring namespace.**

![Prometheus and monitoring pods running in the EKS monitoring namespace.](docs/screenshots/Screenshot%202026-11-25%20190702.png)


**Evidence 142 — Argo CD EKS application showing Synced/Healthy status, alongside application health verification.**

![Argo CD EKS application showing Synced/Healthy status, alongside application health verification.](docs/screenshots/Screenshot%202026-11-25%20194226.png)


**Evidence 143 — EKS cluster command-line resource inspection during deployment validation.**

![EKS cluster command-line resource inspection during deployment validation.](docs/screenshots/Screenshot%202026-11-25%20194449.png)


**Evidence 144 — Prometheus pod status and monitoring workload verification in EKS.**

![Prometheus pod status and monitoring workload verification in EKS.](docs/screenshots/Screenshot%202026-11-25%20194540.png)


**Evidence 145 — Prometheus target-health output showing active targets and both application scrape targets UP.**

![Prometheus target-health output showing active targets and both application scrape targets UP.](docs/screenshots/Screenshot%202026-11-25%20200418.png)


**Evidence 146 — Grafana dashboard during load activity, showing application/cluster telemetry.**

![Grafana dashboard during load activity, showing application/cluster telemetry.](docs/screenshots/Screenshot%202026-11-25%20201154.png)


**Evidence 147 — NetworkPolicy test showing cross-namespace traffic blocked as intended.**

![NetworkPolicy test showing cross-namespace traffic blocked as intended.](docs/screenshots/Screenshot%202026-11-25%20210706.png)


**Evidence 148 — Grafana dashboard showing request/latency/pod metrics during load testing.**

![Grafana dashboard showing request/latency/pod metrics during load testing.](docs/screenshots/Screenshot%202026-11-25%20233046.png)


**Evidence 149 — HPA output showing replicas scaling in response to workload and then stabilizing.**

![HPA output showing replicas scaling in response to workload and then stabilizing.](docs/screenshots/Screenshot%202026-11-25%20233342.png)


**Evidence 150 — AWS EKS console view showing the demo cluster active with its worker nodes.**

![AWS EKS console view showing the demo cluster active with its worker nodes.](docs/screenshots/Screenshot%202026-11-25%20233722.png)


**Evidence 151 — AWS VPC resource map showing the EKS networking layout.**

![AWS VPC resource map showing the EKS networking layout.](docs/screenshots/Screenshot%202026-11-25%20234050.png)


**Evidence 152 — AWS console infrastructure view for the EKS deployment resources.**

![AWS console infrastructure view for the EKS deployment resources.](docs/screenshots/Screenshot%202026-11-25%20234222.png)


**Evidence 153 — Argo CD EKS application resource graph showing the deployed Kubernetes components.**

![Argo CD EKS application resource graph showing the deployed Kubernetes components.](docs/screenshots/Screenshot%202026-11-25%20234844.png)


</details>


## Application endpoints

The Flask application is assembled through an application factory and registers separate route blueprints.

| Endpoint | Purpose |
|---|---|
| `/` | Application landing page |
| `/health` | Health check used by container/Kubernetes/CI validation |
| `/info` | Runtime/application information |
| `/version` | Application version/build metadata |
| `/metrics` | Application metrics endpoint |
| `/metrics/prometheus` | Prometheus scrape endpoint used by the Kubernetes ServiceMonitor |
| `/tech-stack` | Technology-stack information |
| `/developer` | Project/developer metadata |
| `/gitops-demo` | Demonstration endpoint describing the GitOps delivery flow |

## Run locally

### Prerequisites

- Git
- Python 3.12
- pip
- Docker Desktop (for the container workflow)
- For Kubernetes work: `kubectl`, Minikube and Helm
- For GitOps: Argo CD CLI/UI and a running Kubernetes cluster
- For AWS reproduction: AWS CLI, Terraform, an AWS account with appropriately scoped permissions, and GitHub repository secrets/variables configured for OIDC

### Clone and install

```bash
git clone https://github.com/shivam535353/production-grade-devops-platform.git
cd production-grade-devops-platform

python -m venv .venv
source .venv/Scripts/activate   # Git Bash on Windows
# On macOS/Linux use: source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start the Flask application:

```bash
export APP_ENV=development
python app.py
```

Open `http://127.0.0.1:5000` and verify:

```bash
curl -i http://127.0.0.1:5000/health
curl -i http://127.0.0.1:5000/version
curl -i http://127.0.0.1:5000/metrics
```

The configuration generates a development secret when `SECRET_KEY` is not supplied. For a production deployment, provide a strong secret through a secure environment/secret manager; never commit it to Git.

## Run with Docker

Build the image:

```bash
docker build -t production-grade-devops-platform:local .
```

Run the container:

```bash
docker run --rm \
  --name devops-platform \
  -p 5000:5000 \
  -e APP_ENV=production \
  -e SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')" \
  production-grade-devops-platform:local
```

Validate the running container:

```bash
curl -i http://127.0.0.1:5000/health
docker ps
docker logs devops-platform
```

The Dockerfile uses a Python 3.12 slim builder/runtime, installs dependencies in a builder stage, runs as UID 1001 (`appuser`) and defines a container health check against `/health`.

## Kubernetes and Helm deployment

> These commands assume a working local Minikube cluster and that the chart's development values are appropriate for your machine. Review the values file before applying it.

Start Minikube and verify the context:

```bash
minikube start
kubectl config current-context
kubectl get nodes
```

Install or upgrade the application chart:

```bash
helm lint ./helm/devops-platform
helm template devops-platform ./helm/devops-platform \
  --namespace dev \
  -f helm/devops-platform/values-dev.yaml

kubectl create namespace dev --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install devops-platform ./helm/devops-platform \
  --namespace dev \
  -f helm/devops-platform/values-dev.yaml

kubectl get deployments,pods,services -n dev
kubectl rollout status deployment/devops-platform -n dev
```

If the release's Deployment name differs from `devops-platform` in a customized values file, use `kubectl get deployments -n dev` and pass the actual Deployment name to `kubectl rollout status`.

### Argo CD / GitOps

The repository includes Argo CD configuration under `argocd/`. The GitOps workflow is:

1. Connect the repository to Argo CD.
2. Register the relevant Argo CD Application manifest from `argocd/`.
3. Confirm the source repository/path and destination cluster/namespace.
4. Commit a Helm values change to Git.
5. Confirm that Argo CD detects the revision and reports the Application as `Synced` and `Healthy`.

Do not store plaintext credentials in Helm values. The EKS values configuration references an existing Kubernetes Secret named `devops-platform-app-secret`; create/manage that Secret through an approved secret-management process before deploying the chart.

## AWS deployment notes

The AWS demonstration was implemented in `ap-south-1` using Terraform and Amazon EKS. The repository contains separate Terraform areas for bootstrap, CI/ECR/OIDC and the EKS demo.

A safe reproduction sequence is:

1. Configure the AWS CLI with a dedicated profile and confirm the account/region.
2. Review the Terraform variables, backend configuration, IAM permissions and estimated costs.
3. Initialize and apply the bootstrap stack if the remote-state bucket does not already exist.
4. Initialize the CI stack to provision/configure ECR and GitHub OIDC role resources.
5. Review the EKS demo Terraform plan before applying it.
6. Configure `kubectl`, install required EKS add-ons/controllers, and verify node readiness.
7. Ensure the Kubernetes Secret referenced by `values-eks.yaml` exists.
8. Deploy the EKS Argo CD Application and verify the ALB health check, Pods, HPA and Prometheus targets.
9. Destroy the EKS demo stack when testing is complete, while retaining only intentionally persistent resources.

Illustrative Terraform commands (run from the repository root; inspect each plan before applying):

```bash
export AWS_PROFILE=<your-aws-profile>
export AWS_REGION=ap-south-1
export AWS_DEFAULT_REGION=ap-south-1

terraform -chdir=terraform/bootstrap init
terraform -chdir=terraform/bootstrap plan
# Apply only after reviewing the plan:
terraform -chdir=terraform/bootstrap apply

terraform -chdir=terraform/ci init
terraform -chdir=terraform/ci plan
# Apply only after reviewing the plan:
terraform -chdir=terraform/ci apply

terraform -chdir=terraform/eks-demo init
terraform -chdir=terraform/eks-demo plan
# EKS, NAT gateways, load balancers and data transfer can incur charges.
# Apply only when you are ready to run the demonstration:
terraform -chdir=terraform/eks-demo apply
```

Do not copy account IDs, ARNs, access keys, Terraform state contents or generated secrets from screenshots into public documentation. Configure the GitHub Actions variable `AWS_ROLE_ARN` and required repository secrets/permissions using your own environment values.

## Security design

- **Non-root container:** the runtime image runs as a dedicated non-root user (UID 1001).
- **Container health check:** Docker checks the application's `/health` endpoint.
- **CI secret scanning:** Gitleaks scans the Git history and redacts detected secret values in output.
- **Filesystem vulnerability scanning:** Trivy is configured to fail the workflow on CRITICAL, unfixed findings.
- **OIDC federation:** GitHub Actions obtains short-lived AWS credentials by assuming an IAM role through GitHub's OIDC provider; long-lived AWS access keys are not required in GitHub secrets for this path.
- **Kubernetes hardening:** the EKS values include non-root execution, dropped Linux capabilities, RuntimeDefault seccomp, NetworkPolicy and a pre-created Secret reference.
- **Secret separation:** runtime secret data is not intended to live in Helm values or committed plaintext manifests.

Security scans are point-in-time checks; rerun them against the current branch and dependency set before using the project as a production baseline.

## Engineering challenges and learnings

- **Environment parity:** using a common Helm chart with environment-specific values separates application packaging from deployment configuration.
- **GitOps reconciliation:** a Git commit becomes the desired state; Argo CD compares the repository state with the live cluster and reports synchronization/health.
- **Image traceability:** SHA-based image tags make it easier to associate a running container with the source revision that produced it.
- **Cloud identity:** GitHub OIDC reduces the need for static AWS credentials and enables IAM trust conditions scoped to the repository/ref.
- **Observability:** Prometheus scraping and Grafana dashboards make request behavior and workload changes measurable during load tests.
- **Autoscaling behavior:** HPA scale-up and scale-down behavior needs to be observed over time; stabilization windows prevent unnecessary replica churn.
- **Network isolation:** NetworkPolicy validation demonstrated that allowed application/monitoring traffic and blocked cross-namespace traffic must be tested explicitly.
- **Infrastructure lifecycle:** Terraform makes it possible to create and remove expensive demo infrastructure deliberately instead of leaving it running after validation.

## Future improvements

- Add automated unit/integration test coverage beyond endpoint smoke checks.
- Add image signing and provenance attestation (for example, Sigstore/cosign).
- Add dependency/SBOM scanning and a documented vulnerability remediation policy.
- Add TLS with a managed certificate and a custom domain for the public ingress.
- Add a documented promotion/approval strategy for production releases.
- Add automated deployment verification and rollback policy for the EKS environment.
- Add alert notification routing (for example, an explicitly configured Alertmanager receiver) and test delivery end to end.
- Add backup/restore and disaster-recovery exercises for stateful components and Terraform state.
- Add policy-as-code checks for Terraform and Kubernetes manifests.

## Cost and lifecycle note

The EKS environment in this project was deployed and validated as a demonstration, including worker nodes, ingress/load-balancer behavior, HPA scaling, Argo CD health, Prometheus scraping and Grafana dashboards. **The EKS demo infrastructure was subsequently destroyed after validation to avoid ongoing AWS charges.** Therefore, this README documents a completed deployment exercise; it does not claim that the EKS cluster or its load balancer is currently online.

The Terraform bootstrap/S3 remote-state and CI/ECR/OIDC resources were treated separately from the EKS demo stack. Check the current AWS account before applying or destroying anything; resource state may change after this README is published.

## License

This project is distributed under the [Apache License 2.0](LICENSE).
