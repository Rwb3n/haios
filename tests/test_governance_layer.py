# generated: 2026-01-03
# System Auto: last updated on: 2026-01-04T20:09:43
"""
Tests for GovernanceLayer module (E2-240).

Tests L4 functional requirements:
- check_gate(gate_id, context) -> GateResult
- validate_transition(from_node, to_node) -> bool
- load_handlers(config_path) -> dict
- on_event(event_type, payload) -> None

Tests L4 invariants:
- MUST NOT modify work files directly
- MUST log all gate decisions for audit
- MUST be stateless
"""
import sys
from pathlib import Path

import pytest

# Add module path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "modules"))
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))


class TestCheckGate:
    """Tests for check_gate function (L4 requirement)."""

    def test_check_gate_returns_gate_result(self):
        """L4: check_gate(gate_id, context) returns GateResult(allowed, reason)."""
        from governance_layer import GovernanceLayer, GateResult

        layer = GovernanceLayer()
        context = {"work_id": "E2-240", "dod_complete": False}

        result = layer.check_gate("dod", context)

        assert isinstance(result, GateResult)
        assert hasattr(result, "allowed")
        assert hasattr(result, "reason")

    def test_check_gate_denies_incomplete_dod(self):
        """L4 Acceptance: Returns deny for incomplete DoD."""
        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()
        context = {"work_id": "E2-240", "tests_pass": False}

        result = layer.check_gate("dod", context)

        assert result.allowed is False
        assert "incomplete" in result.reason.lower() or "dod" in result.reason.lower()


class TestValidateTransition:
    """Tests for validate_transition function (L4 requirement)."""

    def test_validate_transition_allows_valid(self):
        """L4: Allows valid DAG transitions."""
        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()

        # Valid transitions
        assert layer.validate_transition("backlog", "discovery") is True
        assert layer.validate_transition("backlog", "plan") is True
        assert layer.validate_transition("plan", "implement") is True

    def test_validate_transition_blocks_invalid(self):
        """L4: Blocks invalid transitions (e.g., backlog->complete)."""
        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()

        # Invalid transition (skip implement)
        assert layer.validate_transition("backlog", "complete") is False

        # Invalid transition from terminal node
        assert layer.validate_transition("complete", "backlog") is False


class TestLoadHandlers:
    """Tests for load_handlers function (L4 requirement)."""

    def test_load_handlers_returns_registry(self, tmp_path):
        """L4: load_handlers(config_path) returns Handler registry."""
        from governance_layer import GovernanceLayer

        # Create test config
        config_file = tmp_path / "components.yaml"
        config_file.write_text("hooks: {}\nskills: {}\nagents: {}")

        layer = GovernanceLayer()
        handlers = layer.load_handlers(str(config_file))

        assert isinstance(handlers, dict)

    def test_load_handlers_missing_file_returns_empty(self):
        """Missing config file returns empty dict (graceful degradation)."""
        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()
        handlers = layer.load_handlers("/nonexistent/path.yaml")

        assert handlers == {}


class TestOnEvent:
    """Tests for on_event function (L4 requirement)."""

    def test_on_event_routes_to_handler(self, mocker):
        """L4: on_event(event_type, payload) routes to correct handlers."""
        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()
        mock_handler = mocker.Mock()
        layer._handlers = {"work_transition": [mock_handler]}

        layer.on_event("work_transition", {"work_id": "E2-240", "to_node": "plan"})

        mock_handler.assert_called_once_with({"work_id": "E2-240", "to_node": "plan"})


class TestInvariants:
    """Tests for L4 invariants."""

    def test_governance_layer_is_stateless(self):
        """L4 Invariant: MUST be stateless (no internal state between calls)."""
        from governance_layer import GovernanceLayer

        layer1 = GovernanceLayer()
        layer2 = GovernanceLayer()

        # Different instances should produce same results for same input
        result1 = layer1.check_gate("dod", {"tests_pass": True, "why_captured": True, "docs_current": True})
        result2 = layer2.check_gate("dod", {"tests_pass": True, "why_captured": True, "docs_current": True})

        assert result1.allowed == result2.allowed

    def test_logs_all_gate_decisions(self, mocker):
        """L4 Invariant: MUST log all gate decisions for audit."""
        # Mock the logging function
        mock_log = mocker.patch("governance_layer.log_validation_outcome")

        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()
        layer.check_gate("dod", {"work_id": "E2-240"})

        mock_log.assert_called_once()

    def test_does_not_modify_work_files(self, tmp_path):
        """L4 Invariant: MUST NOT modify work files directly."""
        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()
        work_file = tmp_path / "WORK.md"
        work_file.write_text("status: active\ncurrent_node: backlog")
        original_content = work_file.read_text()

        # Call various methods with work file context
        layer.check_gate("dod", {"work_id": "E2-240", "work_path": str(work_file)})
        layer.validate_transition("backlog", "plan")

        # File should be unchanged
        assert work_file.read_text() == original_content


# =============================================================================
# E2-252: Template Validation and Scaffolding Tests
# =============================================================================


class TestValidateTemplate:
    """Tests for validate_template method (E2-252)."""

    def test_governance_layer_has_validate_template(self):
        """GovernanceLayer should have validate_template method."""
        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()
        assert hasattr(layer, "validate_template")
        assert callable(layer.validate_template)

    def test_validate_template_valid_file(self, tmp_path):
        """Valid template should return is_valid=True."""
        from governance_layer import GovernanceLayer

        # Create minimal valid checkpoint
        checkpoint = tmp_path / "test.md"
        checkpoint.write_text(
            """---
template: checkpoint
status: active
date: 2026-01-04
version: '1.0'
author: Test
project_phase: test
---
# Test

@docs/README.md
@docs/epistemic_state.md
"""
        )
        layer = GovernanceLayer()
        result = layer.validate_template(str(checkpoint))
        assert result["is_valid"] is True

    def test_validate_template_missing_field(self, tmp_path):
        """Missing required field should return is_valid=False."""
        from governance_layer import GovernanceLayer

        checkpoint = tmp_path / "test.md"
        checkpoint.write_text(
            """---
template: checkpoint
status: active
---
# Test
"""
        )
        layer = GovernanceLayer()
        result = layer.validate_template(str(checkpoint))
        assert result["is_valid"] is False
        assert any("Missing" in e for e in result["errors"])


class TestScaffoldTemplate:
    """Tests for scaffold_template method (E2-252)."""

    def test_governance_layer_has_scaffold_template(self):
        """GovernanceLayer should have scaffold_template method."""
        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()
        assert hasattr(layer, "scaffold_template")
        assert callable(layer.scaffold_template)

    def test_scaffold_template_creates_file(self, tmp_path):
        """scaffold_template should create file in output_path."""
        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()
        output = tmp_path / "test_checkpoint.md"
        result = layer.scaffold_template(
            template="checkpoint",
            output_path=str(output),
            backlog_id="999",
            title="Test",
        )
        assert output.exists()
        assert "checkpoint" in output.read_text().lower()


# =============================================================================
# E2-248: Error Visibility Tests
# =============================================================================


class TestErrorVisibility:
    """Tests for E2-248: GovernanceLayer Error Visibility."""

    def test_gate_result_has_degraded_field(self):
        """GateResult should have optional degraded field."""
        from governance_layer import GateResult

        # Default should be False
        result = GateResult(allowed=True, reason="test")
        assert hasattr(result, "degraded")
        assert result.degraded is False

        # Explicit degraded state
        degraded_result = GateResult(allowed=True, reason="partial", degraded=True)
        assert degraded_result.degraded is True

    def test_load_handlers_logs_yaml_error(self, tmp_path, caplog):
        """load_handlers should log errors when YAML parsing fails."""
        from governance_layer import GovernanceLayer
        import logging

        # Create invalid YAML
        bad_config = tmp_path / "bad.yaml"
        bad_config.write_text("invalid: yaml: content: [")

        layer = GovernanceLayer()
        with caplog.at_level(logging.WARNING):
            result = layer.load_handlers(str(bad_config))

        assert result == {}  # Graceful degradation
        assert "Failed to load handlers" in caplog.text
        assert str(bad_config) in caplog.text

    def test_on_event_logs_handler_exception(self, caplog):
        """on_event should log when handler raises exception."""
        from governance_layer import GovernanceLayer
        import logging

        def failing_handler(payload):
            raise ValueError("Handler exploded")

        layer = GovernanceLayer()
        layer._handlers = {"test_event": [failing_handler]}

        with caplog.at_level(logging.WARNING):
            layer.on_event("test_event", {"data": "test"})

        assert "Handler failed" in caplog.text
        assert "test_event" in caplog.text

    def test_existing_gate_result_behavior_unchanged(self):
        """Existing code using GateResult(allowed, reason) should still work."""
        from governance_layer import GateResult

        # Old-style construction still works
        result = GateResult(allowed=True, reason="test")
        assert result.allowed is True
        assert result.reason == "test"
        assert result.degraded is False  # Default value


# =============================================================================
# E2-260: Toggle Access Tests
# =============================================================================


class TestGetToggle:
    """Tests for get_toggle method (E2-260)."""

    def test_get_toggle_returns_value(self):
        """get_toggle returns toggle value from config."""
        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()
        # block_powershell is defined in haios.yaml
        result = layer.get_toggle("block_powershell")
        assert isinstance(result, bool)

    def test_get_toggle_unknown_returns_default(self):
        """get_toggle returns default for unknown toggle."""
        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()
        result = layer.get_toggle("nonexistent_toggle", default=False)
        assert result is False
