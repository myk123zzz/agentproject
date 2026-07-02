"""PolicyMind FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from policymind.core.config import Settings, get_settings, validate_production_settings
from policymind.core.errors import DependencyUnavailable, PolicyMindError
from policymind.core.logging import setup_logging


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan — no heavyweight resources on startup yet."""
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the PolicyMind FastAPI application.

    Tests pass a Settings instance; production reads from the environment.
    """
    if settings is None:
        settings = get_settings()

    validate_production_settings(settings)

    setup_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _register_routes(app, settings)

    return app


def _register_routes(app: FastAPI, settings: Settings) -> None:
    """Register health endpoints and API routers."""

    @app.get("/health/live")
    async def health_live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    async def health_ready() -> dict[str, str]:
        if settings.ENVIRONMENT == "production" and settings.JWT_SECRET == "change-me":
            raise DependencyUnavailable("invalid production configuration")
        return {"status": "ok"}

    # Auth routes — import later to avoid circular dependency
    from policymind.auth.router import router as auth_router

    app.include_router(auth_router)

    # Global exception handler
    @app.exception_handler(PolicyMindError)
    async def policymind_error_handler(_request: Any, exc: PolicyMindError) -> Any:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.code,
                "message": exc.public_message,
            },
        )
