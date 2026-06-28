"""Project info endpoint."""
from flask import Blueprint, current_app, jsonify
info_bp = Blueprint("info", __name__)

@info_bp.route("/info", methods=["GET"])
def info():
    return jsonify({
        "project": {
            "name": current_app.config["APP_NAME"],
            "display_name": current_app.config["APP_DISPLAY_NAME"],
            "tagline": current_app.config["APP_TAGLINE"],
            "version": current_app.config["APP_VERSION"],
            "api_version": current_app.config["API_VERSION"],
            "repository": current_app.config["REPO_URL"],
            "description": (
                "Production-Grade Cloud-Native CI/CD Platform on AWS EKS — "
                "fully automated DevSecOps pipeline featuring GitOps, Kubernetes "
                "orchestration, Helm packaging, ArgoCD delivery, Prometheus and Grafana."
            ),
        },
        "developer": {
            "name": current_app.config["DEVELOPER_NAME"],
            "role": current_app.config["DEVELOPER_ROLE"],
            "github": current_app.config["DEVELOPER_GITHUB"],
            "repository": current_app.config["REPO_URL"],
        },
        "deployment": {
            "environment": current_app.config["ENV"],
            "cloud_platform": current_app.config["CLOUD_PLATFORM"],
            "git_commit": current_app.config["GIT_COMMIT"],
            "build_date": current_app.config["BUILD_DATE"],
        },
        "features": [
            "Containerized Microservices", "Infrastructure as Code (Terraform)",
            "GitOps Continuous Delivery (ArgoCD)", "CI/CD Automation (GitHub Actions)",
            "Multi-Environment Deployments", "Horizontal Pod Autoscaling (HPA)",
            "Container Security Scanning (Trivy)", "Secrets Management",
            "Cloud Native Architecture", "Observability (Prometheus + Grafana)",
            "Production-Ready Health Checks", "DevSecOps Workflow",
        ],
    }), 200
