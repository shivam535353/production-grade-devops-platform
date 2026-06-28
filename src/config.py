"""production-grade-devops-platform — Configuration"""
from __future__ import annotations
import os
from datetime import datetime

class BaseConfig:
    APP_NAME: str         = "production-grade-devops-platform"
    APP_DISPLAY_NAME: str = "DevOps Platform"
    APP_TAGLINE: str      = "Multi-Environment CI/CD Pipeline with Kubernetes, GitOps & Cloud Automation"
    APP_VERSION: str      = "1.0.0"
    API_VERSION: str      = "v1"
    DEVELOPER_NAME: str   = "Shivam Gadilkar"
    DEVELOPER_ROLE: str   = "DevSecOps Engineer | DevOps Engineer | Cloud Enthusiast"
    DEVELOPER_GITHUB: str = "https://github.com/shivam535353"
    REPO_URL: str         = "https://github.com/shivam535353/production-grade-devops-platform"
    SECRET_KEY: str       = os.environ.get("SECRET_KEY", os.urandom(32).hex())
    JSON_SORT_KEYS: bool  = False
    JSONIFY_PRETTYPRINT_REGULAR: bool = True
    BUILD_DATE: str       = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    GIT_COMMIT: str       = os.environ.get("GIT_COMMIT", "local-dev")
    CLOUD_PLATFORM: str   = os.environ.get("CLOUD_PLATFORM", "AWS EKS")
    TESTING: bool = False
    DEBUG: bool   = False
    ENV: str      = "production"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024

class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    ENV: str    = "development"

class ProductionConfig(BaseConfig):
    DEBUG: bool = False
    ENV: str    = "production"
    JSONIFY_PRETTYPRINT_REGULAR: bool = False
    SECRET_KEY: str = os.environ.get("SECRET_KEY", BaseConfig.SECRET_KEY)

class TestingConfig(BaseConfig):
    TESTING: bool = True
    DEBUG: bool   = True
    ENV: str      = "testing"
    SECRET_KEY: str = "test-secret-key"

_MAP = {"development": DevelopmentConfig, "production": ProductionConfig, "testing": TestingConfig}

def get_config(env=None):
    return _MAP.get((env or os.environ.get("APP_ENV", "development")).lower(), DevelopmentConfig)()
