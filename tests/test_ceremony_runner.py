# generated: 2026-02-11
# WORK-118: CeremonyRunner tests (CH-013 CeremonyLifecycleDistinction)
"""
Tests for CeremonyRunner — ceremony phase validation and invocation.

Verifies:
- CEREMONY_PHASES contains only ceremony entries (not lifecycles)
- CYCLE_PHASES contains only lifecycle entries (not ceremonies)
- CeremonyRunner.get_ceremony_phases() returns correct phases
- CeremonyRunner.invoke() wraps ceremony_context
- CeremonyResult dataclass has state-change semantics
- Backward compat: CycleRunner.get_cycle_phases() falls back to CEREMONY_PHASES
"""
import sys
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Module loading: use _ensure_module pattern (S338 WORK-116 learning)
_modules_path = Path(__file__).parent.parent / ".claude" / "haios" / "modules"
_lib_path = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
if str(_modules_path) not in sys.path:
    sys.path.insert(0, str(_modules_path))
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))


def _mock_governance():
    """Create a mock GovernanceLayer for testing."""
    mock = MagicMock()
    mock.check_gate.return_value = MagicMock(allowed=True, reason="test")
    return mock


# =========================================================================
# Test 1: CeremonyRunner returns ceremony phases
# =========================================================================
class TestCeremonyRunnerGetPhases:
    def test_returns_known_ceremony_phases(self):
        from ceremony_runner import CeremonyRunner
        runner = CeremonyRunner(governance=_mock_governance())
        phases = runner.get_ceremony_phases("close-work-cycle")
        assert phases == ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"]

    def test_returns_checkpoint_phases(self):
        from ceremony_runner import CeremonyRunner
        runner = CeremonyRunner(governance=_mock_governance())
        phases = runner.get_ceremony_phases("checkpoint-cycle")
        assert phases == ["SCAFFOLD", "FILL", "VERIFY", "CAPTURE", "COMMIT"]


# =========================================================================
# Test 2: CeremonyRunner returns empty for unknown ceremony
# =========================================================================
class TestCeremonyRunnerUnknown:
    def test_unknown_returns_empty(self):
        from ceremony_runner import CeremonyRunner
        runner = CeremonyRunner(governance=_mock_governance())
        assert runner.get_ceremony_phases("nonexistent") == []

    def test_lifecycle_id_returns_empty(self):
        from ceremony_runner import CeremonyRunner
        runner = CeremonyRunner(governance=_mock_governance())
        # Lifecycle IDs should NOT be in CEREMONY_PHASES
        assert runner.get_ceremony_phases("implementation-cycle") == []


# =========================================================================
# Test 3: CEREMONY_PHASES excludes lifecycles
# =========================================================================
class TestCeremonyPhasesExcludeLifecycles:
    def test_no_lifecycle_entries(self):
        from ceremony_runner import CEREMONY_PHASES
        lifecycle_names = [
            "implementation-cycle",
            "investigation-cycle",
            "plan-authoring-cycle",
        ]
        for name in lifecycle_names:
            assert name not in CEREMONY_PHASES, f"{name} should not be in CEREMONY_PHASES"


# =========================================================================
# Test 4: CycleRunner still returns lifecycle phases (backward compat)
# =========================================================================
class TestCycleRunnerBackwardCompat:
    def test_lifecycle_phases_still_work(self):
        from cycle_runner import CycleRunner
        runner = CycleRunner(governance=_mock_governance())
        phases = runner.get_cycle_phases("implementation-cycle")
        assert phases == ["PLAN", "DO", "CHECK", "DONE", "CHAIN"]

    def test_investigation_phases_still_work(self):
        from cycle_runner import CycleRunner
        runner = CycleRunner(governance=_mock_governance())
        phases = runner.get_cycle_phases("investigation-cycle")
        assert phases == ["EXPLORE", "HYPOTHESIZE", "VALIDATE", "CONCLUDE", "CHAIN"]


# =========================================================================
# Test 5: CycleRunner no longer has ceremony phases in CYCLE_PHASES
# =========================================================================
class TestCyclePhasesExcludeCeremonies:
    def test_no_ceremony_entries_in_cycle_phases(self):
        from cycle_runner import CYCLE_PHASES
        ceremony_names = [
            "close-work-cycle",
            "checkpoint-cycle",
            "work-creation-cycle",
            "observation-triage-cycle",
        ]
        for name in ceremony_names:
            assert name not in CYCLE_PHASES, f"{name} should not be in CYCLE_PHASES"


# =========================================================================
# Test 6: CeremonyResult has state-change semantics
# =========================================================================
class TestCeremonyResult:
    def test_dataclass_fields(self):
        from ceremony_runner import CeremonyResult
        result = CeremonyResult(
            ceremony_id="close-work",
            work_id="WORK-118",
            side_effects=["status_change"],
        )
        assert result.ceremony_id == "close-work"
        assert result.work_id == "WORK-118"
        assert len(result.side_effects) == 1
        assert result.status == "success"

    def test_default_side_effects_empty(self):
        from ceremony_runner import CeremonyResult
        result = CeremonyResult(ceremony_id="test", work_id="WORK-001")
        assert result.side_effects == []
        assert result.status == "success"


# =========================================================================
# Test 7: CeremonyRunner.invoke wraps ceremony_context
# =========================================================================
class TestCeremonyRunnerInvoke:
    def test_invoke_uses_ceremony_context(self, monkeypatch):
        contexts_entered = []

        @contextmanager
        def mock_ceremony_context(name):
            from governance_layer import CeremonyContext
            ctx = CeremonyContext(ceremony_name=name)
            contexts_entered.append(name)
            yield ctx

        import ceremony_runner
        monkeypatch.setattr(ceremony_runner, "ceremony_context", mock_ceremony_context)

        runner = ceremony_runner.CeremonyRunner(governance=_mock_governance())
        result = runner.invoke("close-work", work_id="WORK-118")

        assert "close-work" in contexts_entered
        assert result.ceremony_id == "close-work"
        assert result.work_id == "WORK-118"
        assert result.status == "success"


# =========================================================================
# Test 8: Backward compat — get_cycle_phases falls back to CEREMONY_PHASES
# =========================================================================
class TestCycleRunnerFallback:
    def test_ceremony_id_resolved_via_fallback(self):
        from cycle_runner import CycleRunner
        runner = CycleRunner(governance=_mock_governance())
        # close-work-cycle is not in CYCLE_PHASES, but should resolve via fallback
        phases = runner.get_cycle_phases("close-work-cycle")
        assert len(phases) > 0, "Ceremony phases should resolve via fallback"
        assert phases == ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"]
