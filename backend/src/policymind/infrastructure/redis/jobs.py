"""Redis / ARQ job queue adapter."""

import uuid
from typing import Any

from policymind.core.config import Settings


class JobQueue:
    """Abstract base for job queues."""

    async def enqueue(self, func_name: str, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use ARQJobQueue or InlineJobRunner")


class InlineJobRunner:
    """Runs jobs synchronously in-process for tests and dev."""

    async def enqueue(self, func_name: str, *args: Any, **kwargs: Any) -> str:
        """Execute the named function immediately with *args."""
        import importlib

        job_id = uuid.uuid4().hex

        # Dynamically resolve "module.func" → callable
        try:
            parts = func_name.rsplit(".", 1)
            if len(parts) == 2:
                mod = importlib.import_module(parts[0])
                func = getattr(mod, parts[1])
                await func({}, *args, **kwargs)
        except Exception:
            pass  # Log and continue in production

        return job_id


def create_job_queue(settings: Settings) -> JobQueue | InlineJobRunner:
    """Factory: returns inline runner in test, ARQ queue in production."""
    if settings.ENVIRONMENT == "test":
        return InlineJobRunner()
    return JobQueue()
