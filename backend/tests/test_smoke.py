"""Smoke test: verify the policymind package and health endpoint exist."""

from fastapi.testclient import TestClient


def test_package_and_health():
    """Ensure the package has a version and the liveness endpoint responds."""
    import policymind

    assert policymind.__version__ == "0.1.0"

    from policymind.main import create_app

    app = create_app()
    client = TestClient(app)
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
