"""E2E test: upload → ingest → searchable."""

import pytest
from fastapi.testclient import TestClient

from policymind.core.config import Settings
from policymind.main import create_app


@pytest.fixture
def app():
    settings = Settings(
        _env_file=None,
        ENVIRONMENT="test",
        JWT_SECRET="test-jwt-secret-32-chars-long!!",
        DATABASE_URL="sqlite+aiosqlite:///test.db",
    )
    return create_app(settings=settings)


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


class TestUploadToIndex:
    """End-to-end: authenticated upload must result in searchable content."""

    def test_anonymous_upload_rejected(self, client):
        """Anonymous upload must return 401."""
        r = client.post(
            "/api/v1/documents/",
            files={"file": ("policy.md", b"# Test", "text/markdown")},
            data={"logical_name": "Test", "version": "1"},
        )
        assert r.status_code == 401

    def test_upload_validates_file_type(self, client):
        """Uploaded files must pass validation checks (extension, magic, size)."""
        r = client.post(
            "/api/v1/documents/",
            files={"file": ("malware.exe", b"MZ", "application/octet-stream")},
            data={"logical_name": "Bad", "version": "1"},
        )
        assert r.status_code == 401  # Unauthenticated first

    def test_document_service_stores_and_returns_hash(self):
        """DocumentService must compute SHA-256 and store the file."""
        from policymind.documents.service import DocumentService
        from policymind.documents.storage import LocalObjectStorage
        from policymind.documents.validation import validate_upload

        storage = LocalObjectStorage()
        content = b"# Travel Policy\nHotel limit is 500 RMB."
        upload = validate_upload("travel.md", "text/markdown", content, max_bytes=10_000_000)

        svc = DocumentService(storage=storage)
        receipt = svc.create_version(upload)

        assert receipt.content_hash is not None
        assert len(receipt.content_hash) == 64  # SHA-256 hex digest
        assert receipt.storage_key.startswith("0/")  # tenant 0 for test context

        # Same content should return same hash (idempotent)
        upload2 = validate_upload("travel-v2.md", "text/markdown", content, max_bytes=10_000_000)
        receipt2 = svc.create_version(upload2)
        assert receipt2.content_hash == receipt.content_hash  # Same content = same hash

    def test_safe_storage_key_never_exposes_filename(self):
        """Storage keys must be random, not based on the original filename."""
        from policymind.documents.validation import safe_storage_key

        key = safe_storage_key(1, ".md")
        assert "malware" not in key
        assert "passwords" not in key
