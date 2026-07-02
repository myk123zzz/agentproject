"""Planner node — decomposes complex queries into DAG-structured steps."""

from typing import Any


def validate_plan_is_dag(plan: list[dict[str, Any]]) -> bool:
    """Verify that a plan has no cyclic dependencies."""
    step_ids = {s["step_id"] for s in plan}
    for step in plan:
        for dep in step.get("dependencies", []):
            if dep not in step_ids:
                return False
            # Dependency must refer to an earlier step
            dep_step = next(s for s in plan if s["step_id"] == dep)
            if dep_step["step_id"] >= step["step_id"]:
                return False
    return True


def plan_steps(query: str) -> list[dict[str, Any]]:
    """Generate a plan from a complex query (rule-based fallback)."""
    # In production, this calls an LLM with planner prompt
    return [
        {
            "step_id": 1,
            "description": f"检索与'{query}'相关的制度条款",
            "tool_or_capability": "hybrid_rag",
            "dependencies": [],
            "expected_output": "相关制度原文和引用",
            "risk_level": "low",
        },
        {
            "step_id": 2,
            "description": "查询涉及的部门、角色和审批关系",
            "tool_or_capability": "graph_rag",
            "dependencies": [1],
            "expected_output": "部门和审批关系路径",
            "risk_level": "low",
        },
        {
            "step_id": 3,
            "description": "综合检索和关系信息，生成结论",
            "tool_or_capability": "synthesizer",
            "dependencies": [1, 2],
            "expected_output": "带引用的完整答案",
            "risk_level": "low",
        },
    ]
