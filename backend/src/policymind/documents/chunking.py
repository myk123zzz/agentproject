"""Hierarchical chunker — parent chunks (1000–1600 chars) and leaf chunks (300–500 chars)."""

import hashlib

from policymind.documents.models import Chunk, ChunkContext, ParsedDocument

PARENT_MIN = 800
PARENT_MAX = 1600
LEAF_MIN = 200
LEAF_MAX = 500
LEAF_OVERLAP = 80


def _make_chunk_id(
    version_id: int,
    page: int,
    bbox: tuple[float, float, float, float] | None,
    text: str,
) -> str:
    """Deterministic chunk ID from content hash."""
    bbox_str = ",".join(f"{v:.2f}" for v in bbox) if bbox else "none"
    seed = f"{version_id}:{page}:{bbox_str}:{text}"
    return hashlib.sha256(seed.encode()).hexdigest()[:32]


def _split_text(text: str, max_len: int, overlap: int) -> list[str]:
    """Split long text into chunks with overlap, preferring sentence boundaries."""
    if len(text) <= max_len:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_len, len(text))
        # Try to break at a sentence boundary
        if end < len(text):
            for sep in ["。\n", "。", "\n\n", "\n", ". ", " "]:
                pos = text.rfind(sep, start + max_len // 2, end)
                if pos != -1:
                    end = pos + len(sep)
                    break

        chunks.append(text[start:end].strip())
        start = end - overlap if end < len(text) else end

    return [c for c in chunks if c]


class HierarchicalChunker:
    """Produce parent and leaf chunks with full provenance."""

    def chunk(self, document: ParsedDocument, ctx: ChunkContext) -> list[Chunk]:
        chunks: list[Chunk] = []

        for block in document.blocks:
            # Parent chunk keeps the full block
            parent_id = _make_chunk_id(
                ctx.document_version_id, block.page_number, block.bbox, block.text
            )
            parent = Chunk(
                id=parent_id,
                tenant_id=ctx.tenant_id,
                document_id=ctx.document_id,
                document_version_id=ctx.document_version_id,
                parent_id=None,
                level="parent",
                text=block.text,
                page_number=block.page_number,
                heading_path=block.heading_path,
                bbox=block.bbox,
                access_level=ctx.access_level,
                effective_from=ctx.effective_from,
                effective_to=ctx.effective_to,
                block_type=block.block_type,
            )
            chunks.append(parent)

            # Table blocks: do NOT split — keep as one leaf
            if block.block_type == "table":
                leaf = Chunk(
                    id=_make_chunk_id(ctx.document_version_id, block.page_number, block.bbox, block.text + "_leaf"),
                    tenant_id=ctx.tenant_id,
                    document_id=ctx.document_id,
                    document_version_id=ctx.document_version_id,
                    parent_id=parent_id,
                    level="leaf",
                    text=block.text,
                    page_number=block.page_number,
                    heading_path=block.heading_path,
                    bbox=block.bbox,
                    access_level=ctx.access_level,
                    effective_from=ctx.effective_from,
                    effective_to=ctx.effective_to,
                    block_type=block.block_type,
                )
                chunks.append(leaf)
                continue

            # Other blocks: split into leaf chunks
            leaves_text = _split_text(block.text, LEAF_MAX, LEAF_OVERLAP)
            for leaf_text in leaves_text:
                leaf = Chunk(
                    id=_make_chunk_id(ctx.document_version_id, block.page_number, block.bbox, leaf_text),
                    tenant_id=ctx.tenant_id,
                    document_id=ctx.document_id,
                    document_version_id=ctx.document_version_id,
                    parent_id=parent_id,
                    level="leaf",
                    text=leaf_text,
                    page_number=block.page_number,
                    heading_path=block.heading_path,
                    bbox=block.bbox,
                    access_level=ctx.access_level,
                    effective_from=ctx.effective_from,
                    effective_to=ctx.effective_to,
                    block_type=block.block_type,
                )
                chunks.append(leaf)

        return chunks
