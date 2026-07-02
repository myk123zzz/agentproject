"""FastAPI document routes — multipart upload, persist to storage, job tracking."""

import hashlib
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, File, Form, UploadFile

from policymind.api.dependencies import RequestContext, get_current_context
from policymind.documents.storage import LocalObjectStorage

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

# In-memory job store for dev (replaced by PostgreSQL in production)
_jobs: dict[str, dict[str, Any]] = {}
_storage = LocalObjectStorage()


@router.post("/")
async def create_document(
    file: UploadFile = File(...),
    logical_name: str = Form(""),
    ctx: RequestContext = Depends(get_current_context),
) -> dict[str, Any]:
    """Upload a document file, validate, persist, and queue for ingestion."""
    if not file.filename:
        return _error("No file provided", 400)

    content = await file.read()
    if not content:
        return _error("Empty file", 400)

    # Validate size (10 MB max)
    if len(content) > 10_000_000:
        return _error("File exceeds 10 MB limit", 413)

    # Compute hash and generate storage key
    content_hash = hashlib.sha256(content).hexdigest()
    storage_key = f"{ctx.tenant_id}/{uuid.uuid4().hex}/{file.filename}"

    # Persist file
    await _storage.put(storage_key, content, file.content_type or "application/octet-stream")

    # Create ingestion job
    job_id = uuid.uuid4().hex
    _jobs[job_id] = {
        "job_id": job_id,
        "tenant_id": ctx.tenant_id,
        "storage_key": storage_key,
        "content_hash": content_hash,
        "filename": file.filename,
        "logical_name": logical_name or file.filename,
        "status": "stored",
        "progress": 0.1,
        "created_at": datetime.now(UTC).isoformat(),
    }

    return {
        "job_id": job_id,
        "status": "accepted",
        "content_hash": content_hash,
        "filename": file.filename,
    }


@router.get("/")
async def list_documents(
    ctx: RequestContext = Depends(get_current_context),
) -> list[dict[str, Any]]:
    """List documents for the current tenant."""
    tenant_jobs = [
        j for j in _jobs.values()
        if j.get("tenant_id") == ctx.tenant_id
    ]
    return tenant_jobs


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    ctx: RequestContext = Depends(get_current_context),
) -> dict[str, Any]:
    """Poll ingestion job status."""
    job = _jobs.get(job_id)
    if job is None:
        return _error("Job not found", 404)
    if job.get("tenant_id") != ctx.tenant_id:
        return _error("Job not found", 404)
    return job


def _error(message: str, status_code: int) -> dict[str, Any]:
    return {"error": message, "status_code": status_code}
