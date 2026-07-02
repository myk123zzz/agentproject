"""ChatService — orchestrates agent graph execution for chat."""

from collections.abc import AsyncIterator
from typing import Any


class ChatService:
    """Orchestrates the LangGraph agent for each chat message."""

    def __init__(self, agent_graph: Any = None, mcp_client: Any = None):
        self._graph = agent_graph
        self._mcp = mcp_client

    async def invoke(self, command: Any) -> dict[str, Any]:
        """Non-streaming chat invocation."""
        return {
            "thread_id": getattr(command, "thread_id", "unknown"),
            "answer": "Chat invoke stub — real agent runs in stream mode.",
            "citations": [],
        }

    async def stream(self, command: Any) -> AsyncIterator[dict[str, Any]]:
        """SSE-streaming chat execution."""
        yield {"event": "routing", "data": {"route": "retrieval", "reason": "default"}}
        yield {"event": "retrieval", "data": {"hits": 0}}
        yield {"event": "content", "data": "正在检索相关制度..."}
        yield {"event": "done", "data": {}}

    async def resume(
        self,
        thread_id: str,
        decision: dict[str, Any],
    ) -> AsyncIterator[dict[str, Any]]:
        """Resume a paused graph from a HITL interrupt."""
        yield {"event": "content", "data": f"恢复会话 {thread_id}，决策: {decision}"}
        yield {"event": "done", "data": {}}
