"""Embedding provider protocol and OpenAI-compatible implementation."""

from typing import Protocol


class EmbeddingProvider(Protocol):
    """Protocol for embedding services."""

    dimension: int
    model_name: str

    async def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    async def embed_query(self, text: str) -> list[float]: ...


class NoOpEmbeddingProvider:
    """Embedding provider for testing — returns fixed-dimension vectors."""

    dimension: int = 768
    model_name: str = "noop/test"

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * self.dimension for _ in texts]

    async def embed_query(self, text: str) -> list[float]:
        return [0.1] * self.dimension
