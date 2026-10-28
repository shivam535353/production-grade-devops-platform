import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_home_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_info_endpoint(client):
    response = client.get("/info")
    assert response.status_code == 200


def test_version_endpoint(client):
    response = client.get("/version")
    assert response.status_code == 200


def test_prometheus_metrics_endpoint(client):
    response = client.get("/metrics/prometheus")
    assert response.status_code == 200
    assert b"clouddeploy_app_uptime_seconds" in response.data