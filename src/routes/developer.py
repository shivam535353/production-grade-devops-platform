"""Developer profile endpoint."""
from flask import Blueprint, current_app, jsonify
developer_bp = Blueprint("developer", __name__)

@developer_bp.route("/developer", methods=["GET"])
def developer():
    return jsonify({
        "name": current_app.config["DEVELOPER_NAME"],
        "role": current_app.config["DEVELOPER_ROLE"],
        "github": current_app.config["DEVELOPER_GITHUB"],
        "repository": current_app.config["REPO_URL"],
        "specialisations": [
            "DevSecOps Engineering", "Cloud Infrastructure (AWS)",
            "Kubernetes & Container Orchestration", "CI/CD Pipeline Design",
            "Infrastructure as Code (Terraform)", "GitOps (ArgoCD)",
            "Observability & Monitoring", "Container Security",
        ],
        "project": {
            "name": current_app.config["APP_NAME"],
            "version": current_app.config["APP_VERSION"],
            "environment": current_app.config["ENV"],
        },
    }), 200
