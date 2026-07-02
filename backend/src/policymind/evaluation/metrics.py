"""Evaluation metrics for retrieval, agent, and generation quality."""

from collections.abc import Sequence


def recall_at_k(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    """Recall@K — fraction of relevant items found in the top K results."""
    if not relevant:
        return 1.0
    top_k = set(retrieved[:k])
    return len(top_k & relevant) / len(relevant)


def reciprocal_rank(retrieved: Sequence[str], relevant: set[str]) -> float:
    """Mean Reciprocal Rank — 1 / rank of the first relevant item."""
    for i, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / i
    return 0.0


def ndcg_at_k(
    retrieved: Sequence[str],
    gains: dict[str, float],
    k: int,
) -> float:
    """Normalized Discounted Cumulative Gain at K."""
    import math

    dcg = 0.0
    for i, item in enumerate(retrieved[:k], start=1):
        g = gains.get(item, 0.0)
        dcg += g / math.log2(i + 1)

    ideal_gains = sorted(gains.values(), reverse=True)[:k]
    idcg = 0.0
    for i, g in enumerate(ideal_gains, start=1):
        idcg += g / math.log2(i + 1)

    if idcg == 0:
        return 0.0
    return dcg / idcg


def citation_precision(answer_ids: set[str], valid_ids: set[str]) -> float:
    """Precision of citations: what fraction of referenced IDs are valid."""
    if not answer_ids:
        return 0.0
    return len(answer_ids & valid_ids) / len(answer_ids)


def graph_path_accuracy(actual: Sequence[str], expected: Sequence[str]) -> float:
    """Accuracy of graph paths — how many expected edges appear."""
    if not expected:
        return 1.0
    actual_set = set(actual)
    expected_set = set(expected)
    return len(actual_set & expected_set) / len(expected_set)


def required_fact_coverage(answer: str, facts: Sequence[str]) -> float:
    """Fraction of required facts that appear in the answer."""
    if not facts:
        return 1.0
    answer_lower = answer.lower()
    covered = sum(1 for f in facts if f.lower() in answer_lower)
    return covered / len(facts)
