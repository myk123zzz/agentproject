"""Domain models for documents, versions, chunks."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class DocumentBlock(BaseModel):
    """A single parsed block within a document."""

    text: str
    page_number: int
    block_type: Literal["title", "text", "table", "image", "flowchart"]
    heading_path: tuple[str, ...] = ()
    bbox: tuple[float, float, float, float] | None = None
    media_key: str | None = None


class ParsedDocument(BaseModel):
    """The structured output of a document parser."""

    title: str = ""
    page_count: int = 1
    blocks: list[DocumentBlock]
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChunkContext(BaseModel):
    """Context passed through to every chunk for provenance."""

    tenant_id: int
    document_id: int
    document_version_id: int
    access_level: int
    effective_from: datetime
    effective_to: datetime | None = None


class Chunk(BaseModel):
    """A chunk of document content — parent or leaf."""

    id: str
    tenant_id: int
    document_id: int
    document_version_id: int
    parent_id: str | None = None
    level: Literal["parent", "leaf"]
    text: str
    page_number: int
    heading_path: tuple[str, ...] = ()
    bbox: tuple[float, float, float, float] | None = None
    access_level: int = 0
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    block_type: str = "text"
