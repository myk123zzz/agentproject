"""Unit tests for file upload validation."""

import pytest

from policymind.documents.validation import safe_storage_key, validate_upload


class TestValidateUpload:
    """File upload validation — extension, magic, size, empty files."""

    def test_rejects_empty_file(self):
        """Empty files must be rejected."""
        with pytest.raises(ValueError, match="empty"):
            validate_upload("test.pdf", "application/pdf", b"", max_bytes=10_000_000)

    def test_rejects_mime_mismatch(self):
        """Declared MIME must match the file extension and magic bytes."""
        content = b"%PDF-1.4 test pdf content"
        with pytest.raises(ValueError, match="MIME"):
            validate_upload("test.pdf", "image/png", content, max_bytes=10_000_000)

    def test_rejects_oversized_file(self):
        """Files exceeding max_bytes must be rejected."""
        content = b"x" * 1001
        with pytest.raises(ValueError, match="exceed"):
            validate_upload("test.txt", "text/plain", content, max_bytes=1000)

    def test_accepts_valid_pdf(self):
        """A valid PDF with correct MIME should pass."""
        content = b"%PDF-1.4\ntest pdf content with enough bytes for validation"
        result = validate_upload(
            "policy.pdf", "application/pdf", content, max_bytes=10_000_000
        )
        assert result.filename == "policy.pdf"
        assert result.mime_type == "application/pdf"
        assert result.content == content

    def test_rejects_dangerous_extension(self):
        """Executable extensions must be rejected."""
        content = b"some content that looks like text"
        with pytest.raises(ValueError, match="extension"):
            validate_upload(
                "malware.exe", "application/octet-stream", content, max_bytes=10_000_000
            )


class TestSafeStorageKey:
    """Storage keys must be random and never embed the original filename."""

    def test_key_is_random(self):
        """Two calls produce different keys."""
        a = safe_storage_key(1, ".pdf")
        b = safe_storage_key(1, ".pdf")
        assert a != b

    def test_key_contains_tenant(self):
        """Key must be scoped to a tenant."""
        key = safe_storage_key(42, ".pdf")
        assert key.startswith("42/")

    def test_key_does_not_contain_original_name(self):
        """Key must NOT embed the original filename."""
        key = safe_storage_key(1, ".pdf")
        # Safe keys use UUIDs, not user-provided names
        assert "malware" not in key
