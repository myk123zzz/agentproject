"""Synthesizer node — generates the final answer with citations."""

from typing import Any


def build_synthesized_answer(
    query: str,
    retrieval_context: str,
    graph_context: str = "",
    tool_observations: list[dict[str, Any]] | None = None,
) -> str:
    """Build an answer from retrieval, graph, and tool evidence.

    In production, this calls an LLM with the synthesizer prompt.
    """
    parts: list[str] = []

    if retrieval_context:
        parts.append(f"根据检索到的制度内容：\n{retrieval_context}")

    if graph_context:
        parts.append(f"根据知识图谱关系：\n{graph_context}")

    if tool_observations:
        for obs in tool_observations:
            parts.append(f"工具 [{obs.get('tool_name', 'unknown')}] 返回: {obs.get('result', '')}")

    if not parts:
        return f"未找到与'{query}'相关的制度信息。建议核实问题或联系制度管理员。"

    answer = f"关于'{query}'，综合以下信息：\n\n" + "\n\n".join(parts)
    answer += "\n\n如需进一步确认，请参考引用来源或提交人工审核。"

    return answer
