"""Conversation and message models."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatCommand:
    thread_id: str = ""
    query: str = ""


@dataclass
class ChatResult:
    thread_id: str
    answer: str
    citations: list[dict[str, Any]] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    pending_review: bool = False
