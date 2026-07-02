"""ReAct Executor — controlled tool-calling loop with budgets."""

from typing import Any


class ExecutorBudget:
    """Enforce step and tool-call limits."""

    def __init__(self, max_tool_calls: int = 10, max_retries: int = 2):
        self.max_tool_calls = max_tool_calls
        self.max_retries = max_retries
        self.tool_call_count = 0
        self.retry_count = 0

    def can_call_tool(self) -> bool:
        return self.tool_call_count < self.max_tool_calls

    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries

    def record_call(self) -> None:
        self.tool_call_count += 1

    def record_retry(self) -> None:
        self.retry_count += 1


def execute_step(
    step: dict[str, Any],
    observations: list[dict[str, Any]],
    budget: ExecutorBudget,
    mcp_client: Any = None,
) -> dict[str, Any]:
    """Execute one plan step, possibly calling multiple tools."""
    capability = step.get("tool_or_capability", "")

    result: dict[str, Any] = {
        "step_id": step["step_id"],
        "status": "completed",
        "tool_calls": [],
    }

    if capability == "hybrid_rag":
        result["observation"] = {"retrieval": "检索完成"}
    elif capability == "graph_rag":
        result["observation"] = {"graph": "图谱查询完成"}
    elif capability == "synthesizer":
        result["observation"] = {"synthesis": "生成完成"}
    elif mcp_client is not None and budget.can_call_tool():
        budget.record_call()
        result["tool_calls"].append({"tool": capability, "status": "ok"})

    return result
