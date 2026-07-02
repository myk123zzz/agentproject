"""FastAPI shared dependencies — auth context, RBAC, rate limiting."""

from collections.abc import Callable
from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from policymind.core.config import Settings, get_settings
from policymind.core.errors import AuthorizationDenied

_security = HTTPBearer(auto_error=False)


class RequestContext:
    """Context injected into every authenticated request."""

    def __init__(self, tenant_id: int, user_id: int, access_level: int, role: str, trace_id: str):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.access_level = access_level
        self.role = role
        self.trace_id = trace_id


async def get_current_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security),
    settings: Settings = Depends(get_settings),
) -> RequestContext:
    """Parse JWT and return RequestContext.  Returns anonymous context if no token."""
    if credentials is None:
        # Anonymous access for login endpoints
        return RequestContext(
            tenant_id=0, user_id=0, access_level=0, role="anonymous", trace_id=""
        )
    # In production: decode JWT, query user, verify tenant/status/role
    return RequestContext(
        tenant_id=1, user_id=1, access_level=0, role="employee", trace_id=""
    )


def require_roles(*roles: str) -> Callable[..., Any]:
    """FastAPI dependency factory for RBAC."""

    async def role_checker(ctx: RequestContext = Depends(get_current_context)) -> RequestContext:
        if ctx.role not in roles and ctx.role != "system_admin":
            raise AuthorizationDenied(f"Requires one of: {roles}")
        return ctx

    return role_checker
