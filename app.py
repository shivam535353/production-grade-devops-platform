"""
production-grade-devops-platform — Flask Application Factory
GitHub : https://github.com/shivam535353/production-grade-devops-platform
Author : Shivam Gadilkar
"""

import logging, sys
from flask import Flask, jsonify
from src.config import get_config
from src.routes.home import home_bp
from src.routes.health import health_bp
from src.routes.info import info_bp
from src.routes.version import version_bp
from src.routes.metrics import metrics_bp
from src.routes.tech_stack import tech_stack_bp
from src.routes.developer import developer_bp


def _configure_logging(app):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    ))
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(handler.level)
    app.logger.propagate = False


def _register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(exc):
        return jsonify({"status": "error", "code": 404,
                        "message": "Resource not found.",
                        "hint": "Visit / for the dashboard."}), 404

    @app.errorhandler(500)
    def internal_error(exc):
        app.logger.exception("500 — %s", exc)
        return jsonify({"status": "error", "code": 500,
                        "message": "An unexpected error occurred."}), 500

    @app.errorhandler(405)
    def method_not_allowed(exc):
        return jsonify({"status": "error", "code": 405,
                        "message": "HTTP method not allowed."}), 405


def _register_security_headers(app):
    @app.after_request
    def add_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"]        = "DENY"
        response.headers["X-XSS-Protection"]       = "1; mode=block"
        response.headers["Referrer-Policy"]        = "strict-origin-when-cross-origin"
        response.headers["Server"]                 = "DevOpsPlatform/1.0"
        return response


def create_app(env=None):
    app = Flask(
        __name__,
        template_folder="src/templates",
        static_folder="src/static",
    )
    app.config.from_object(get_config(env))
    _configure_logging(app)
    _register_security_headers(app)
    _register_error_handlers(app)

    for bp in [home_bp, health_bp, info_bp, version_bp,
               metrics_bp, tech_stack_bp, developer_bp]:
        app.register_blueprint(bp)
        app.logger.debug("Registered blueprint: %s", bp.name)

    app.logger.info("DevOps Platform started — env=%s debug=%s",
                    app.config["ENV"], app.debug)
    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=application.debug, use_reloader=True)
