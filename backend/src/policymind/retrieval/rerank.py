"""Reranker protocol."""

from typing import Protocol

from policymind.retrieval.ports import SearchHit


class Reranker(Protocol):
    """Protocol for reranking models."""

    async def rerank(
        self,
        query: str,
        candidates: list[SearchHit],
        limit: int,
    ) -> list[SearchHit]: ...


class NoOpReranker:
    """Pass-through reranker — preserves input order."""

    async def rerank(
        self,
        query: str,
        candidates: list[SearchHit],
        limit: int,
    ) -> list[SearchHit]:
        return candidates[:limit]
