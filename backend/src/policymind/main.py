"""PolicyMind FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from policymind.core.config import Settings, get_settings, validate_production_settings
from policymind.core.errors import (
    DependencyUnavailable,
    PolicyMindError,
)
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

    # CRITICAL: override get_settings so every Depends(get_settings) returns
    # the SAME Settings instance used to create the app.  Without this, route
    # handlers resolve a fresh Settings() from the environment, which has a
    # different JWT_SECRET — breaking positive-path auth entirely.
    app.dependency_overrides[get_settings] = lambda: settings

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

    # API routers
    from policymind.api.v1.chat import router as chat_router
    from policymind.api.v1.documents import router as doc_router
    from policymind.api.v1.evaluations import router as eval_router
    from policymind.api.v1.graph import router as graph_router
    from policymind.api.v1.reviews import router as review_router
    from policymind.auth.router import router as auth_router

    app.include_router(auth_router)
    app.include_router(doc_router)
    app.include_router(chat_router)
    app.include_router(review_router)
    app.include_router(graph_router)
    app.include_router(eval_router)

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
