"""Unit tests for GraphRAG — ontology, extraction, path ranking."""


from policymind.graph.ontology import ALLOWED_ENTITIES, ALLOWED_RELATIONS
from policymind.graph.path_ranker import rank_paths


class TestOntology:
    """Ontology must define allowed entities and relations."""

    def test_required_entities_exist(self):
        required = {"Policy", "Clause", "Department", "Role", "Process", "ApprovalStep"}
        assert required <= ALLOWED_ENTITIES

    def test_required_relations_exist(self):
        required = {
            "APPLIES_TO", "OWNED_BY", "REQUIRES", "APPROVED_BY",
            "NEXT_STEP", "REFERENCES", "SUPERSEDES", "CONFLICTS_WITH", "EXTRACTED_FROM",
        }
        assert required <= ALLOWED_RELATIONS


class TestPathRanker:
    """Path ranking prioritizes shorter paths with higher confidence."""

    def test_shorter_path_ranks_higher(self):
        short = {"nodes": ["A", "B"], "length": 1, "confidence": 0.8, "edges": ["APPLIES_TO"]}
        long = {"nodes": ["A", "B", "C", "D"], "length": 3, "confidence": 0.8, "edges": ["NEXT_STEP"] * 3}
        query = "谁审批采购？"
        ranked = rank_paths([long, short], query)
        assert ranked[0]["length"] == 1

    def test_higher_confidence_ranks_higher(self):
        low_conf = {"nodes": ["A", "B"], "length": 1, "confidence": 0.3, "edges": ["APPLIES_TO"]}
        high_conf = {"nodes": ["A", "B"], "length": 1, "confidence": 0.9, "edges": ["APPLIES_TO"]}
        query = "采购审批"
        ranked = rank_paths([low_conf, high_conf], query)
        assert ranked[0]["confidence"] == 0.9

    def test_query_match_boosts_ranking(self):
        matching = {"nodes": ["采购部", "经理"], "length": 1, "confidence": 0.7, "edges": ["OWNED_BY"]}
        non_matching = {"nodes": ["X", "Y"], "length": 1, "confidence": 0.7, "edges": ["REFERENCES"]}
        query = "采购部"
        ranked = rank_paths([non_matching, matching], query)
        assert "采购部" in str(ranked[0]["nodes"])


class TestGraphSearchResult:
    """Graph search must return source-bound results."""

    def test_result_contains_sources(self):
        """Every path must reference source documents."""
        from policymind.graph.search import GraphSearchResult

        result = GraphSearchResult(
            seed_entities=["Policy:1"],
            paths=[{
                "nodes": ["Policy:1", "Clause:2"],
                "edges": ["CONTAINS"],
                "source_document_version_id": 42,
                "confidence": 0.85,
                "length": 1,
            }],
            answer_context="Policy contains Clause",
            graph_score=0.85,
            graph_used=True,
            skip_reason=None,
        )
        assert result.graph_used is True
        assert result.graph_score > 0.8
