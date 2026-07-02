"""RBAC and role-based access tests."""


class TestRBAC:
    """Role-based access control enforcement."""

    def test_missing_token_on_review_approve_returns_401(self):
        """POST /reviews/{id}/approve without token must return 401."""
        from fastapi.testclient import TestClient

        from policymind.core.config import Settings
        from policymind.main import create_app

        s = Settings(_env_file=None, ENVIRONMENT="test", JWT_SECRET="x" * 32, DATABASE_URL="sqlite+aiosqlite:///t.db")
        c = TestClient(create_app(settings=s))
        r = c.post("/api/v1/reviews/1/approve")
        assert r.status_code == 401

    def test_missing_token_on_eval_runs_returns_401(self):
        """POST /evaluations/runs without token must return 401."""
        from fastapi.testclient import TestClient

        from policymind.core.config import Settings
        from policymind.main import create_app

        s = Settings(_env_file=None, ENVIRONMENT="test", JWT_SECRET="x" * 32, DATABASE_URL="sqlite+aiosqlite:///t.db")
        c = TestClient(create_app(settings=s))
        r = c.post("/api/v1/evaluations/runs", json={})
        assert r.status_code == 401

    def test_chat_stream_requires_auth(self):
        """POST /chat/stream without token must return 401."""
        from fastapi.testclient import TestClient

        from policymind.core.config import Settings
        from policymind.main import create_app

        s = Settings(_env_file=None, ENVIRONMENT="test", JWT_SECRET="x" * 32, DATABASE_URL="sqlite+aiosqlite:///t.db")
        c = TestClient(create_app(settings=s))
        r = c.post("/api/v1/chat/stream", json={})
        assert r.status_code == 401
