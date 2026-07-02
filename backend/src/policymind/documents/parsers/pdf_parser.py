"""PDF parser using PyMuPDF (fitz)."""

import fitz  # type: ignore[import-untyped]  # PyMuPDF

from policymind.documents.models import DocumentBlock, ParsedDocument


class PDFParser:
    """Extract text, pages, and bounding boxes from PDF files."""

    supported_mime_types = frozenset({"application/pdf"})

    def parse(self, content: bytes, filename: str = "") -> ParsedDocument:
        doc = fitz.open(stream=content, filetype="pdf")
        blocks: list[DocumentBlock] = []
        page_count = doc.page_count

        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if text.strip():
                # Split by paragraph breaks for block-level extraction
                for paragraph in text.split("\n\n"):
                    para = paragraph.strip()
                    if not para:
                        continue
                    # Determine block type
                    lines = para.split("\n")
                    block_type = "title" if len(lines) == 1 and len(para) < 120 else "text"
                    blocks.append(
                        DocumentBlock(
                            text=para,
                            page_number=page_num,
                            block_type=block_type,  # type: ignore[arg-type]
                            bbox=(0, 0, page.rect.width, page.rect.height),
                        )
                    )

        title = doc.metadata.get("title", filename) if doc.metadata else filename
        return ParsedDocument(
            title=title or "Untitled",
            page_count=page_count,
            blocks=blocks,
            metadata=dict(doc.metadata) if doc.metadata else {},
        )
