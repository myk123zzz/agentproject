"""Unit tests for hierarchical chunking."""

from datetime import UTC, datetime

import pytest

from policymind.documents.chunking import HierarchicalChunker
from policymind.documents.models import ChunkContext, DocumentBlock, ParsedDocument


@pytest.fixture
def simple_doc() -> ParsedDocument:
    """A parsed document with two sections."""
    return ParsedDocument(
        title="Test Policy",
        page_count=2,
        blocks=[
            DocumentBlock(
                text="Section 1 Title",
                page_number=1,
                block_type="title",
                heading_path=("1",),
            ),
            DocumentBlock(
                text="This is the content of section one. " * 40,  # ~1200 chars
                page_number=1,
                block_type="text",
                heading_path=("1",),
            ),
            DocumentBlock(
                text="Section 2 Title",
                page_number=2,
                block_type="title",
                heading_path=("2",),
            ),
            DocumentBlock(
                text="Section two content. " * 20,
                page_number=2,
                block_type="text",
                heading_path=("2",),
            ),
        ],
        metadata={"author": "test"},
    )


@pytest.fixture
def chunk_context() -> ChunkContext:
    return ChunkContext(
        tenant_id=1,
        document_id=1,
        document_version_id=1,
        access_level=0,
        effective_from=datetime(2024, 1, 1, tzinfo=UTC),
        effective_to=None,
    )


class TestHierarchicalChunker:
    """Chunking must produce parent and leaf chunks with provenance."""

    def test_produces_both_levels(self, simple_doc, chunk_context):
        """Must produce at least one parent and one leaf chunk."""
        chunker = HierarchicalChunker()
        chunks = chunker.chunk(simple_doc, chunk_context)
        levels = {c.level for c in chunks}
        assert "parent" in levels
        assert "leaf" in levels

    def test_leaf_chunks_have_provenance(self, simple_doc, chunk_context):
        """Every leaf must reference parent_id, page_number, and source."""
        chunker = HierarchicalChunker()
        chunks = chunker.chunk(simple_doc, chunk_context)
        leaves = [c for c in chunks if c.level == "leaf"]
        assert len(leaves) > 0
        for c in leaves:
            assert c.parent_id is not None, f"Leaf {c.id} missing parent_id"
            assert c.page_number > 0, f"Leaf {c.id} missing page_number"
            assert c.document_version_id == chunk_context.document_version_id

    def test_chunk_ids_are_stable(self, simple_doc, chunk_context):
        """Same input must produce identical chunk IDs (deterministic)."""
        chunker = HierarchicalChunker()
        first = {c.id for c in chunker.chunk(simple_doc, chunk_context)}
        second = {c.id for c in chunker.chunk(simple_doc, chunk_context)}
        assert first == second

    def test_table_blocks_not_split(self, chunk_context):
        """Table header and data must stay in the same chunk."""
        doc = ParsedDocument(
            title="Table Test",
            page_count=1,
            blocks=[
                DocumentBlock(
                    text="Header1 | Header2 | Header3\nData1 | Data2 | Data3",
                    page_number=1,
                    block_type="table",
                ),
            ],
            metadata={},
        )
        chunker = HierarchicalChunker()
        chunks = chunker.chunk(doc, chunk_context)
        leaf = [c for c in chunks if c.level == "leaf"]
        # The table block should be kept together
        assert any("Header1" in c.text for c in leaf)
