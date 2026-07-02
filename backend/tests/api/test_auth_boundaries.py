"""Auth boundary tests — tenant isolation, token validation, RBAC."""

import pytest
from fastapi.testclient import TestClient

from policymind.core.config import Settings
from policymind.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        _env_file=None,
        ENVIRONMENT="test",
        JWT_SECRET="test-jwt-secret-32-chars-long!!",
        DATABASE_URL="sqlite+aiosqlite:///test.db",
    )


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    app = create_app(settings=test_settings)
    with TestClient(app) as c:
        yield c


class TestConfigIsolation:
    """Host environment must not leak into app settings."""

    def test_host_debug_variable_does_not_override_app_settings(self, monkeypatch):
        """Host DEBUG env var must not affect Settings.DEBUG."""
        monkeypatch.setenv("DEBUG", "release")
        settings = Settings(_env_file=None)
        assert settings.DEBUG is False

    def test_settings_have_namespace_prefix(self):
        """Settings must use POLICYMIND_ prefix to avoid collisions."""
        assert Settings.model_config.get("env_prefix") == "POLICYMIND_"


class TestAuthBoundaries:
    """Authentication and authorization must reject invalid/missing credentials."""

    def test_no_token_returns_401_on_protected_endpoint(self, client):
        """Anonymous requests to /auth/me must return 401."""
        r = client.get("/api/v1/auth/me")
        assert r.status_code == 401

    def test_fake_bearer_token_is_rejected(self, client):
        """A non-JWT bearer token must be rejected with 401."""
        r = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer definitely-not-a-jwt"},
        )
        assert r.status_code == 401

    def test_documents_require_auth(self, client):
        """POST /documents without auth must return 401."""
        r = client.post("/api/v1/documents/", json={"logical_name": "test"})
        assert r.status_code == 401

    def test_graph_rejects_anonymous(self, client):
        """Graph endpoint without auth must return 401."""
        r = client.get("/api/v1/graph/subgraph")
        assert r.status_code == 401

    def test_reviews_require_auth(self, client):
        """Reviews endpoint without auth must return 401."""
        r = client.get("/api/v1/reviews/")
        assert r.status_code == 401
