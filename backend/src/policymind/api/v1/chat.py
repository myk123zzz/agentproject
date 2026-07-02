"""Chat SSE streaming routes."""

from typing import Any

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from policymind.api.dependencies import RequestContext, get_current_context

router = APIRouter(prefix="/api/v1")


@router.post("/chat")
async def chat(
    payload: dict[str, Any],
    ctx: RequestContext = Depends(get_current_context),
) -> dict[str, Any]:
    """Non-streaming chat."""
    return {
        "thread_id": payload.get("thread_id", ""),
        "answer": "Chat endpoint — agent graph will process your query.",
        "tenant_id": ctx.tenant_id,
    }


@router.post("/chat/stream")
async def chat_stream(
    payload: dict[str, Any],
    ctx: RequestContext = Depends(get_current_context),
) -> StreamingResponse:
    """SSE streaming chat endpoint."""

    async def event_stream() -> Any:
        yield "event: routing\ndata: {\"route\": \"retrieval\"}\n\n"
        yield f"event: content\ndata: [{ctx.tenant_id}] 正在处理您的问题...\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/chat/{thread_id}/resume")
async def chat_resume(
    thread_id: str,
    payload: dict[str, Any],
    ctx: RequestContext = Depends(get_current_context),
) -> StreamingResponse:
    """Resume a HITL-interrupted chat by thread_id."""

    async def event_stream() -> Any:
        yield f"event: content\ndata: [{ctx.tenant_id}] 恢复会话 {thread_id}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
