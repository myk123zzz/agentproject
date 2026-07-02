"""RRF (Reciprocal Rank Fusion) and related utilities."""

from collections.abc import Mapping, Sequence

from policymind.retrieval.ports import SearchHit


def rrf_fuse(
    channels: Mapping[str, Sequence[SearchHit]],
    weights: Mapping[str, float],
    *,
    k: int = 60,
    limit: int = 30,
) -> list[SearchHit]:
    """Fuse ranked results from multiple channels using Reciprocal Rank Fusion.

    score(d) = Σ weight(channel) / (k + rank(channel, d))
    """
    scores: dict[str, float] = {}
    best_hits: dict[str, SearchHit] = {}

    for channel, hits in channels.items():
        w = weights.get(channel, 0.0)
        for hit in hits:
            rrf = w / (k + hit.rank)
            if hit.chunk_id in scores:
                scores[hit.chunk_id] += rrf
            else:
                scores[hit.chunk_id] = rrf
                best_hits[hit.chunk_id] = hit

    # Sort by fused score descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    result: list[SearchHit] = []
    for chunk_id, fused_score in ranked[:limit]:
        hit = best_hits[chunk_id]
        hit.score = fused_score
        result.append(hit)

    return result


def rrf_fuse_simple(
    dense: Sequence[SearchHit],
    sparse: Sequence[SearchHit],
    *,
    k: int = 60,
    dense_weight: float = 0.6,
    sparse_weight: float = 0.4,
    limit: int = 30,
) -> list[SearchHit]:
    """Convenience wrapper for the common Dense + BM25 case."""
    return rrf_fuse(
        channels={"dense": dense, "bm25": sparse},
        weights={"dense": dense_weight, "bm25": sparse_weight},
        k=k,
        limit=limit,
    )
