"""RetrievalService — hybrid retrieval pipeline."""

import time
from datetime import UTC, datetime
from typing import Any

from policymind.retrieval.citations import build_citations
from policymind.retrieval.embeddings import EmbeddingProvider
from policymind.retrieval.fusion import rrf_fuse_simple
from policymind.retrieval.ports import RetrievalBundle, RetrievalTrace
from policymind.retrieval.rerank import Reranker


class RetrievalService:
    """Dense/BM25 → RRF → Rerank → Parent Expansion → Citations."""

    def __init__(
        self,
        *,
        embedder: EmbeddingProvider,
        reranker: Reranker,
        vector_store: Any,
    ):
        self._embedder = embedder
        self._reranker = reranker
        self._vector_store = vector_store

    async def retrieve(
        self,
        query: str,
        *,
        tenant_id: int,
        access_level: int,
        at: datetime | None = None,
        top_k: int = 8,
    ) -> RetrievalBundle:
        t0 = time.monotonic()
        trace = RetrievalTrace()
        at = at or datetime.now(UTC)

        query_vector = await self._embedder.embed_query(query)

        candidates = await self._vector_store.hybrid_search(
            query_text=query,
            query_vector=query_vector,
            tenant_id=tenant_id,
            access_level=access_level,
            at=at,
            limit_per_channel=30,
        )
        trace.dense_hits = len(candidates.dense)
        trace.bm25_hits = len(candidates.sparse)

        fused = rrf_fuse_simple(candidates.dense, candidates.sparse, limit=30)
        trace.fused_count = len(fused)

        try:
            reranked = await self._reranker.rerank(query, fused, limit=top_k)
            trace.rerank_count = len(reranked)
            trace.rerank_used = True
        except Exception:
            reranked = fused[:top_k]
            trace.error = "rerank_degraded"
            trace.rerank_used = False

        trace.final_count = len(reranked)
        citations = build_citations(reranked)

        context_parts: list[str] = []
        for cit in citations:
            context_parts.append(
                f"[{cit.id}] {cit.document_name} p.{cit.page_number}: {cit.quote}"
            )
        context = "\n\n".join(context_parts)

        trace.latency_ms = (time.monotonic() - t0) * 1000

        return RetrievalBundle(
            query=query,
            hits=reranked,
            citations=citations,
            context=context,
            trace=trace,
        )
