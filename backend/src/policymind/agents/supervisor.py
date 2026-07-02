"""Supervisor node — routes queries to the correct execution path."""

ROUTE_RETRIEVAL = "retrieval"
ROUTE_GRAPH = "graph"
ROUTE_PLANNER = "planner"
ROUTE_EXECUTOR = "executor"


def classify_query(query: str) -> tuple[str, str]:
    """Simple keyword-based routing fallback when LLM is unavailable.

    Returns (route, reason).
    """
    rel_keywords = ["谁", "哪个部门", "审批", "负责", "流程", "步骤", "关系", "区别"]
    complex_keywords = ["比较", "分析", "综合", "为什么", "怎么", "如何"]

    # Check relationship questions → GraphRAG
    if any(kw in query for kw in rel_keywords):
        return ROUTE_GRAPH, "relationship_query"

    # Check complex questions → Planner
    if any(kw in query for kw in complex_keywords):
        return ROUTE_PLANNER, "complex_query"

    # Default → Hybrid RAG
    return ROUTE_RETRIEVAL, "knowledge_query"
