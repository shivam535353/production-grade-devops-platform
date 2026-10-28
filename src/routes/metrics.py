"""Runtime metrics endpoints: JSON diagnostics and Prometheus metrics."""

import time
from datetime import datetime, timezone

from flask import Blueprint, Response, current_app, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from src.services.system_service import SystemService

metrics_bp = Blueprint("metrics", __name__)

_START = time.monotonic()
_REQ_COUNT = 0

APP_UPTIME = Gauge(
    "clouddeploy_app_uptime_seconds",
    "Application uptime in seconds",
)
APP_REQUESTS = Counter(
    "clouddeploy_app_metrics_requests_total",
    "Requests made to the JSON metrics endpoint",
)
APP_INFO = Gauge(
    "clouddeploy_app_info",
    "Static application information",
    ["application", "version", "environment"],
)

HTTP_REQUESTS = Counter(
    "flask_http_request_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION = Histogram(
    "flask_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)


@metrics_bp.route("/metrics", methods=["GET"])
def metrics():
    """Existing JSON diagnostics endpoint."""
    global _REQ_COUNT
    _REQ_COUNT += 1
    APP_REQUESTS.inc()

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
                    "probes": {
                        "liveness": "/health",
                        "readiness": "/health",
                    },
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
    """Prometheus-compatible metrics endpoint."""
    APP_UPTIME.set(time.monotonic() - _START)
    APP_INFO.labels(
        application=current_app.config["APP_NAME"],
        version=current_app.config["APP_VERSION"],
        environment=current_app.config["ENV"],
    ).set(1)

    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
