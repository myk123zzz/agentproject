"""Document parser protocol and registry."""

from typing import Protocol

from policymind.documents.models import ParsedDocument
from policymind.documents.validation import ValidatedUpload


class DocumentParser(Protocol):
    """Protocol for document format parsers."""

    supported_mime_types: frozenset[str]

    def parse(self, content: bytes, filename: str) -> ParsedDocument: ...


class ParserRegistry:
    """Registry that selects the right parser by MIME type."""

    def __init__(self) -> None:
        self._parsers: dict[str, DocumentParser] = {}

    def register(self, parser: DocumentParser) -> None:
        for mime in parser.supported_mime_types:
            self._parsers[mime] = parser

    def resolve(self, mime_type: str) -> DocumentParser:
        parser = self._parsers.get(mime_type)
        if parser is None:
            raise ValueError(f"No parser registered for MIME type: {mime_type}")
        return parser

    def parse(self, upload: ValidatedUpload) -> ParsedDocument:
        parser = self.resolve(upload.mime_type)
        return parser.parse(upload.content, upload.filename)
