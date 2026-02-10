# generated: 2026-02-10
"""
Tests for CH-012 Ceremony Context Manager (WORK-115).

Tests ceremony_context(), in_ceremony_context(), check_ceremony_required(),
CeremonyContext, and WorkEngine integration.
"""
import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add module path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "modules"))
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


# =========================================================================
# Test 1: ceremony_context logs start and end events
# =========================================================================
class TestCeremonyContextLogging:
    def test_ceremony_context_logs_start_end(self, monkeypatch):
        """CeremonyStart event on enter, CeremonyEnd event on exit."""
        from governance_layer import ceremony_context

        logged = []
        monkeypatch.setattr(
            "governance_layer._log_ceremony_event", lambda e: logged.append(e)
        )

        with ceremony_context("close-work"):
            pass

        assert len(logged) == 2
        assert logged[0]["type"] == "CeremonyStart"
        assert logged[0]["ceremony"] == "close-work"
        assert logged[1]["type"] == "CeremonyEnd"
        assert logged[1]["ceremony"] == "close-work"

    def test_ceremony_context_logs_end_on_exception(self, monkeypatch):
        """CeremonyEnd still logged even if body raises exception."""
        from governance_layer import ceremony_context

        logged = []
        monkeypatch.setattr(
            "governance_layer._log_ceremony_event", lambda e: logged.append(e)
        )

        with pytest.raises(ValueError):
            with ceremony_context("close-work"):
                raise ValueError("test error")

        assert len(logged) == 2
        assert logged[1]["type"] == "CeremonyEnd"


# =========================================================================
# Test 2: in_ceremony_context returns correct state
# =========================================================================
class TestInCeremonyContext:
    def test_in_ceremony_context_true_inside(self, monkeypatch):
        """in_ceremony_context() returns True inside ceremony_context."""
        from governance_layer import ceremony_context, in_ceremony_context

        monkeypatch.setattr(
            "governance_layer._log_ceremony_event", lambda e: None
        )

        with ceremony_context("test"):
            assert in_ceremony_context() is True

    def test_in_ceremony_context_false_outside(self):
        """in_ceremony_context() returns False outside ceremony_context."""
        from governance_layer import in_ceremony_context, _clear_ceremony_context

        # Ensure clean state
        _clear_ceremony_context()
        assert in_ceremony_context() is False


# =========================================================================
# Test 3: CeremonyContext object has methods
# =========================================================================
class TestCeremonyContextObject:
    def test_ceremony_context_has_methods(self, monkeypatch):
        """CeremonyContext provides execute_step and log_side_effect."""
        from governance_layer import ceremony_context

        monkeypatch.setattr(
            "governance_layer._log_ceremony_event", lambda e: None
        )

        with ceremony_context("close-work") as ctx:
            assert hasattr(ctx, "execute_step")
            assert hasattr(ctx, "log_side_effect")
            assert ctx.ceremony_name == "close-work"


# =========================================================================
# Test 4: log_side_effect records effect
# =========================================================================
class TestLogSideEffect:
    def test_log_side_effect_records(self, monkeypatch):
        """log_side_effect() stores effect in context."""
        from governance_layer import ceremony_context

        monkeypatch.setattr(
            "governance_layer._log_ceremony_event", lambda e: None
        )

        with ceremony_context("close-work") as ctx:
            ctx.log_side_effect("status_changed", {"from": "active", "to": "complete"})
            assert len(ctx.side_effects) == 1
            assert ctx.side_effects[0]["effect"] == "status_changed"
            assert ctx.side_effects[0]["details"]["from"] == "active"

    def test_execute_step_records_as_side_effect(self, monkeypatch):
        """execute_step() records step as side effect."""
        from governance_layer import ceremony_context

        monkeypatch.setattr(
            "governance_layer._log_ceremony_event", lambda e: None
        )

        with ceremony_context("close-work") as ctx:
            ctx.execute_step("observation-capture", work_id="WORK-115")
            assert len(ctx.side_effects) == 1
            assert ctx.side_effects[0]["effect"] == "step:observation-capture"


# =========================================================================
# Test 5: Nesting is forbidden
# =========================================================================
class TestNestingForbidden:
    def test_nesting_raises_error(self, monkeypatch):
        """Nested ceremony_context raises CeremonyNestingError."""
        from governance_layer import ceremony_context, CeremonyNestingError

        monkeypatch.setattr(
            "governance_layer._log_ceremony_event", lambda e: None
        )

        with ceremony_context("outer"):
            with pytest.raises(CeremonyNestingError, match="Cannot nest"):
                with ceremony_context("inner"):
                    pass


# =========================================================================
# Test 6: Warn mode logs warning
# =========================================================================
class TestWarnMode:
    def test_warn_mode_logs_warning(self, monkeypatch, caplog):
        """In warn mode, check_ceremony_required logs warning but does not raise."""
        from governance_layer import check_ceremony_required, _clear_ceremony_context

        _clear_ceremony_context()
        monkeypatch.setattr(
            "governance_layer._get_ceremony_enforcement", lambda: "warn"
        )

        with caplog.at_level(logging.WARNING):
            check_ceremony_required("close")  # Should not raise

        assert "outside ceremony context" in caplog.text


# =========================================================================
# Test 7: Block mode raises error
# =========================================================================
class TestBlockMode:
    def test_block_mode_raises_error(self, monkeypatch):
        """In block mode, check_ceremony_required raises CeremonyRequiredError."""
        from governance_layer import (
            check_ceremony_required,
            CeremonyRequiredError,
            _clear_ceremony_context,
        )

        _clear_ceremony_context()
        monkeypatch.setattr(
            "governance_layer._get_ceremony_enforcement", lambda: "block"
        )

        with pytest.raises(CeremonyRequiredError, match="close"):
            check_ceremony_required("close")


# =========================================================================
# Test 8: WorkEngine.close outside ceremony triggers enforcement
# =========================================================================
class TestWorkEngineOutsideCeremony:
    def test_work_engine_close_outside_ceremony_block(self, tmp_path, monkeypatch):
        """WorkEngine.close() outside ceremony context raises in block mode."""
        from governance_layer import GovernanceLayer, CeremonyRequiredError, _clear_ceremony_context
        from work_engine import WorkEngine

        _clear_ceremony_context()
        monkeypatch.setattr(
            "governance_layer._get_ceremony_enforcement", lambda: "block"
        )

        engine = WorkEngine(governance=GovernanceLayer(), base_path=tmp_path)

        with pytest.raises(CeremonyRequiredError, match="close"):
            engine.close("WORK-TEST")


# =========================================================================
# Test 9: WorkEngine.close inside ceremony succeeds
# =========================================================================
class TestWorkEngineInsideCeremony:
    def test_work_engine_close_inside_ceremony(self, tmp_path, monkeypatch):
        """WorkEngine.close() inside ceremony_context succeeds normally."""
        from governance_layer import (
            GovernanceLayer,
            ceremony_context,
            _clear_ceremony_context,
        )
        from work_engine import WorkEngine, WorkNotFoundError

        _clear_ceremony_context()
        monkeypatch.setattr(
            "governance_layer._log_ceremony_event", lambda e: None
        )
        monkeypatch.setattr(
            "governance_layer._get_ceremony_enforcement", lambda: "block"
        )

        engine = WorkEngine(governance=GovernanceLayer(), base_path=tmp_path)

        # close() will raise WorkNotFoundError (no actual work item),
        # but it should NOT raise CeremonyRequiredError
        with ceremony_context("close-work"):
            with pytest.raises(WorkNotFoundError):
                engine.close("WORK-TEST")


# =========================================================================
# Test 10: Backward compatibility - default warn mode
# =========================================================================
class TestDefaultEnforcement:
    def test_default_enforcement_is_warn(self):
        """Default enforcement mode is 'warn' for backward compatibility."""
        from governance_layer import _get_ceremony_enforcement

        # _get_ceremony_enforcement reads from ConfigLoader which may
        # not have ceremony_context_enforcement set - should default to warn
        mode = _get_ceremony_enforcement()
        assert mode == "warn"
