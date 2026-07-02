"""Object storage abstraction — local filesystem and S3/MinIO."""

from pathlib import Path
from typing import Protocol


class ObjectStorage(Protocol):
    """Protocol for object storage adapters."""

    async def put(self, key: str, content: bytes, content_type: str) -> None: ...
    async def get(self, key: str) -> bytes: ...
    async def delete(self, key: str) -> None: ...


class LocalObjectStorage:
    """Stores objects on the local filesystem (dev and unit tests)."""

    def __init__(self, base_dir: str | Path = "./storage") -> None:
        self._base = Path(base_dir)

    async def put(self, key: str, content: bytes, content_type: str = "application/octet-stream") -> None:
        target = self._base / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    async def get(self, key: str) -> bytes:
        target = self._base / key
        if not target.is_file():
            raise FileNotFoundError(f"Object not found: {key}")
        return target.read_bytes()

    async def delete(self, key: str) -> None:
        target = self._base / key
        if target.is_file():
            target.unlink()
