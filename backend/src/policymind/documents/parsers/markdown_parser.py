"""Markdown parser for .md files."""

import re

from policymind.documents.models import DocumentBlock, ParsedDocument


class MarkdownParser:
    """Parse Markdown into blocks preserving heading hierarchy."""

    supported_mime_types = frozenset({"text/markdown", "text/plain"})

    def parse(self, content: bytes, filename: str = "") -> ParsedDocument:
        text = content.decode("utf-8", errors="replace")
        blocks: list[DocumentBlock] = []
        heading_stack: list[str] = []

        # Split on empty lines for block detection
        sections = re.split(r"\n\s*\n", text)

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # Detect headings
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", section, re.MULTILINE)
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                heading_stack = heading_stack[: level - 1]
                heading_stack.append(title)
                blocks.append(
                    DocumentBlock(
                        text=title,
                        page_number=1,
                        block_type="title",
                        heading_path=tuple(heading_stack),
                    )
                )
                # The rest of the section (if any) is body text
                remaining = section[heading_match.end() :].strip()
                if remaining:
                    blocks.append(
                        DocumentBlock(
                            text=remaining,
                            page_number=1,
                            block_type="text",
                            heading_path=tuple(heading_stack),
                        )
                    )
            else:
                # Detect code blocks
                if section.startswith("```"):
                    # Code block — keep as-is
                    blocks.append(
                        DocumentBlock(
                            text=section,
                            page_number=1,
                            block_type="text",
                            heading_path=tuple(heading_stack),
                        )
                    )
                elif section.startswith("|"):
                    # Table
                    blocks.append(
                        DocumentBlock(
                            text=section,
                            page_number=1,
                            block_type="table",
                            heading_path=tuple(heading_stack),
                        )
                    )
                else:
                    blocks.append(
                        DocumentBlock(
                            text=section,
                            page_number=1,
                            block_type="text",
                            heading_path=tuple(heading_stack),
                        )
                    )

        # Use first heading as title
        title = filename
        for b in blocks:
            if b.block_type == "title":
                title = b.text
                break

        return ParsedDocument(
            title=title or "Untitled",
            page_count=1,
            blocks=blocks,
            metadata={"parser": "markdown"},
        )
