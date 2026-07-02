"""Milvus vector store adapter (production) and in-memory adapter (testing)."""

from datetime import datetime
from typing import Any

from policymind.retrieval.ports import HybridCandidates, SearchHit


class MemoryVectorStore:
    """In-memory vector store for unit tests — no Milvus dependency."""

    def __init__(self) -> None:
        self._chunks: list[dict[str, Any]] = []

    async def upsert(self, chunks: list[Any], vectors: list[list[float]]) -> None:
        for chunk, vector in zip(chunks, vectors, strict=False):
            self._chunks.append({
                "chunk_id": chunk.id if hasattr(chunk, "id") else chunk.get("id", ""),
                "text": chunk.text if hasattr(chunk, "text") else chunk.get("text", ""),
                "vector": vector,
                "tenant_id": getattr(chunk, "tenant_id", 1),
                "access_level": getattr(chunk, "access_level", 0),
                "page_number": getattr(chunk, "page_number", 1),
                "document_name": getattr(chunk, "document_name", "test"),
                "document_version": getattr(chunk, "document_version", "1.0"),
                "document_version_id": getattr(chunk, "document_version_id", 1),
                "effective_from": getattr(chunk, "effective_from", None),
                "effective_to": getattr(chunk, "effective_to", None),
            })

    async def hybrid_search(
        self,
        *,
        query_text: str,
        query_vector: list[float],
        tenant_id: int,
        access_level: int,
        at: datetime,
        limit_per_channel: int = 30,
    ) -> HybridCandidates:
        # Filter by tenant and access level
        allowed = [
            c for c in self._chunks
            if c["tenant_id"] == tenant_id and c["access_level"] <= access_level
        ]
        # Simple TF-based BM25 simulation
        dense_hits: list[SearchHit] = []
        sparse_hits: list[SearchHit] = []

        for i, chunk in enumerate(allowed[:limit_per_channel]):
            score = 0.9 - i * 0.02
            hit = SearchHit(
                chunk_id=chunk["chunk_id"],
                text=chunk["text"],
                score=score,
                channel="dense",
                rank=i + 1,
                page_number=chunk.get("page_number", 1),
                document_name=chunk.get("document_name", "test"),
                document_version=chunk.get("document_version", "1.0"),
            )
            dense_hits.append(hit)

            # Simulate BM25 with keyword match bonus
            bm25_score = 0.0
            query_terms = query_text.lower().split()
            chunk_text = chunk["text"].lower()
            for term in query_terms:
                if term in chunk_text:
                    bm25_score += 0.3
            if bm25_score > 0:
                hit2 = SearchHit(
                    chunk_id=chunk["chunk_id"],
                    text=chunk["text"],
                    score=min(bm25_score, 0.95),
                    channel="bm25",
                    rank=i + 1,
                    page_number=chunk.get("page_number", 1),
                    document_name=chunk.get("document_name", "test"),
                    document_version=chunk.get("document_version", "1.0"),
                )
                sparse_hits.append(hit2)

        return HybridCandidates(dense=dense_hits, sparse=sparse_hits)

    async def delete_document_version(self, tenant_id: int, version_id: int) -> int:
        before = len(self._chunks)
        self._chunks = [
            c for c in self._chunks
            if not (c["tenant_id"] == tenant_id and c.get("document_version_id") == version_id)
        ]
        return before - len(self._chunks)
