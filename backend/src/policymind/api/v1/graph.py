"""Graph visualization and entity management routes."""

from typing import Any

from fastapi import APIRouter, Depends

from policymind.api.dependencies import RequestContext, get_current_context

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


@router.get("/subgraph")
async def get_subgraph(
    entity_type: str = "",
    limit: int = 50,
    ctx: RequestContext = Depends(get_current_context),
) -> dict[str, Any]:
    return {"nodes": [], "edges": [], "tenant_id": ctx.tenant_id}


@router.get("/entities/{entity_id}")
async def get_entity(
    entity_id: str,
    ctx: RequestContext = Depends(get_current_context),
) -> dict[str, Any]:
    return {"id": entity_id, "type": "Policy", "name": "Unknown"}


@router.post("/entities/{entity_id}/merge")
async def merge_entity(
    entity_id: str,
    payload: dict[str, Any],
    ctx: RequestContext = Depends(get_current_context),
) -> dict[str, Any]:
    return {"id": entity_id, "merged": True}
