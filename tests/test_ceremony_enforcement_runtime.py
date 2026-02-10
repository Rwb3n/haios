# generated: 2026-02-10
"""
Tests for ceremony contract enforcement at runtime (WORK-114).

Verifies that PreToolUse hook validates ceremony input contracts
when ceremony skills are invoked, using enforce_ceremony_contract()
from lib/ceremony_contracts.py.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml

# Add hooks directory to path for imports
HOOKS_DIR = Path(__file__).parent.parent / ".claude" / "hooks" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

# Add lib directory for ceremony_contracts
LIB_DIR = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
sys.path.insert(0, str(LIB_DIR))


class TestCeremonyContractEnforcement:
    """Test _check_ceremony_contract() integration in PreToolUse hook."""

    def test_ceremony_skill_triggers_contract_check(self):
        """Skills listed in ceremony_registry.yaml trigger contract validation.

        queue-commit is a ceremony with required field work_id.
        With empty inputs (PreToolUse can't extract structured args),
        validation should return allow-with-warning in default warn mode.
        """
        from pre_tool_use import _check_ceremony_contract

        result = _check_ceremony_contract(
            "queue-commit", {"skill": "queue-commit"}
        )
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"
        reason = result["hookSpecificOutput"].get("permissionDecisionReason", "")
        assert "contract" in reason.lower() or "required" in reason.lower()

    def test_non_ceremony_skill_returns_none(self):
        """Non-ceremony skills (implementation-cycle, survey-cycle) skip validation."""
        from pre_tool_use import _check_ceremony_contract

        result = _check_ceremony_contract(
            "implementation-cycle", {"skill": "implementation-cycle"}
        )
        assert result is None

        result2 = _check_ceremony_contract(
            "survey-cycle", {"skill": "survey-cycle"}
        )
        assert result2 is None

    def test_ceremony_no_required_fields_passes(self):
        """Ceremony with only optional input fields returns None (contract satisfied)."""
        from pre_tool_use import _check_ceremony_contract, _parse_skill_contract

        # Find a ceremony that has no required fields, or test via mock
        # Test the underlying logic: if contract has no required fields,
        # validate_ceremony_input returns valid=True, function returns None
        from ceremony_contracts import (
            CeremonyContract,
            ContractField,
            OutputField,
            validate_ceremony_input,
        )

        contract = CeremonyContract(
            name="test-ceremony",
            category="session",
            input_contract=[
                ContractField(
                    field="note",
                    type="string",
                    required=False,
                    description="Optional note",
                )
            ],
            output_contract=[
                OutputField(
                    field="success",
                    type="boolean",
                    guaranteed="always",
                    description="Result",
                )
            ],
            side_effects=["Logs event"],
        )
        result = validate_ceremony_input(contract, {})
        assert result.valid is True

    def test_warn_mode_allows_with_warning(self):
        """In warn mode (default), missing required fields produce allow + warning."""
        from pre_tool_use import _check_ceremony_contract

        # Default haios.yaml has ceremony_contract_enforcement: warn
        result = _check_ceremony_contract(
            "queue-commit", {"skill": "queue-commit"}
        )
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"
        reason = result["hookSpecificOutput"].get("permissionDecisionReason", "")
        assert len(reason) > 0  # Should have warning text

    def test_block_mode_denies(self, tmp_path):
        """In block mode, missing required fields produce deny response."""
        from pre_tool_use import _check_ceremony_contract

        # Create a temporary haios.yaml with block mode
        config = tmp_path / "haios.yaml"
        config.write_text(
            yaml.dump({"toggles": {"ceremony_contract_enforcement": "block"}})
        )

        # Patch _read_enforcement_toggle to use our config
        with patch(
            "ceremony_contracts._read_enforcement_toggle", return_value="block"
        ):
            result = _check_ceremony_contract(
                "queue-commit", {"skill": "queue-commit"}
            )
            assert result is not None
            assert result["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_missing_skill_file_returns_none(self):
        """If ceremony skill SKILL.md doesn't exist, skip validation gracefully."""
        from pre_tool_use import _check_ceremony_contract

        # Patch _find_skill_path to return None (skill file not found)
        with patch("pre_tool_use._find_skill_path", return_value=None):
            result = _check_ceremony_contract(
                "queue-commit", {"skill": "queue-commit"}
            )
            assert result is None
