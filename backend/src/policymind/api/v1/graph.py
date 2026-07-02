"""Graph visualization and entity management routes."""

from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


@router.get("/subgraph")
async def get_subgraph(
    tenant_id: int = 1,
    entity_type: str = "",
    limit: int = 50,
) -> dict[str, Any]:
    return {"nodes": [], "edges": []}


@router.get("/entities/{entity_id}")
async def get_entity(entity_id: str) -> dict[str, Any]:
    return {"id": entity_id, "type": "Policy", "name": "Unknown"}


@router.post("/entities/{entity_id}/merge")
async def merge_entity(entity_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"id": entity_id, "merged": True}
