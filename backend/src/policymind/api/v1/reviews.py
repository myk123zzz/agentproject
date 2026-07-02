"""Human review (HITL) routes."""

from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


@router.get("/")
async def list_reviews() -> list[dict[str, Any]]:
    return []


@router.get("/{review_id}")
async def get_review(review_id: int) -> dict[str, Any]:
    return {"id": review_id, "status": "pending"}


@router.post("/{review_id}/approve")
async def approve_review(review_id: int) -> dict[str, Any]:
    return {"id": review_id, "status": "approved"}


@router.post("/{review_id}/reject")
async def reject_review(review_id: int, reason: str = "") -> dict[str, Any]:
    return {"id": review_id, "status": "rejected", "reason": reason}
