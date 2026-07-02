"""Critic node — evaluates answer quality and decides pass/replan/interrupt."""

from typing import Any


def evaluate_answer(
    answer: str,
    has_citations: bool = False,
    has_evidence: bool = False,
    retry_count: int = 0,
) -> dict[str, Any]:
    """Evaluate answer and return critique.

    Returns dict with: verdict, reason, should_interrupt.
    """
    critique: dict[str, Any] = {
        "verdict": "pass",
        "reason": "",
        "should_interrupt": False,
        "retry_count": retry_count,
    }

    if not has_evidence:
        critique["verdict"] = "replan"
        critique["reason"] = "no_evidence_found"
        return critique

    if not has_citations:
        if retry_count < 2:
            critique["verdict"] = "replan"
            critique["reason"] = "missing_citations"
        else:
            critique["verdict"] = "interrupt"
            critique["reason"] = "persistent_missing_citations"
            critique["should_interrupt"] = True
        return critique

    # Low confidence detection
    if len(answer) < 20:
        critique["verdict"] = "interrupt"
        critique["reason"] = "low_confidence"
        critique["should_interrupt"] = True

    return critique


def needs_human_review(critique: dict[str, Any]) -> bool:
    """Decide if the critique triggers HITL."""
    return critique.get("should_interrupt", False) or critique.get("verdict") == "interrupt"
