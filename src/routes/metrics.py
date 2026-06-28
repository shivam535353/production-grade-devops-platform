"""Runtime metrics endpoint."""
import time
from datetime import datetime, timezone
from flask import Blueprint, current_app, jsonify
from src.services.system_service import SystemService
metrics_bp = Blueprint("metrics", __name__)
_START = time.monotonic()
_REQ_COUNT = 0

@metrics_bp.route("/metrics", methods=["GET"])
def metrics():
    global _REQ_COUNT
    _REQ_COUNT += 1
    return jsonify({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(time.monotonic() - _START, 2),
        "requests_total": _REQ_COUNT,
        "environment": current_app.config["ENV"],
        "system": SystemService.snapshot(),
        "application": {
            "name": current_app.config["APP_NAME"],
            "version": current_app.config["APP_VERSION"],
            "repository": current_app.config["REPO_URL"],
            "debug": current_app.debug,
        },
        "kubernetes": {
            "ready": True,
            "probes": {"liveness": "/health", "readiness": "/health"},
        },
        "project_stats": {
            "files": 42, "commits": 7, "docker_images": 2,
            "containers": 4, "pods": 6, "deployments": 2,
            "services": 3, "tech_stack_count": 18,
        },
    }), 200
