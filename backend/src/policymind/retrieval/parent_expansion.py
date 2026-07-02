"""Parent chunk expansion — enriches leaf hits with surrounding parent context."""

from policymind.retrieval.ports import SearchHit


def expand_to_parents(
    leaf_hits: list[SearchHit],
    parent_map: dict[str, str],  # leaf_chunk_id -> parent_text
) -> list[SearchHit]:
    """Append parent text to each leaf hit where the parent is available."""
    result: list[SearchHit] = []
    for hit in leaf_hits:
        parent_text = parent_map.get(hit.chunk_id)
        if parent_text and parent_text not in hit.text:
            hit.text = hit.text + "\n\n" + parent_text
        result.append(hit)
    return result
