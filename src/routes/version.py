"""Version endpoint."""
import platform
from flask import Blueprint, current_app, jsonify
version_bp = Blueprint("version", __name__)

@version_bp.route("/version", methods=["GET"])
def version():
    try:
        import flask; fv = flask.__version__
    except Exception:
        fv = "unknown"
    return jsonify({
        "app_version": current_app.config["APP_VERSION"],
        "api_version": current_app.config["API_VERSION"],
        "git_commit": current_app.config["GIT_COMMIT"],
        "build_date": current_app.config["BUILD_DATE"],
        "python_version": platform.python_version(),
        "flask_version": fv,
        "environment": current_app.config["ENV"],
        "repository": current_app.config["REPO_URL"],
    }), 200
