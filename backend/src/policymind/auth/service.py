"""Authentication service — tenant-scoped login, refresh, revocation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from policymind.auth.models import Tenant, User
from policymind.auth.schemas import LoginRequest, TokenPair
from policymind.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from policymind.core.config import Settings
from policymind.core.errors import AuthenticationError


class AuthService:
    """Handles tenant-scoped login, token refresh, and logout/revocation."""

    def __init__(self, settings: Settings, session: AsyncSession):
        self._settings = settings
        self._session = session

    async def authenticate(self, login: LoginRequest) -> TokenPair:
        """Validate tenant slug + username + password, return token pair."""
        # Look up tenant first
        tenant_stmt = select(Tenant).where(Tenant.slug == login.tenant_slug)
        tenant_result = await self._session.execute(tenant_stmt)
        tenant = tenant_result.scalar_one_or_none()
        if tenant is None:
            raise AuthenticationError("invalid tenant or credentials")

        # Look up user within that tenant
        user_stmt = select(User).where(
            User.tenant_id == tenant.id,
            User.username == login.username,
        )
        user_result = await self._session.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        if user is None or not verify_password(login.password, user.password_hash):
            raise AuthenticationError("invalid tenant or credentials")

        if not user.is_active:
            raise AuthenticationError("user is disabled")

        access = create_access_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            role=user.role.value,
            access_level=user.access_level,
            token_version=user.token_version,
            settings=self._settings,
        )
        refresh = create_refresh_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            token_version=user.token_version,
            settings=self._settings,
        )
        return TokenPair(access_token=access, refresh_token=refresh)

    async def refresh(self, refresh_token: str) -> TokenPair:
        """Validate a refresh token and issue a new pair."""
        try:
            payload = decode_token(refresh_token, self._settings)
        except Exception:
            raise AuthenticationError("invalid refresh token") from None

        if payload.get("typ") != "refresh":
            raise AuthenticationError("not a refresh token")

        user_id = int(payload["sub"])
        tenant_id = int(payload.get("tenant_id", 0))
        user = await self._session.get(User, user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("user not found or disabled")
        if user.tenant_id != tenant_id:
            raise AuthenticationError("tenant mismatch")
        if payload.get("ver") != user.token_version:
            raise AuthenticationError("token has been revoked")

        access = create_access_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            role=user.role.value,
            access_level=user.access_level,
            token_version=user.token_version,
            settings=self._settings,
        )
        new_refresh = create_refresh_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            token_version=user.token_version,
            settings=self._settings,
        )
        return TokenPair(access_token=access, refresh_token=new_refresh)
