"""Test that the LangGraph agent graph builds and compiles correctly."""


class TestPolicyGraph:
    """The agent StateGraph must compile and process a basic query."""

    def test_graph_builds_without_error(self):
        """Graph compilation must succeed with all nodes and edges."""
        from policymind.agents.graph import build_policy_graph

        graph = build_policy_graph()
        assert graph is not None

    def test_graph_invokes_normalize_and_supervisor(self):
        """A simple query must route through normalize → supervisor → end."""
        import asyncio

        from policymind.agents.graph import build_policy_graph

        graph = build_policy_graph()
        result = asyncio.run(
            graph.ainvoke(
                {"user_query": "采购制度是什么？"},
                config={"configurable": {"thread_id": "test-1"}},
            )
        )
        assert "route" in result
        assert result["route"] in ("retrieval", "graph", "planner")


class TestChatService:
    """ChatService resume must use Command(resume=...)."""

    def test_resume_without_graph_yields_error(self):
        """Without a graph, resume yields an error event."""
        import asyncio

        from policymind.conversations.service import ChatService

        async def _run():
            svc = ChatService(agent_graph=None)
            events = []
            async for e in svc.resume("t1", {"decision": "approve"}):
                events.append(e)
            return events

        events = asyncio.run(_run())
        assert any(e["event"] == "error" for e in events)
