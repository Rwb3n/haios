# generated: 2026-02-10
"""
Tests for CH-012 Ceremony Context Manager.

WORK-115: ceremony_context(), in_ceremony_context(), check_ceremony_required(),
CeremonyContext, and WorkEngine integration.

WORK-116: Ceremony adoption tests — verify execute_queue_transition and
cli.py cmd_close/cmd_archive/cmd_transition wrap state changes in ceremony_context.
"""
import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# WORK-117: Module loading handled by conftest.py (_load_module_once)
# Need bare `import governance_layer` for monkeypatch.setattr(module, attr, ...)
import governance_layer
import work_engine as work_engine_mod
import queue_ceremonies


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
            governance_layer, "_get_ceremony_enforcement", lambda: "warn"
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


# =========================================================================
# WORK-116: Ceremony Adoption Tests
# =========================================================================

import json

# WORK-117: _ensure_module, _get_gov_mod, and per-file module loading removed.
# conftest.py loads all modules once; governance_layer, work_engine_mod, and
# queue_ceremonies are imported at the top of this file.


def _read_events(events_file: Path) -> list:
    """Read JSONL events file."""
    events = []
    if events_file.exists():
        with open(events_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
    return events


@pytest.fixture
def w116_engine(tmp_path):
    """Create WorkEngine for WORK-116 tests."""
    return work_engine_mod.WorkEngine(
        governance=governance_layer.GovernanceLayer(), base_path=tmp_path
    )


@pytest.fixture(autouse=True)
def w116_patch_events(tmp_path, monkeypatch):
    """Redirect events files for test isolation.

    Session 338: Multiple test files use _load_module("governance_layer", ...)
    which unconditionally creates new module instances, each with its own
    ContextVar. work_engine_mod.check_ceremony_required was bound to whichever
    governance_layer existed when work_engine was loaded. We must ensure ALL
    ceremony_context/check_ceremony_required calls use the SAME ContextVar.

    Strategy: rebind work_engine_mod.check_ceremony_required to the current
    sys.modules["governance_layer"] so it shares ContextVar with ceremony_context
    (which resolves from sys.modules at call time via lazy import in cli.py and
    queue_ceremonies.py).
    """
    gov = governance_layer
    events_file = tmp_path / "test-events.jsonl"
    monkeypatch.setattr(queue_ceremonies, "EVENTS_FILE", events_file)
    # Patch event logging on the canonical module
    monkeypatch.setattr(
        gov, "_log_ceremony_event",
        lambda e: events_file.open("a").write(json.dumps(e) + "\n"),
    )
    # Defensive: ensures shared ContextVar even if module loading changes.
    # Can remove after WORK-117 verified stable. (S338 root cause: ContextVar divergence)
    monkeypatch.setattr(
        work_engine_mod, "check_ceremony_required", gov.check_ceremony_required
    )
    return events_file


@pytest.fixture(autouse=True)
def w116_clean_context():
    """Ensure clean ceremony context for each test."""
    governance_layer._clear_ceremony_context()
    yield
    governance_layer._clear_ceremony_context()


# =========================================================================
# Test 11: execute_queue_transition wraps in ceremony_context (no warning)
# =========================================================================
class TestQueueTransitionCeremonyAdoption:
    def test_execute_queue_transition_no_warning(self, w116_engine, caplog, monkeypatch):
        """execute_queue_transition wraps state change in ceremony_context — no warning."""
        monkeypatch.setattr(
            governance_layer, "_get_ceremony_enforcement", lambda: "warn"
        )

        # create_work in setup will warn (expected — not wrapped by this work item)
        w116_engine.create_work("WORK-QT1", "Queue Test 1")
        caplog.clear()  # Clear setup warnings

        with caplog.at_level(logging.WARNING):
            result = queue_ceremonies.execute_queue_transition(
                work_engine=w116_engine,
                work_id="WORK-QT1",
                to_position="ready",
                ceremony="Prioritize",
                rationale="Test",
                agent="test",
            )

        assert result["success"] is True
        # After WORK-116 implementation, this assertion should pass:
        # No "outside ceremony context" warning for set_queue_position
        governance_warnings = [
            r for r in caplog.records
            if r.levelno >= logging.WARNING
            and "outside ceremony context" in r.message
            and "set_queue_position" in r.message
        ]
        assert len(governance_warnings) == 0, (
            f"Expected no set_queue_position ceremony warnings, got: {[r.message for r in governance_warnings]}"
        )


# =========================================================================
# Test 12: execute_queue_transition logs CeremonyStart/CeremonyEnd events
# =========================================================================
class TestQueueTransitionCeremonyEvents:
    def test_execute_queue_transition_ceremony_events(self, w116_engine, w116_patch_events, monkeypatch):
        """execute_queue_transition produces CeremonyStart and CeremonyEnd events."""
        monkeypatch.setattr(
            governance_layer, "_get_ceremony_enforcement", lambda: "warn"
        )
        w116_engine.create_work("WORK-QT2", "Queue Test 2")

        queue_ceremonies.execute_queue_transition(
            work_engine=w116_engine,
            work_id="WORK-QT2",
            to_position="ready",
            ceremony="Prioritize",
        )

        events = _read_events(w116_patch_events)
        ceremony_starts = [e for e in events if e.get("type") == "CeremonyStart"]
        ceremony_ends = [e for e in events if e.get("type") == "CeremonyEnd"]

        assert len(ceremony_starts) >= 1, f"Expected CeremonyStart event, got: {events}"
        assert len(ceremony_ends) >= 1, f"Expected CeremonyEnd event, got: {events}"
        assert ceremony_starts[-1]["ceremony"] == "queue-prioritize"


# =========================================================================
# Test 13: cmd_close wraps in ceremony_context (no warning)
# =========================================================================
class TestCmdCloseCeremonyAdoption:
    def test_cmd_close_no_warning(self, w116_engine, tmp_path, caplog, monkeypatch):
        """cmd_close wraps engine.close() in ceremony_context — no warning."""
        monkeypatch.setattr(
            governance_layer, "_get_ceremony_enforcement", lambda: "warn"
        )
        # Create a work item to close
        w116_engine.create_work("WORK-CL1", "Close Test 1")
        caplog.clear()  # Clear setup warnings

        # WORK-117: cli exists in both lib/ and modules/ — must load the modules/ one
        # which has get_engine(). Inline load since `import cli` resolves to lib/cli.py.
        import importlib.util as _ilu
        _cli_path = Path(__file__).parent.parent / ".claude" / "haios" / "modules" / "cli.py"
        if "cli_modules" in sys.modules:
            cli_mod = sys.modules["cli_modules"]
        else:
            _spec = _ilu.spec_from_file_location("cli_modules", _cli_path)
            cli_mod = _ilu.module_from_spec(_spec)
            sys.modules["cli_modules"] = cli_mod
            _spec.loader.exec_module(cli_mod)

        # Monkeypatch cli.py's get_engine to return our test engine
        monkeypatch.setattr(cli_mod, "get_engine", lambda: w116_engine)

        with caplog.at_level(logging.WARNING):
            result = cli_mod.cmd_close("WORK-CL1")

        assert result == 0
        # After WORK-116 implementation, close should not warn
        governance_warnings = [
            r for r in caplog.records
            if r.levelno >= logging.WARNING
            and "outside ceremony context" in r.message
            and "'close'" in r.message
        ]
        assert len(governance_warnings) == 0, (
            f"Expected no close ceremony warnings, got: {[r.message for r in governance_warnings]}"
        )


# =========================================================================
# Test 14: Direct WorkEngine call outside ceremony still warns
# =========================================================================
class TestDirectCallStillWarns:
    def test_direct_set_queue_position_warns(self, w116_engine, caplog, monkeypatch):
        """Direct WorkEngine.set_queue_position outside ceremony_context still warns."""
        monkeypatch.setattr(
            governance_layer, "_get_ceremony_enforcement", lambda: "warn"
        )
        w116_engine.create_work("WORK-DW1", "Direct Warn Test")

        with caplog.at_level(logging.WARNING):
            w116_engine.set_queue_position("WORK-DW1", "ready")

        governance_warnings = [
            r for r in caplog.records
            if r.levelno >= logging.WARNING and "outside ceremony context" in r.message
        ]
        assert len(governance_warnings) > 0, (
            "Expected 'outside ceremony context' warning for direct call"
        )
