"""Technology stack endpoint."""
from flask import Blueprint, jsonify
tech_stack_bp = Blueprint("tech_stack", __name__)

_STACK = [
    {"name":"Docker",         "category":"Containerisation","description":"Container runtime & image build"},
    {"name":"Kubernetes",     "category":"Orchestration",   "description":"Production-grade container orchestration"},
    {"name":"Minikube",       "category":"Local Dev",       "description":"Local Kubernetes cluster for development"},
    {"name":"Helm",           "category":"Packaging",       "description":"Kubernetes package manager"},
    {"name":"Terraform",      "category":"IaC",             "description":"Infrastructure as Code provisioning"},
    {"name":"GitHub Actions", "category":"CI/CD",           "description":"Automated CI/CD pipelines"},
    {"name":"ArgoCD",         "category":"GitOps",          "description":"Declarative GitOps continuous delivery"},
    {"name":"Prometheus",     "category":"Observability",   "description":"Metrics collection and alerting"},
    {"name":"Grafana",        "category":"Observability",   "description":"Metrics visualisation and dashboards"},
    {"name":"Trivy",          "category":"Security",        "description":"Container vulnerability scanning"},
    {"name":"AWS EKS",        "category":"Cloud",           "description":"Managed Kubernetes on AWS"},
    {"name":"Linux",          "category":"OS",              "description":"Production server operating system"},
    {"name":"Python",         "category":"Language",        "description":"Primary backend language"},
    {"name":"Flask",          "category":"Framework",       "description":"Lightweight WSGI web framework"},
    {"name":"Git",            "category":"VCS",             "description":"Distributed version control"},
    {"name":"GitHub",         "category":"VCS",             "description":"Source code hosting & collaboration"},
    {"name":"YAML",           "category":"Config",          "description":"Kubernetes & pipeline configuration"},
    {"name":"Containerd",     "category":"Runtime",         "description":"Industry-standard container runtime"},
]

@tech_stack_bp.route("/tech-stack", methods=["GET"])
def tech_stack():
    cats: dict = {}
    for t in _STACK:
        cats.setdefault(t["category"], []).append(t)
    return jsonify({"total": len(_STACK), "technologies": _STACK, "by_category": cats}), 200
