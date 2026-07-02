"""Five enterprise MCP tools — read-only + one write (HITL-protected)."""

from datetime import date
from typing import Any


def get_employee_profile(employee_id: str) -> dict[str, Any]:
    """Return department, role, level for an employee."""
    # Demo data via repository pattern — real implementation queries DB
    profiles: dict[str, dict[str, Any]] = {
        "EMP001": {
            "employee_id": "EMP001",
            "name": "张三",
            "department": "研发部",
            "role": "高级工程师",
            "access_level": 2,
        },
        "EMP002": {
            "employee_id": "EMP002",
            "name": "李四",
            "department": "财务部",
            "role": "财务主管",
            "access_level": 3,
        },
    }
    return profiles.get(employee_id, {
        "employee_id": employee_id,
        "department": "未知",
        "role": "未知",
        "access_level": 0,
    })


def get_approval_chain(
    process_type: str,
    department: str,
    amount: float = 0.0,
    employee_level: int = 0,
) -> dict[str, Any]:
    """Return ordered approval steps based on process type and amount."""
    steps: list[dict[str, Any]] = []
    if amount <= 5000:
        steps = [
            {"order": 1, "role": "直属上级", "condition": "金额 ≤ 5000"},
            {"order": 2, "role": "部门负责人", "condition": "金额 ≤ 5000"},
        ]
    elif amount <= 50000:
        steps = [
            {"order": 1, "role": "直属上级", "condition": "5000 < 金额 ≤ 50000"},
            {"order": 2, "role": "部门负责人", "condition": "5000 < 金额 ≤ 50000"},
            {"order": 3, "role": "分管副总", "condition": "金额 > 5000"},
        ]
    else:
        steps = [
            {"order": 1, "role": "直属上级", "condition": "金额 > 50000"},
            {"order": 2, "role": "部门负责人", "condition": "金额 > 50000"},
            {"order": 3, "role": "分管副总", "condition": "金额 > 50000"},
            {"order": 4, "role": "总经理", "condition": "金额 > 50000"},
            {"order": 5, "role": "董事会", "condition": "金额 > 50000"},
        ]

    return {
        "process_type": process_type,
        "department": department,
        "amount": amount,
        "steps": steps,
        "total_steps": len(steps),
    }


def list_required_materials(process_type: str) -> dict[str, Any]:
    """Return checklist of materials, templates, and prerequisites."""
    checklists: dict[str, dict[str, Any]] = {
        "差旅报销": {
            "materials": [
                {"name": "出差申请单", "required": True, "template": "TRV-001"},
                {"name": "交通票据原件", "required": True, "template": None},
                {"name": "住宿发票", "required": True, "template": None},
                {"name": "出差报告", "required": False, "template": "TRV-002"},
            ],
        },
        "采购": {
            "materials": [
                {"name": "采购申请单", "required": True, "template": "PRC-001"},
                {"name": "供应商比价表", "required": True, "template": "PRC-002"},
                {"name": "合同草案", "required": True, "template": None},
            ],
        },
    }
    return checklists.get(
        process_type,
        {"materials": [{"name": "请咨询行政部门", "required": True, "template": None}]},
    )


def get_policy_version(policy_name: str, at: date | None = None) -> dict[str, Any]:
    """Return the version of a policy effective at a given date."""
    from datetime import date as dt

    pd = at or dt.today()
    # Demo: 采购管理制度 has two versions
    if policy_name == "采购管理制度":
        if pd >= dt(2025, 1, 1):
            return {
                "policy_name": policy_name,
                "version": "2.0",
                "effective_from": "2025-01-01",
                "effective_to": None,
            }
        return {
            "policy_name": policy_name,
            "version": "1.0",
            "effective_from": "2023-01-01",
            "effective_to": "2024-12-31",
        }
    return {
        "policy_name": policy_name,
        "version": "1.0",
        "effective_from": "2023-01-01",
        "effective_to": None,
    }


def create_review_ticket(
    question: str,
    evidence: str,
    conflict: str = "",
    suggested_reviewer: str = "",
) -> dict[str, Any]:
    """Create a human review ticket.  Write operation — requires HITL approval."""
    import uuid

    return {
        "ticket_id": uuid.uuid4().hex[:12],
        "question": question,
        "evidence": evidence,
        "conflict": conflict,
        "suggested_reviewer": suggested_reviewer,
        "status": "pending_review",
    }
