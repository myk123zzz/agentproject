"""GraphRepository protocol and in-memory implementation."""

from typing import Any, Protocol

from policymind.graph.extraction import GraphExtraction


class GraphRepository(Protocol):
    """Protocol for graph database operations."""

    async def upsert(self, extraction: GraphExtraction) -> None: ...

    async def search_paths(
        self,
        *,
        tenant_id: int,
        seed_entity_ids: list[str],
        max_hops: int,
        limit: int,
    ) -> list[dict[str, Any]]: ...


class MemoryGraphRepository:
    """In-memory graph repository for unit tests."""

    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: list[dict[str, Any]] = []

    async def upsert(self, extraction: GraphExtraction) -> None:
        for entity in extraction.entities:
            key = f"{entity.type}:{entity.name}"
            self._nodes[key] = {
                "name": entity.name,
                "type": entity.type,
                "tenant_id": entity.tenant_id,
                "confidence": entity.confidence,
                "source_document_version_id": entity.source_document_version_id,
            }
        for rel in extraction.relations:
            self._edges.append({
                "source": rel.source,
                "target": rel.target,
                "type": rel.type,
                "tenant_id": rel.tenant_id,
                "confidence": rel.confidence,
                "source_document_version_id": rel.source_document_version_id,
            })

    async def search_paths(
        self,
        *,
        tenant_id: int,
        seed_entity_ids: list[str],
        max_hops: int = 3,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        paths: list[dict[str, Any]] = []
        for seed in seed_entity_ids:
            for edge in self._edges:
                if edge["tenant_id"] != tenant_id:
                    continue
                if edge["source"] in seed or edge["target"] in seed:
                    paths.append({
                        "nodes": [edge["source"], edge["target"]],
                        "edges": [edge["type"]],
                        "source_document_version_id": edge["source_document_version_id"],
                        "confidence": edge["confidence"],
                        "length": 1,
                    })
        return paths[:limit]
