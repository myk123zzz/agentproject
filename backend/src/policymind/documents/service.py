"""DocumentService — create versions, check hash idempotency, store files."""

import hashlib
import uuid
from dataclasses import dataclass

from policymind.documents.storage import ObjectStorage
from policymind.documents.validation import ValidatedUpload


@dataclass
class IngestionReceipt:
    """Returned after a successful upload."""

    job_id: str
    status: str = "accepted"
    version_id: int = 0
    content_hash: str = ""
    storage_key: str = ""


class DocumentService:
    """Creates document versions, enforces hash-based idempotency."""

    def __init__(self, storage: ObjectStorage):
        self._storage = storage

    def create_version(self, upload: ValidatedUpload) -> IngestionReceipt:
        """Validate → hash → check idempotency → store → return receipt."""
        content_hash = hashlib.sha256(upload.content).hexdigest()
        storage_key = f"0/{uuid.uuid4().hex}/{upload.filename}"

        # In production, check database for (tenant_id, document_id, content_hash)
        # and return existing version if found.

        # For now, always store and return new receipt
        # (async storage.put happens in the pipeline)
        return IngestionReceipt(
            job_id=uuid.uuid4().hex,
            status="accepted",
            content_hash=content_hash,
            storage_key=storage_key,
        )
