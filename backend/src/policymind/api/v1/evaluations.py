"""Evaluation run and report routes."""

from typing import Any

from fastapi import APIRouter, Depends

from policymind.api.dependencies import RequestContext, get_current_context, require_roles

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


@router.post("/runs")
async def create_evaluation_run(
    payload: dict[str, Any],
    ctx: RequestContext = Depends(require_roles("policy_admin", "system_admin")),
) -> dict[str, Any]:
    import uuid

    return {"run_id": uuid.uuid4().hex, "status": "queued", "tenant_id": ctx.tenant_id}


@router.get("/runs/{run_id}")
async def get_evaluation_run(
    run_id: str,
    ctx: RequestContext = Depends(get_current_context),
) -> dict[str, Any]:
    return {"run_id": run_id, "status": "completed", "metrics": {}}


@router.get("/runs/{run_id}/report")
async def get_evaluation_report(
    run_id: str,
    ctx: RequestContext = Depends(get_current_context),
) -> dict[str, Any]:
    return {"run_id": run_id, "report": "Evaluation report"}


@router.get("/compare")
async def compare_runs(
    run_ids: str = "",
    ctx: RequestContext = Depends(get_current_context),
) -> dict[str, Any]:
    return {"comparison": []}
