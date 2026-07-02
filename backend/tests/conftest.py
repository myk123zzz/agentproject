"""Shared test fixtures for the policymind test suite."""

import pytest
from fastapi.testclient import TestClient

from policymind.core.config import Settings
from policymind.main import create_app


@pytest.fixture
def settings() -> Settings:
    """Return test settings (non-production, safe defaults)."""
    return Settings(
        _env_file=None,
        ENVIRONMENT="test",
        JWT_SECRET="test-jwt-secret-for-testing-only",
        DATABASE_URL="sqlite+aiosqlite:///test.db",
    )


@pytest.fixture
def client(settings: Settings) -> TestClient:
    """Create a TestClient with test settings."""
    app = create_app(settings=settings)
    with TestClient(app) as c:
        yield c
