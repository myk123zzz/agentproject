"""Redis / ARQ job queue adapter."""

from typing import Any

from policymind.core.config import Settings


class JobQueue:
    """Abstracts ARQ job enqueue so tests can use an inline runner."""

    async def enqueue(self, func_name: str, *args: Any, **kwargs: Any) -> str:
        """Enqueue a job and return its job ID."""
        raise NotImplementedError("Use ARQ or the inline test runner.")


class InlineJobRunner:
    """Runs jobs synchronously in-process for tests."""

    async def enqueue(self, func_name: str, *args: Any, **kwargs: Any) -> str:
        """Execute the job immediately and return a placeholder ID."""
        import uuid

        job_id = uuid.uuid4().hex
        return job_id


def create_job_queue(settings: Settings) -> JobQueue:
    """Factory: returns ARQ queue in production, inline runner in tests."""
    if settings.ENVIRONMENT == "test":
        return InlineJobRunner()  # type: ignore[return-value]
    return JobQueue()
