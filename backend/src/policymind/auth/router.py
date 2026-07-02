"""FastAPI auth routes — login, refresh, logout, me."""

from fastapi import APIRouter, Depends

from policymind.auth.schemas import LoginRequest, RefreshRequest, TokenPair, UserInfo
from policymind.auth.service import AuthService
from policymind.core.config import Settings, get_settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
async def login(
    body: LoginRequest,
    settings: Settings = Depends(get_settings),
) -> TokenPair:
    """Authenticate and return access + refresh tokens."""
    # Import inside to avoid circular dependency at module level.
    from policymind.infrastructure.postgres.session import (
        create_engine_and_sessionmaker,
    )

    _, sessionmaker = create_engine_and_sessionmaker(settings)
    async with sessionmaker() as session:
        svc = AuthService(settings=settings, session=session)
        return await svc.authenticate(body)


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    body: RefreshRequest,
    settings: Settings = Depends(get_settings),
) -> TokenPair:
    """Exchange a refresh token for a new token pair."""
    from policymind.infrastructure.postgres.session import (
        create_engine_and_sessionmaker,
    )

    _, sessionmaker = create_engine_and_sessionmaker(settings)
    async with sessionmaker() as session:
        svc = AuthService(settings=settings, session=session)
        return await svc.refresh(body.refresh_token)


@router.get("/me", response_model=UserInfo)
async def me(
    settings: Settings = Depends(get_settings),
) -> UserInfo:
    """Return the current user's info (placeholder — JWT parsing real in Task 8)."""
    return UserInfo(
        id=1,
        tenant_id=1,
        username="placeholder",
        role="employee",
        access_level=0,
    )
