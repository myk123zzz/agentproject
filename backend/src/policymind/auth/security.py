"""Password hashing and JWT token creation / verification."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from jose import jwt  # type: ignore[import-untyped]

from policymind.core.config import Settings

_ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a plaintext password with Argon2id."""
    return _ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Constant-time password verification against an Argon2id hash."""
    try:
        return _ph.verify(password_hash, password)
    except VerificationError:
        return False


def create_access_token(
    *,
    user_id: int,
    tenant_id: int,
    role: str,
    access_level: int,
    token_version: int,
    settings: Settings,
) -> str:
    """Issue a short-lived access token."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "tenant_id": tenant_id,
        "role": role,
        "access_level": access_level,
        "ver": token_version,
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "jti": uuid.uuid4().hex,
    }
    return str(jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM))


def create_refresh_token(
    *,
    user_id: int,
    tenant_id: int,
    token_version: int,
    settings: Settings,
) -> str:
    """Issue a longer-lived refresh token."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "tenant_id": tenant_id,
        "ver": token_version,
        "iat": now,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "jti": uuid.uuid4().hex,
        "typ": "refresh",
    }
    return str(jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM))


def decode_token(token: str, settings: Settings) -> dict[str, Any]:
    """Decode and validate a JWT.  Raises JWTError on failure."""
    return dict(jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]))
