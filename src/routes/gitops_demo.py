"""
GitOps Demo Route
ArgoCD auto-deploy demonstrate करण्यासाठी नवीन endpoint
"""
from flask import Blueprint, jsonify
from datetime import datetime, timezone

gitops_demo_bp = Blueprint("gitops_demo", __name__)


@gitops_demo_bp.route("/gitops-demo", methods=["GET"])
def gitops_demo():
    return jsonify({
        "message": "🚀 This endpoint was deployed via GitOps!",
        "workflow": {
            "step_1": "Code changed in app.py",
            "step_2": "git commit + git push to GitHub",
            "step_3": "ArgoCD detected change in 3 minutes",
            "step_4": "ArgoCD rendered Helm chart",
            "step_5": "Rolling update applied to Kubernetes",
            "step_6": "New pod is serving this response"
        },
        "deployed_at": datetime.now(timezone.utc).isoformat(),
        "gitops_tool": "ArgoCD",
        "cluster": "Minikube (dev namespace)",
        "status": "success"
    }), 200