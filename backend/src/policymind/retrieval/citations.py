"""Citation building and validation."""

import re

from policymind.retrieval.ports import Citation, CitationValidation, SearchHit


def build_citations(hits: list[SearchHit]) -> list[Citation]:
    """Build a Citation for each SearchHit with C1, C2, ... IDs."""
    citations: list[Citation] = []
    for i, hit in enumerate(hits):
        citations.append(
            Citation(
                id=f"C{i + 1}",
                document_name=hit.document_name,
                document_version=hit.document_version,
                page_number=hit.page_number,
                quote=hit.text[:200] if hit.text else "",
                channel=hit.channel,
                score=hit.score,
            )
        )
    return citations


def validate_answer_citations(
    answer: str,
    citations: list[Citation],
) -> CitationValidation:
    """Check that every [Cxx] in the answer maps to a real citation."""
    referenced = set(re.findall(r"\[C(\d+)\]", answer))
    valid_ids = {c.id.lstrip("C") for c in citations}
    citation_ids = {c.id for c in citations}

    unknown = {f"C{rid}" for rid in referenced - valid_ids}
    present = {f"C{rid}" for rid in referenced & valid_ids}
    unused = citation_ids - present

    return CitationValidation(
        is_valid=len(unknown) == 0,
        unknown_ids=sorted(unknown),
        unused_ids=sorted(unused),
        present_ids=sorted(present),
    )
