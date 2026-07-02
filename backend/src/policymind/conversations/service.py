"""ChatService — LangGraph agent execution with SSE streaming and HITL resume."""

from collections.abc import AsyncIterator
from typing import Any

from langgraph.types import Command


class ChatService:
    """Orchestrates LangGraph agent for chat messages."""

    def __init__(self, agent_graph: Any = None, mcp_client: Any = None):
        self._graph = agent_graph
        self._mcp = mcp_client

    async def invoke(self, command: Any) -> dict[str, Any]:
        """Non-streaming invocation — returns final state."""
        result = {"thread_id": getattr(command, "thread_id", "unknown"), "answer": ""}
        if self._graph:
            state = await self._graph.ainvoke(
                {"user_query": command.query if hasattr(command, "query") else str(command)},
                config={"configurable": {"thread_id": getattr(command, "thread_id", "default")}},
            )
            result["answer"] = state.get("draft_answer", "")
        return result

    async def stream(self, command: Any) -> AsyncIterator[dict[str, Any]]:
        """SSE-streaming execution. Yields routing, retrieval, content, citations, done."""
        yield {"event": "routing", "data": {"route": "retrieval", "reason": "default"}}
        yield {"event": "retrieval", "data": {"hits": 0}}
        yield {"event": "content", "data": "正在检索相关制度..."}
        if self._graph:
            try:
                async for event in self._graph.astream_events(
                    {"user_query": command.query if hasattr(command, "query") else str(command)},
                    config={"configurable": {"thread_id": getattr(command, "thread_id", "default")}},
                    version="v2",
                ):
                    yield {"event": event.get("event", "data"), "data": event.get("data", {})}
            except Exception:
                yield {"event": "error", "data": {"message": "Agent execution failed"}}
        yield {"event": "done", "data": {}}

    async def resume(
        self,
        thread_id: str,
        decision: dict[str, Any],
    ) -> AsyncIterator[dict[str, Any]]:
        """Resume a HITL-interrupted graph using Command(resume=...)."""
        if not self._graph:
            yield {"event": "error", "data": {"message": "No agent graph configured"}}
            yield {"event": "done", "data": {}}
            return

        try:
            async for event in self._graph.astream_events(
                Command(resume=decision),
                config={"configurable": {"thread_id": thread_id}},
                version="v2",
            ):
                yield {"event": event.get("event", "data"), "data": event.get("data", {})}
        except Exception as exc:
            yield {"event": "error", "data": {"message": str(exc)}}
        yield {"event": "done", "data": {}}
