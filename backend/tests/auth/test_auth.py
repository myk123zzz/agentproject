"""Tests for authentication, tenant isolation, and RBAC."""

import pytest

from policymind.core.config import Settings, validate_production_settings
from policymind.main import create_app


class TestProductionSafety:
    """Security checks for production deployments."""

    def test_validate_production_rejects_default_jwt(self):
        """Production must reject known-waak JWT secrets."""
        settings = Settings(ENVIRONMENT="production", JWT_SECRET="change-me")
        with pytest.raises(ValueError, match="JWT_SECRET"):
            validate_production_settings(settings)

    def test_validate_production_rejects_short_jwt(self):
        """Production JWT must be at least 32 characters."""
        settings = Settings(ENVIRONMENT="production", JWT_SECRET="sh0rt")
        with pytest.raises(ValueError, match="32"):
            validate_production_settings(settings)

    def test_validate_production_rejects_wildcard_cors(self):
        """Production CORS must not contain wildcard."""
        settings = Settings(
            ENVIRONMENT="production",
            JWT_SECRET="a-strong-secret-with-32-chars!!!",
            CORS_ORIGINS=["*"],
        )
        with pytest.raises(ValueError, match="CORS"):
            validate_production_settings(settings)

    def test_validate_production_allows_valid_config(self):
        """Valid production config should pass validation."""
        settings = Settings(
            ENVIRONMENT="production",
            JWT_SECRET="a-strong-production-secret-32chars!",
            CORS_ORIGINS=["https://policymind.example.com"],
        )
        validate_production_settings(settings)  # should not raise

    def test_create_app_calls_validation(self):
        """create_app with default secret in production should fail fast."""
        settings = Settings(ENVIRONMENT="production", JWT_SECRET="change-me")
        with pytest.raises(ValueError, match="JWT_SECRET"):
            create_app(settings=settings)

    def test_dev_settings_pass_validation(self):
        """Development mode allows weak secrets (for local dev convenience)."""
        settings = Settings(ENVIRONMENT="development", JWT_SECRET="change-me")
        app = create_app(settings=settings)
        from fastapi.testclient import TestClient

        client = TestClient(app)
        r = client.get("/health/live")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


class TestPasswordHashing:
    """Argon2id password hashing correctness."""

    def test_hash_and_verify(self):
        from policymind.auth.security import hash_password, verify_password

        hashed = hash_password("correct-horse-battery-staple")
        assert verify_password("correct-horse-battery-staple", hashed) is True

    def test_verify_wrong_password(self):
        from policymind.auth.security import hash_password, verify_password

        hashed = hash_password("secret-123")
        assert verify_password("wrong-password", hashed) is False


class TestJWT:
    """JWT token creation and decoding."""

    def test_create_and_decode_access_token(self):
        from policymind.auth.security import create_access_token, decode_token

        settings = Settings(
            JWT_SECRET="test-secret-32-chars-long!!!!!",
            ACCESS_TOKEN_EXPIRE_MINUTES=15,
        )
        token = create_access_token(
            user_id=42,
            tenant_id=1,
            role="employee",
            access_level=0,
            token_version=1,
            settings=settings,
        )
        payload = decode_token(token, settings)
        assert payload["sub"] == "42"
        assert payload["tenant_id"] == 1
        assert payload["role"] == "employee"
        assert payload["ver"] == 1

    def test_decode_tampered_token_fails(self):
        from jose import JWTError

        from policymind.auth.security import create_access_token, decode_token

        settings = Settings(
            JWT_SECRET="test-secret-32-chars-long!!!!!",
            ACCESS_TOKEN_EXPIRE_MINUTES=15,
        )
        token = create_access_token(
            user_id=42,
            tenant_id=1,
            role="employee",
            access_level=0,
            token_version=1,
            settings=settings,
        )
        # Tamper with the token
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        with pytest.raises(JWTError):
            decode_token(tampered, settings)

    def test_refresh_token_has_correct_type(self):
        from policymind.auth.security import create_refresh_token, decode_token

        settings = Settings(
            JWT_SECRET="test-secret-32-chars-long!!!!!",
            REFRESH_TOKEN_EXPIRE_DAYS=7,
        )
        token = create_refresh_token(
            user_id=42,
            tenant_id=1,
            token_version=1,
            settings=settings,
        )
        payload = decode_token(token, settings)
        assert payload["typ"] == "refresh"
