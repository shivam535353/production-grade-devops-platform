"""
GitOps Demo Route
ArgoCD auto-deploy demonstration endpoint
"""

from flask import Blueprint, jsonify
from datetime import datetime, timezone

gitops_demo_bp = Blueprint("gitops_demo", __name__)


@gitops_demo_bp.route("/gitops-demo", methods=["GET"])
def gitops_demo():
    return (
        jsonify(
            {
                "message": "🚀 This endpoint was deployed via GitOps!",
                "workflow": {
                    "step_1": "Code changed in app.py",
                    "step_2": "git commit + git push to GitHub",
                    "step_3": "ArgoCD detected change",
                    "step_4": "Rolling update applied to Kubernetes",
                },
                "deployed_at": datetime.now(timezone.utc).isoformat(),
                "gitops_tool": "ArgoCD",
                "status": "success finally",
            }
        ),
        200,
    )
