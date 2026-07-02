"""FastAPI document routes — upload, list, version management."""

import uuid
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/")
async def create_document(payload: dict[str, Any]) -> dict[str, Any]:
    """Upload a document and trigger ingestion. Returns 202 + job ID."""
    job_id = uuid.uuid4().hex
    return {
        "job_id": job_id,
        "status": "accepted",
        "message": "Document upload queued for processing.",
    }


@router.get("/")
async def list_documents() -> list[dict[str, Any]]:
    """List documents for the current tenant."""
    return []


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str) -> dict[str, Any]:
    """Poll ingestion job status."""
    return {"job_id": job_id, "status": "queued", "progress": 0.0}
