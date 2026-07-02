"""Chat SSE streaming routes."""

from typing import Any

from fastapi import APIRouter
from starlette.responses import StreamingResponse

router = APIRouter(prefix="/api/v1")


@router.post("/chat")
async def chat(payload: dict[str, Any]) -> dict[str, Any]:
    """Non-streaming chat."""
    from policymind.conversations.service import ChatService

    svc = ChatService()
    return await svc.invoke(payload)


@router.post("/chat/stream")
async def chat_stream(payload: dict[str, Any]) -> StreamingResponse:
    """SSE streaming chat endpoint."""

    async def event_stream() -> Any:
        yield "event: routing\ndata: {\"route\": \"retrieval\"}\n\n"
        yield "event: content\ndata: 正在处理您的问题...\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/chat/{thread_id}/resume")
async def chat_resume(thread_id: str, payload: dict[str, Any]) -> StreamingResponse:
    """Resume a HITL-interrupted chat by thread_id."""

    async def event_stream() -> Any:
        yield f"event: content\ndata: 恢复会话 {thread_id}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
