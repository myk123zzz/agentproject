"""PolicyMind FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan — no heavyweight resources on startup yet."""
    yield


def create_app() -> FastAPI:
    """Create and configure the PolicyMind FastAPI application."""
    app = FastAPI(
        title="PolicyMind",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health/live")
    async def health_live() -> dict[str, str]:
        """Liveness check — process is alive."""
        return {"status": "ok"}

    return app
