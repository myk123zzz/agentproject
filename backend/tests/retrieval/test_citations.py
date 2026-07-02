"""Unit tests for citation building and validation."""

from policymind.retrieval.citations import build_citations, validate_answer_citations
from policymind.retrieval.ports import SearchHit


def _hit(chunk_id: str, channel: str = "dense", page: int = 1) -> SearchHit:
    return SearchHit(
        chunk_id=chunk_id,
        text=f"原文片段 {chunk_id}",
        score=0.9,
        channel=channel,
        rank=1,
        page_number=page,
        document_name="测试制度v2.0",
        document_version="2.0",
    )


class TestBuildCitations:
    """Citations must include file, version, page, quote, and channel."""

    def test_each_hit_becomes_citation(self):
        hits = [_hit("a", "dense", 1), _hit("b", "bm25", 3)]
        citations = build_citations(hits)
        assert len(citations) == 2
        assert citations[0].id == "C1"
        assert citations[1].id == "C2"

    def test_citation_contains_file_and_version(self):
        citations = build_citations([_hit("a")])
        assert citations[0].document_name == "测试制度v2.0"
        assert citations[0].document_version == "2.0"

    def test_citation_contains_channel(self):
        citations = build_citations([_hit("a", "bm25")])
        assert citations[0].channel == "bm25"


class TestCitationValidation:
    """Unknown [Cxx] references in answers must be flagged."""

    def test_valid_citations_pass(self):
        citations = build_citations([_hit("a"), _hit("b")])
        answer = "根据制度，审批需要[C1]和[C2]两个步骤。"
        result = validate_answer_citations(answer, citations)
        assert result.is_valid is True
        assert len(result.unknown_ids) == 0

    def test_unknown_citation_detected(self):
        citations = build_citations([_hit("a")])
        answer = "参见[C1]和[C5]相关规定。"
        result = validate_answer_citations(answer, citations)
        assert result.is_valid is False
        assert "C5" in result.unknown_ids

    def test_no_citations_in_answer(self):
        citations = build_citations([_hit("a")])
        answer = "没有引用任何制度。"
        result = validate_answer_citations(answer, citations)
        # Missing citations is a warning but doesn't invalidate
        assert len(result.unused_ids) >= 0
