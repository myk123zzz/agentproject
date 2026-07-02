"""Graph path ranking — scores paths by query match, confidence, version, and length."""

from typing import Any


def rank_paths(
    paths: list[dict[str, Any]],
    query: str,
    *,
    length_penalty: float = 0.2,
    confidence_weight: float = 0.4,
    query_match_weight: float = 0.4,
) -> list[dict[str, Any]]:
    """Rank graph paths by a composite score.

    Score = confidence_weight * confidence
          + query_match_weight * query_match
          - length_penalty * length
    """
    scored: list[tuple[float, dict[str, Any]]] = []
    query_lower = query.lower()
    query_terms = set(query_lower.split())

    for path in paths:
        score = 0.0
        confidence = float(path.get("confidence", 0.5))
        length = int(path.get("length", 1))
        nodes = str(path.get("nodes", [])).lower()

        # Query match
        query_match = sum(1.0 for t in query_terms if t in nodes) / max(len(query_terms), 1)
        query_match = min(query_match, 1.0)

        score = (
            confidence_weight * confidence
            + query_match_weight * query_match
            - length_penalty * length
        )
        scored.append((score, path))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored]
