"""Human review (HITL) routes."""

from typing import Any

from fastapi import APIRouter, Depends

from policymind.api.dependencies import RequestContext, get_current_context, require_roles

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


@router.get("/")
async def list_reviews(
    ctx: RequestContext = Depends(get_current_context),
) -> list[dict[str, Any]]:
    return []


@router.get("/{review_id}")
async def get_review(
    review_id: int,
    ctx: RequestContext = Depends(get_current_context),
) -> dict[str, Any]:
    return {"id": review_id, "tenant_id": ctx.tenant_id, "status": "pending"}


@router.post("/{review_id}/approve")
async def approve_review(
    review_id: int,
    ctx: RequestContext = Depends(require_roles("policy_admin", "system_admin")),
) -> dict[str, Any]:
    return {"id": review_id, "status": "approved", "reviewer_id": ctx.user_id}


@router.post("/{review_id}/reject")
async def reject_review(
    review_id: int,
    reason: str = "",
    ctx: RequestContext = Depends(require_roles("policy_admin", "system_admin")),
) -> dict[str, Any]:
    return {"id": review_id, "status": "rejected", "reason": reason}
