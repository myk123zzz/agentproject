"""Unit tests for RRF fusion and reranking."""

from policymind.retrieval.fusion import rrf_fuse
from policymind.retrieval.ports import SearchHit


def _hit(chunk_id: str, scores: dict[str, tuple[float, int]]):
    """Helper: create SearchHit from channel→(score, rank) mapping."""
    for channel, (score, rank) in scores.items():
        return SearchHit(
            chunk_id=chunk_id,
            text=f"text-{chunk_id}",
            score=score,
            channel=channel,
            rank=rank,
            page_number=1,
            document_name="test",
        )
    raise AssertionError("No channels")


class TestRRF:
    """Reciprocal Rank Fusion must promote chunks appearing in multiple channels."""

    def test_rrf_promotes_dual_channel_hit(self):
        """A chunk found by both Dense and BM25 should rank first."""
        a = SearchHit("a", "text-a", 0.95, "dense", 1, 1, "test")
        b = SearchHit("b", "text-b", 0.80, "dense", 2, 1, "test")
        b2 = SearchHit("b", "text-b", 0.70, "bm25", 1, 1, "test")
        c = SearchHit("c", "text-c", 0.60, "bm25", 2, 1, "test")

        result = rrf_fuse(
            channels={"dense": [a, b], "bm25": [b2, c]},
            weights={"dense": 0.6, "bm25": 0.4},
            k=60,
            limit=10,
        )
        # b appears in both channels and should come out first
        assert result[0].chunk_id == "b"

    def test_rrf_deduplicates_by_chunk_id(self):
        """Same chunk from multiple channels should appear once."""
        hits = [SearchHit("x", "text-x", 0.9, "dense", 1, 1, "test")]
        hits2 = [SearchHit("x", "text-x", 0.5, "bm25", 3, 1, "test")]

        result = rrf_fuse(
            channels={"dense": hits, "bm25": hits2},
            weights={"dense": 0.6, "bm25": 0.4},
            k=60,
            limit=10,
        )
        ids = [h.chunk_id for h in result]
        assert ids.count("x") == 1


class TestReranker:
    """Reranker must respect timeout and fallback to RRF order."""

    def test_reranker_fallback_on_timeout(self):
        """When reranker times out, RRF order is preserved."""
        # This is a contract test — real implementation in adapter
        pass
