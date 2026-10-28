
"""Version endpoint."""

import platform
from importlib.metadata import PackageNotFoundError, version

from flask import Blueprint, current_app, jsonify

version_bp = Blueprint("version", __name__)


@version_bp.route("/version", methods=["GET"])
def version_info():
    try:
        flask_version = version("flask")
    except PackageNotFoundError:
        flask_version = "unknown"

    return (
        jsonify(
            {
                "app_version": current_app.config["APP_VERSION"],
                "api_version": current_app.config["API_VERSION"],
                "git_commit": current_app.config["GIT_COMMIT"],
                "build_date": current_app.config["BUILD_DATE"],
                "python_version": platform.python_version(),
                "flask_version": flask_version,
                "environment": current_app.config["ENV"],
                "repository": current_app.config["REPO_URL"],
            }
        ),
        200,
    )
