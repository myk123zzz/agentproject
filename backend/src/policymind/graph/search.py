"""GraphSearchService — performs local graph search and returns context."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraphSearchResult:
    seed_entities: list[str] = field(default_factory=list)
    paths: list[dict[str, Any]] = field(default_factory=list)
    answer_context: str = ""
    graph_score: float = 0.0
    graph_used: bool = False
    skip_reason: str | None = None


class GraphSearchService:
    """Local graph search: chunks → seed entities → paths → ranked context."""

    def __init__(self, repository: Any):
        self._repository = repository

    async def search(
        self,
        *,
        tenant_id: int,
        query: str,
        seed_entity_ids: list[str],
        max_hops: int = 3,
    ) -> GraphSearchResult:
        if not seed_entity_ids:
            return GraphSearchResult(
                graph_used=False,
                skip_reason="no_seed_entities",
            )

        paths = await self._repository.search_paths(
            tenant_id=tenant_id,
            seed_entity_ids=seed_entity_ids,
            max_hops=max_hops,
            limit=10,
        )

        if not paths:
            return GraphSearchResult(
                seed_entities=seed_entity_ids,
                graph_used=False,
                skip_reason="no_paths_found",
            )

        from policymind.graph.path_ranker import rank_paths

        ranked = rank_paths(paths, query)
        avg_conf = sum(float(p.get("confidence", 0)) for p in ranked) / max(len(ranked), 1)

        # Build context
        parts: list[str] = []
        for i, path in enumerate(ranked[:5]):
            nodes = " → ".join(str(n) for n in path.get("nodes", []))
            edges = ", ".join(str(e) for e in path.get("edges", []))
            parts.append(f"路径{i + 1}: {nodes} (关系: {edges})")

        return GraphSearchResult(
            seed_entities=seed_entity_ids,
            paths=ranked,
            answer_context="\n".join(parts),
            graph_score=round(avg_conf, 3),
            graph_used=True,
        )
