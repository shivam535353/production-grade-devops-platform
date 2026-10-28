"""Runtime metrics endpoints."""

import time
from datetime import datetime, timezone

from flask import Blueprint, Response, current_app, jsonify

from src.services.system_service import SystemService

metrics_bp = Blueprint("metrics", __name__)
_START = time.monotonic()
_REQ_COUNT = 0
_PROMETHEUS_CONTENT_TYPE = "text/plain; version=0.0.4; charset=utf-8"


def _escape_label(value):
    """Escape a label value for Prometheus text exposition."""
    return str(value).replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


@metrics_bp.route("/metrics", methods=["GET"])
def metrics():
    """Return runtime metrics as JSON."""
    global _REQ_COUNT
    _REQ_COUNT += 1

    return (
        jsonify(
            {
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
                    "files": 42,
                    "commits": 7,
                    "docker_images": 2,
                    "containers": 4,
                    "pods": 6,
                    "deployments": 2,
                    "services": 3,
                    "tech_stack_count": 18,
                },
            }
        ),
        200,
    )


@metrics_bp.route("/metrics/prometheus", methods=["GET"])
def prometheus_metrics():
    """Expose application metrics in Prometheus text format."""
    labels = ",".join(
        f'{key}="{_escape_label(value)}"'
        for key, value in (
            ("application", current_app.config["APP_NAME"]),
            ("version", current_app.config["APP_VERSION"]),
            ("environment", current_app.config["ENV"]),
        )
    )

    body = (
        "# HELP clouddeploy_app_uptime_seconds Application uptime in seconds\n"
        "# TYPE clouddeploy_app_uptime_seconds gauge\n"
        f"clouddeploy_app_uptime_seconds {time.monotonic() - _START}\n"
        "# HELP clouddeploy_app_metrics_requests_total Requests made to the JSON metrics endpoint\n"
        "# TYPE clouddeploy_app_metrics_requests_total counter\n"
        f"clouddeploy_app_metrics_requests_total {_REQ_COUNT}\n"
        "# HELP clouddeploy_app_info Static application information\n"
        "# TYPE clouddeploy_app_info gauge\n"
        f"clouddeploy_app_info{{{labels}}} 1\n"
    )

    return Response(body, mimetype=_PROMETHEUS_CONTENT_TYPE)
