"""Chat SSE streaming routes — connected to real ChatService + LangGraph agent."""

import json
from typing import Any

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from policymind.agents.graph import build_policy_graph
from policymind.api.dependencies import RequestContext, get_current_context
from policymind.conversations.service import ChatService

# Build agent graph once at module load (shared across requests)
_agent_graph = build_policy_graph()
_chat_service = ChatService(agent_graph=_agent_graph)

router = APIRouter(prefix="/api/v1")


@router.post("/chat")
async def chat(
    payload: dict[str, Any],
    ctx: RequestContext = Depends(get_current_context),
) -> dict[str, Any]:
    """Non-streaming chat — executed through ChatService → LangGraph agent."""
    result = await _chat_service.invoke(payload)
    return {"thread_id": payload.get("thread_id", ""), "answer": result.get("answer", ""), "tenant_id": ctx.tenant_id}


@router.post("/chat/stream")
async def chat_stream(
    payload: dict[str, Any],
    ctx: RequestContext = Depends(get_current_context),
) -> StreamingResponse:
    """SSE streaming chat — ChatService → LangGraph agent → real events."""

    async def event_stream() -> Any:
        try:
            async for evt in _chat_service.stream(payload):
                yield f"event: {evt['event']}\ndata: {json.dumps(evt.get('data', {}), default=str)}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'message': str(exc)})}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/chat/{thread_id}/resume")
async def chat_resume(
    thread_id: str,
    payload: dict[str, Any],
    ctx: RequestContext = Depends(get_current_context),
) -> StreamingResponse:
    """Resume a HITL-interrupted chat — uses Command(resume=...) internally."""

    async def event_stream() -> Any:
        decision = payload.get("decision", payload)
        try:
            async for evt in _chat_service.resume(thread_id, decision):
                yield f"event: {evt['event']}\ndata: {json.dumps(evt.get('data', {}), default=str)}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'message': str(exc)})}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
