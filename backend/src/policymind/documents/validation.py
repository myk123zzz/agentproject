"""File upload validation — extension, MIME, magic bytes, size."""

import uuid
from dataclasses import dataclass

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".xls",
    ".md",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
    ".bmp",
}

# Simple magic-byte signatures for common office / image formats
MAGIC_SIGNATURES: dict[str, bytes] = {
    ".pdf": b"%PDF",
    ".docx": b"PK\x03\x04",
    ".xlsx": b"PK\x03\x04",
    ".png": b"\x89PNG",
    ".jpg": b"\xff\xd8\xff",
}

MIME_TO_EXT: dict[str, set[str]] = {
    "application/pdf": {".pdf"},
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {".docx"},
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {".xlsx"},
    "text/markdown": {".md"},
    "text/plain": {".txt", ".md"},
    "image/png": {".png"},
    "image/jpeg": {".jpg", ".jpeg"},
}


@dataclass(frozen=True, slots=True)
class ValidatedUpload:
    """A file that has passed all validation checks."""

    filename: str
    mime_type: str
    content: bytes
    size: int


def validate_upload(
    filename: str,
    declared_mime: str,
    content: bytes,
    max_bytes: int,
) -> ValidatedUpload:
    """Validate extension, MIME, magic bytes, size, and empty files."""
    if len(content) == 0:
        raise ValueError("File is empty")

    if len(content) > max_bytes:
        raise ValueError(f"File size ({len(content)}) exceeds limit ({max_bytes})")

    # Extension check
    ext = _extract_extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Disallowed file extension: {ext}")

    # MIME vs extension
    expected = MIME_TO_EXT.get(declared_mime)
    if expected is None or ext not in expected:
        raise ValueError(
            f"Declared MIME '{declared_mime}' does not match extension '{ext}'"
        )

    # Magic-byte check (non-blocking warning for unknown types)
    signature = MAGIC_SIGNATURES.get(ext)
    if signature and not content.startswith(signature):
        raise ValueError(f"File content does not match expected signature for {ext}")

    return ValidatedUpload(
        filename=filename,
        mime_type=declared_mime,
        content=content,
        size=len(content),
    )


def safe_storage_key(tenant_id: int, suffix: str) -> str:
    """Generate a random, tenant-scoped storage key.  Never embeds the original filename."""
    return f"{tenant_id}/{uuid.uuid4().hex}{suffix}"


def _extract_extension(filename: str) -> str:
    name = filename.rsplit(".", 1)
    if len(name) == 1:
        return ""
    return "." + name[-1].lower()
