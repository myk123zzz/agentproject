"""MCP Client — connects to the policy MCP server via transport."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class MCPTool:
    name: str
    description: str
    parameters: dict[str, Any]


@dataclass
class ToolObservation:
    tool_name: str
    arguments: dict[str, Any]
    result: dict[str, Any]
    risk_level: str = "low"
    requires_approval: bool = False


class EnterpriseMCPClient:
    """Client that calls tools via the MCP server transport.

    In production, this uses stdio/HTTP transport to the policy-mcp-server process.
    For development, it can call tools directly via import.
    """

    def __init__(self, transport_mode: str = "direct"):
        self._mode = transport_mode
        self._tools: dict[str, MCPTool] = {}

    async def connect(self) -> None:
        """Connect to the MCP server and discover tools."""

        self._tools = {
            "get_employee_profile": MCPTool(
                name="get_employee_profile",
                description="查询员工部门、岗位、职级和访问级别",
                parameters={"employee_id": "str"},
            ),
            "get_approval_chain": MCPTool(
                name="get_approval_chain",
                description="查询流程审批步骤和适用规则",
                parameters={"process_type": "str", "department": "str", "amount": "float"},
            ),
            "list_required_materials": MCPTool(
                name="list_required_materials",
                description="查询材料清单、模板和前置条件",
                parameters={"process_type": "str"},
            ),
            "get_policy_version": MCPTool(
                name="get_policy_version",
                description="查询制度在指定日期的有效版本",
                parameters={"policy_name": "str", "at": "date"},
            ),
            "create_review_ticket": MCPTool(
                name="create_review_ticket",
                description="创建人工审核工单",
                parameters={"question": "str", "evidence": "str"},
            ),
        }

    async def list_tools(self) -> list[MCPTool]:
        await self.connect()
        return list(self._tools.values())

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        approval_token: str | None = None,
    ) -> ToolObservation:
        """Invoke a tool by name. Write tools require a valid approval token.

        Raises ApprovalRequired if a write tool is called without approval.
        """
        from policymind.core.errors import ApprovalRequired

        if name == "create_review_ticket" and not approval_token:
            raise ApprovalRequired("create_review_ticket requires HITL approval")
        # In production: validate approval token (thread_id, tool, args hash, expiry)

        from policymind.mcp.tools import (
            create_review_ticket,
            get_approval_chain,
            get_employee_profile,
            get_policy_version,
            list_required_materials,
        )

        tool_map: dict[str, Callable[..., Any]] = {
            "get_employee_profile": get_employee_profile,
            "get_approval_chain": get_approval_chain,
            "list_required_materials": list_required_materials,
            "get_policy_version": get_policy_version,
            "create_review_ticket": create_review_ticket,
        }

        func = tool_map.get(name)
        if func is None:
            raise ValueError(f"Unknown tool: {name}")

        result = func(**arguments)
        requires_approval = name == "create_review_ticket"
        return ToolObservation(
            tool_name=name,
            arguments=arguments,
            result=result,
            risk_level="high" if requires_approval else "low",
            requires_approval=requires_approval,
        )
