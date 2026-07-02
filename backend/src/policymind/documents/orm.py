"""SQLAlchemy ORM models for documents, versions, chunks, and ingestion jobs."""

import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from policymind.infrastructure.postgres.base import Base


class DocumentStatus(str, enum.Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DELETED = "deleted"


class ProcessingStatus(str, enum.Enum):
    QUEUED = "queued"
    STORED = "stored"
    PARSED = "parsed"
    CHUNKED = "chunked"
    EMBEDDED = "embedded"
    VECTOR_INDEXED = "vector_indexed"
    GRAPH_INDEXED = "graph_indexed"
    READY = "ready"
    FAILED = "failed"


class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id"), nullable=False)
    logical_name: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner_department_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    access_level: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status"), default=DocumentStatus.ACTIVE
    )
    current_version_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DocumentVersionRecord(Base):
    __tablename__ = "document_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, name="processing_status"),
        default=ProcessingStatus.QUEUED,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ChunkRecord(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id"), nullable=False)
    document_version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("document_versions.id"), nullable=False
    )
    chunk_ext_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    parent_chunk_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, default=1)
    block_type: Mapped[str] = mapped_column(String(32), default="text")
    heading_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    text_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    milvus_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    bbox_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class IngestionJobRecord(Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id"), nullable=False)
    document_version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("document_versions.id"), nullable=False
    )
    job_id: Mapped[str] = mapped_column(String(64), nullable=False)
    stage: Mapped[str] = mapped_column(String(64), nullable=False)
    progress: Mapped[float] = mapped_column(default=0.0)
    status: Mapped[str] = mapped_column(String(32), default="queued")
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
