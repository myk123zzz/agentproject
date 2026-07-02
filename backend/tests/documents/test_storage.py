"""Contract tests for object storage adapters."""

import pytest

from policymind.documents.storage import LocalObjectStorage


class TestLocalObjectStorage:
    """Local filesystem storage adapter."""

    @pytest.fixture
    def storage(self, tmp_path):
        return LocalObjectStorage(base_dir=tmp_path)

    @pytest.mark.asyncio
    async def test_put_and_get(self, storage):
        """Should round-trip content through storage."""
        await storage.put("test/key.txt", b"hello world", "text/plain")
        result = await storage.get("test/key.txt")
        assert result == b"hello world"

    @pytest.mark.asyncio
    async def test_delete(self, storage):
        """Deleted keys must not be retrievable."""
        await storage.put("test/key.txt", b"temp", "text/plain")
        await storage.delete("test/key.txt")
        with pytest.raises(FileNotFoundError):
            await storage.get("test/key.txt")

    @pytest.mark.asyncio
    async def test_get_missing_raises(self, storage):
        """Non-existent keys must raise."""
        with pytest.raises(FileNotFoundError):
            await storage.get("nonexistent/key.txt")
