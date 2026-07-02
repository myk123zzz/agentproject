"""Authentication service — login, refresh, token revocation."""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from policymind.auth.models import User
from policymind.auth.schemas import LoginRequest, TokenPair
from policymind.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from policymind.core.config import Settings
from policymind.core.errors import AuthenticationError


@dataclass
class AuthService:
    """Handles login, token refresh, and logout/revocation."""

    settings: Settings
    session: AsyncSession

    async def authenticate(self, login: LoginRequest) -> TokenPair:
        """Validate credentials and return token pair."""
        user = await self._lookup_user(login.username)
        if user is None or not verify_password(login.password, user.password_hash):
            raise AuthenticationError("invalid credentials")

        if not user.is_active:
            raise AuthenticationError("user is disabled")

        access = create_access_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            role=user.role.value,
            access_level=user.access_level,
            token_version=user.token_version,
            settings=self.settings,
        )
        refresh = create_refresh_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            token_version=user.token_version,
            settings=self.settings,
        )
        return TokenPair(access_token=access, refresh_token=refresh)

    async def refresh(self, refresh_token: str) -> TokenPair:
        """Validate a refresh token and issue a new pair."""
        try:
            payload = decode_token(refresh_token, self.settings)
        except Exception:
            raise AuthenticationError("invalid refresh token") from None

        if payload.get("typ") != "refresh":
            raise AuthenticationError("not a refresh token")

        user_id = int(payload["sub"])
        user = await self.session.get(User, user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("user not found or disabled")
        if payload.get("ver") != user.token_version:
            raise AuthenticationError("token has been revoked")

        access = create_access_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            role=user.role.value,
            access_level=user.access_level,
            token_version=user.token_version,
            settings=self.settings,
        )
        new_refresh = create_refresh_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            token_version=user.token_version,
            settings=self.settings,
        )
        return TokenPair(access_token=access, refresh_token=new_refresh)

    async def _lookup_user(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
