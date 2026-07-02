"""Contract tests for MCP tools."""



class TestMCPTools:
    """All five enterprise tools must be callable and handle missing data."""

    def test_get_employee_profile_returns_employee(self):
        """get_employee_profile must return department, role, level."""
        from policymind.mcp.tools import get_employee_profile

        profile = get_employee_profile("EMP001")
        assert profile["employee_id"] == "EMP001"
        assert "department" in profile
        assert "role" in profile
        assert "access_level" in profile

    def test_get_approval_chain_returns_steps(self):
        """get_approval_chain must return ordered approval steps."""
        from policymind.mcp.tools import get_approval_chain

        chain = get_approval_chain(
            process_type="采购",
            department="研发部",
            amount=7000.0,
            employee_level=3,
        )
        assert len(chain["steps"]) > 0
        # Each step must have a role and order
        for step in chain["steps"]:
            assert "role" in step
            assert "order" in step

    def test_list_required_materials_returns_checklist(self):
        """list_required_materials must return materials and forms."""
        from policymind.mcp.tools import list_required_materials

        materials = list_required_materials("差旅报销")
        assert len(materials["materials"]) > 0

    def test_get_policy_version_returns_effective_version(self):
        """get_policy_version must return the version effective at a date."""
        from datetime import date

        from policymind.mcp.tools import get_policy_version

        version = get_policy_version("采购管理制度", at=date(2025, 6, 15))
        assert version["policy_name"] == "采购管理制度"
        assert "effective_from" in version
        assert "effective_to" in version
