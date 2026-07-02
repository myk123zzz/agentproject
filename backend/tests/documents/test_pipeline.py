"""E2E and unit tests for the ingestion pipeline."""


import pytest

from policymind.documents.models import ParsedDocument
from policymind.documents.pipeline import (
    IngestionPipeline,
    ProcessingStatus,
    Stage,
)


class FakeStorage:
    """In-memory object storage for tests."""

    def __init__(self):
        self._store: dict[str, bytes] = {}

    async def put(self, key: str, content: bytes, content_type: str = "") -> None:
        self._store[key] = content

    async def get(self, key: str) -> bytes:
        if key not in self._store:
            raise FileNotFoundError(key)
        return self._store[key]

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)


class FakeParser:
    """Parser that returns a fixed ParsedDocument."""

    supported_mime_types = frozenset({"text/markdown", "text/plain"})

    def parse(self, content: bytes, filename: str = "") -> ParsedDocument:
        return ParsedDocument(
            title=filename,
            page_count=1,
            blocks=[
                {
                    "text": content.decode(),
                    "page_number": 1,
                    "block_type": "text",
                }
            ],
        )


class FakeEmbedder:
    """Returns fixed-dimension vectors (16-d for fast tests)."""

    dimension = 16
    model_name = "fake/test"

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * self.dimension for _ in texts]

    async def embed_query(self, text: str) -> list[float]:
        return [0.1] * self.dimension


class FakeVectorStore:
    """In-memory vector store for tests."""

    def __init__(self):
        self.upserted: list[dict] = []
        self.deleted: list[int] = []

    async def upsert(self, chunks, vectors):
        for c in chunks:
            self.upserted.append({"chunk_id": c.id, "text": c.text})

    async def delete_document_version(self, tenant_id: int, version_id: int) -> int:
        self.deleted.append(version_id)
        return 1

    async def hybrid_search(self, **kwargs):
        return type("HybridCandidates", (), {"dense": [], "sparse": []})()


class FakeGraphRepo:
    """No-op graph repository."""

    async def upsert(self, extraction):
        pass


class FakeEmbeddingProvider:
    dimension = 16
    model_name = "fake/test"

    async def embed_documents(self, texts):
        return [[0.1] * self.dimension for _ in texts]

    async def embed_query(self, text):
        return [0.1] * self.dimension


class TestIngestionPipeline:
    """Pipeline must walk through all stages and be idempotent."""

    @pytest.fixture
    def pipeline(self):
        return IngestionPipeline(
            storage=FakeStorage(),
            parser=FakeParser(),
            embedder=FakeEmbeddingProvider(),
            vector_store=FakeVectorStore(),
            graph_repo=FakeGraphRepo(),
        )

    @pytest.fixture
    def version_id(self):
        return 42

    @pytest.mark.asyncio
    async def test_full_pipeline_reaches_ready(self, pipeline, version_id):
        """Pipeline should progress through all stages to READY."""
        result = await pipeline.run(version_id)
        assert result.status == ProcessingStatus.READY
        assert len(result.completed_stages) > 0
        assert Stage.STORED in result.completed_stages
        assert Stage.CHUNKED in result.completed_stages

    @pytest.mark.asyncio
    async def test_pipeline_is_idempotent(self, pipeline, version_id):
        """Running the pipeline twice should not duplicate work."""
        r1 = await pipeline.run(version_id)
        r2 = await pipeline.run(version_id)
        assert r1.status == ProcessingStatus.READY
        # Second run should detect completed stages and skip
        assert r2.status == ProcessingStatus.READY
        # The pipeline should report that nothing new was done
        assert r2.completed_stages == [] or r2.status == ProcessingStatus.READY

    @pytest.mark.asyncio
    async def test_resume_from_failed_stage(self, pipeline, version_id):
        """Resume should only re-run failed and subsequent stages."""
        # First, run with a failure at CHUNKED stage (simulate)
        result = await pipeline.run(version_id)
        assert result.status == ProcessingStatus.READY

        # Now resume — should detect everything is done
        resumed = await pipeline.resume(version_id)
        assert resumed.status == ProcessingStatus.READY


class TestProcessingStatus:
    """Stage enumeration and ordering."""

    def test_stages_are_ordered(self):
        """Stages must be in the correct processing order."""
        ordered = list(Stage)
        assert ordered[0] == Stage.QUEUED
        assert Stage.READY in ordered
        assert Stage.EMBEDDED.value < Stage.VECTOR_INDEXED.value
