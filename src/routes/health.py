"""Health check — Kubernetes liveness/readiness probe."""
import platform, socket, time
from datetime import datetime, timezone
from flask import Blueprint, current_app, jsonify
from src.services.system_service import SystemService
health_bp = Blueprint("health", __name__)
_START = time.monotonic()

@health_bp.route("/health", methods=["GET"])
def health():
    uptime = round(time.monotonic() - _START, 2)
    return jsonify({
        "status": "healthy",
        "service": current_app.config["APP_NAME"],
        "version": current_app.config["APP_VERSION"],
        "api_version": current_app.config["API_VERSION"],
        "environment": current_app.config["ENV"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hostname": socket.gethostname(),
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "uptime_seconds": uptime,
        "checks": {"flask": "ok", "config": "ok", "memory": SystemService.memory_status()},
    }), 200
