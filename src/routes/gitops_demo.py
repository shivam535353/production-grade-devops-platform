"""
GitOps Demo Route
ArgoCD auto-deploy demonstration endpoint
"""

from flask import Blueprint, jsonify
from datetime import datetime, timezone

gitops_demo_bp = Blueprint("gitops_demo", __name__)


@gitops_demo_bp.route("/gitops-demo", methods=["GET"])
def gitops_demo():
    # ---------------------------------------------------------
    # INTENTIONAL BUG
    # This simulates a bad deployment for the GitOps rollback demo.
    result = 1 / 0

    # This code will never execute.
    return jsonify({
        "message": "This will never reach here",
        "deployed_at": datetime.now(timezone.utc).isoformat(),
        "status": "success"
    }), 200