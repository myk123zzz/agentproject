"""LangGraph agent graph — Supervisor→Retrieval|Graph|Planner→Executor→Synthesizer→Critic."""

from typing import Any, Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from policymind.agents.state import AgentState


def _normalize(state: AgentState) -> dict[str, Any]:
    return {"normalized_query": state.get("user_query", ""), "errors": []}


def _supervisor(state: AgentState) -> dict[str, Any]:
    from policymind.agents.supervisor import classify_query

    route, reason = classify_query(state.get("user_query", ""))
    return {"route": route, "route_reason": reason}


def _route_after_supervisor(state: AgentState) -> Literal["retrieval", "graph", "planner"]:
    route = state.get("route", "retrieval")
    if route in ("retrieval", "graph", "planner"):
        return route  # type: ignore[return-value]
    return "retrieval"


def _retrieval_node(state: AgentState) -> dict[str, Any]:
    return {"retrieval_ref": "retrieved"}


def _graph_node(state: AgentState) -> dict[str, Any]:
    return {"graph_ref": "graph_searched"}


def _planner_node(state: AgentState) -> dict[str, Any]:
    from policymind.agents.planner import plan_steps

    plan = plan_steps(state.get("user_query", ""))
    return {"plan": plan, "current_step_id": "1"}


def _executor_node(state: AgentState) -> dict[str, Any]:
    return {"completed_step_ids": state.get("completed_step_ids", []) + ["1"], "tool_call_count": 0}


def _synthesizer_node(state: AgentState) -> dict[str, Any]:
    return {"draft_answer": f"Answer: {state.get('user_query', '')}"}


def _critic_node(state: AgentState) -> dict[str, Any]:
    return {"critique": {"verdict": "pass", "reason": "ok", "should_interrupt": False}}


def _route_after_critic(state: AgentState) -> Literal["end", "replan", "interrupt"]:
    critique = state.get("critique", {})
    verdict = critique.get("verdict", "pass") if critique else "pass"
    if verdict == "interrupt":
        return "interrupt"
    if verdict == "replan" and state.get("retry_count", 0) < 2:
        return "replan"
    return "end"


def build_policy_graph() -> Any:
    """Construct and compile the PolicyMind agent graph."""
    builder = StateGraph(AgentState)

    builder.add_node("normalize", _normalize)
    builder.add_node("supervisor", _supervisor)
    builder.add_node("retrieval", _retrieval_node)
    builder.add_node("graph", _graph_node)
    builder.add_node("planner", _planner_node)
    builder.add_node("executor", _executor_node)
    builder.add_node("synthesizer", _synthesizer_node)
    builder.add_node("critic", _critic_node)

    builder.set_entry_point("normalize")
    builder.add_edge("normalize", "supervisor")

    builder.add_conditional_edges("supervisor", _route_after_supervisor, {
        "retrieval": "retrieval",
        "graph": "graph",
        "planner": "planner",
    })

    builder.add_edge("planner", "executor")
    builder.add_edge("executor", "synthesizer")
    builder.add_edge("retrieval", "synthesizer")
    builder.add_edge("graph", "synthesizer")

    builder.add_edge("synthesizer", "critic")
    builder.add_conditional_edges("critic", _route_after_critic, {
        "end": END,
        "replan": "planner",
        "interrupt": END,  # HITL: Interrupt is handled at the service layer
    })

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)
