"""Home route — serves the dashboard HTML."""
from flask import Blueprint, current_app, render_template
home_bp = Blueprint("home", __name__)

@home_bp.route("/", methods=["GET"])
def index():
    current_app.logger.info("Dashboard requested")
    return render_template("index.html",
        app_name=current_app.config["APP_NAME"],
        app_display_name=current_app.config["APP_DISPLAY_NAME"],
        app_tagline=current_app.config["APP_TAGLINE"],
        app_version=current_app.config["APP_VERSION"],
        api_version=current_app.config["API_VERSION"],
        developer_name=current_app.config["DEVELOPER_NAME"],
        developer_role=current_app.config["DEVELOPER_ROLE"],
        developer_github=current_app.config["DEVELOPER_GITHUB"],
        repo_url=current_app.config["REPO_URL"],
        env=current_app.config["ENV"],
        cloud_platform=current_app.config["CLOUD_PLATFORM"],
        git_commit=current_app.config["GIT_COMMIT"],
        build_date=current_app.config["BUILD_DATE"],
    )
