"""LangGraph AgentState definition."""

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """Serializable agent state compatible with LangGraph checkpointer."""

    messages: list[Any]
    request_context: dict[str, Any]
    thread_id: str
    user_query: str
    normalized_query: str
    route: str
    route_reason: str
    plan: list[dict[str, Any]]
    current_step_id: str | None
    completed_step_ids: list[str]
    observations: list[dict[str, Any]]
    retrieval_ref: str | None
    graph_ref: str | None
    citation_ids: list[str]
    draft_answer: str
    critique: dict[str, Any] | None
    retry_count: int
    tool_call_count: int
    step_budget: int
    token_budget: int
    pending_review_id: int | None
    errors: list[str]
