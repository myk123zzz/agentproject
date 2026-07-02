"""FastAPI auth routes — login, refresh, me."""

from fastapi import APIRouter, Depends

from policymind.api.dependencies import RequestContext, get_current_context
from policymind.auth.schemas import LoginRequest, RefreshRequest, TokenPair, UserInfo
from policymind.auth.service import AuthService
from policymind.core.config import Settings, get_settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
async def login(
    body: LoginRequest,
    settings: Settings = Depends(get_settings),
) -> TokenPair:
    """Authenticate with tenant slug + username + password."""
    from policymind.infrastructure.postgres.session import create_engine_and_sessionmaker

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
    from policymind.infrastructure.postgres.session import create_engine_and_sessionmaker

    _, sessionmaker = create_engine_and_sessionmaker(settings)
    async with sessionmaker() as session:
        svc = AuthService(settings=settings, session=session)
        return await svc.refresh(body.refresh_token)


@router.get("/me", response_model=UserInfo)
async def me(
    ctx: RequestContext = Depends(get_current_context),
) -> UserInfo:
    """Return the authenticated user's info from JWT context."""
    return UserInfo(
        id=ctx.user_id,
        tenant_id=ctx.tenant_id,
        username=f"user-{ctx.user_id}",
        role=ctx.role,
        access_level=ctx.access_level,
    )
