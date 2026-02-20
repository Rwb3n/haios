# generated: 2026-02-20
"""
Tests for critique_injector.py — Critique-as-Hook (WORK-169).

Covers all 4 tiers (trivial/small/standard/architectural), transition
detection (inhale-to-exhale), fallback behavior, and regression guard.

Pattern: test_tier_detector.py (sys.path + monkeypatch).
"""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add lib/ to path for direct import
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))

import tier_detector
import critique_injector
from critique_injector import compute_critique_injection


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _write_slim_json(tmp_path: Path, phase: str = None, work_id: str = None) -> Path:
    """Write a minimal haios-status-slim.json with session_state."""
    slim_dir = tmp_path / ".claude"
    slim_dir.mkdir(parents=True, exist_ok=True)
    slim_file = slim_dir / "haios-status-slim.json"
    data = {
        "session_state": {
            "active_cycle": "implementation-cycle",
            "current_phase": phase,
            "work_id": work_id,
            "entered_at": None,
            "active_queue": None,
            "phase_history": [],
        }
    }
    slim_file.write_text(json.dumps(data), encoding="utf-8")
    return tmp_path


def _write_work_md(tmp_path: Path, work_id: str, effort: str = "medium",
                   source_files: list = None, work_type: str = "implementation") -> Path:
    """Write minimal WORK.md for tier detection."""
    work_dir = tmp_path / "docs" / "work" / "active" / work_id
    work_dir.mkdir(parents=True, exist_ok=True)
    sf_yaml = ""
    if source_files:
        sf_yaml = "source_files:\n" + "\n".join(f"  - {f}" for f in source_files)
    else:
        sf_yaml = "source_files: []"
    content = f"""---
id: {work_id}
type: {work_type}
effort: {effort}
{sf_yaml}
traces_to: []
---
# {work_id}
"""
    (work_dir / "WORK.md").write_text(content, encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# Test 1: Trivial tier produces no injection
# ---------------------------------------------------------------------------


def test_trivial_tier_no_injection(tmp_path):
    """Trivial work items get no critique injection."""
    root = _write_slim_json(tmp_path, phase="PLAN", work_id="WORK-999")
    # Trivial: effort=small, source_files<=2, no plan, no ADR
    _write_work_md(root, "WORK-999", effort="small",
                   source_files=["file1.py"])
    result = compute_critique_injection("implementation-cycle", project_root=root)
    assert result is None


# ---------------------------------------------------------------------------
# Test 2: Small tier produces checklist injection
# ---------------------------------------------------------------------------


def test_small_tier_checklist_injection(tmp_path):
    """Small work items get checklist injected as additionalContext."""
    root = _write_slim_json(tmp_path, phase="PLAN", work_id="WORK-100")
    # Small: effort=small, source_files<=3, no ADR
    _write_work_md(root, "WORK-100", effort="small",
                   source_files=["f1.py", "f2.py", "f3.py"])
    # Create a plan file so it's not trivial
    plan_dir = root / "docs" / "work" / "active" / "WORK-100" / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / "PLAN.md").write_text("---\nstatus: draft\n---\n# Plan", encoding="utf-8")

    result = compute_critique_injection("implementation-cycle", project_root=root)
    assert result is not None
    assert "verify" in result.lower() or "checklist" in result.lower() or "CHECKPOINT" in result


# ---------------------------------------------------------------------------
# Test 3: Standard tier produces full subagent instruction
# ---------------------------------------------------------------------------


def test_standard_tier_full_subagent(tmp_path):
    """Standard work items get instruction to invoke critique-agent subagent."""
    root = _write_slim_json(tmp_path, phase="PLAN", work_id="WORK-100")
    # Standard: effort=medium (default)
    _write_work_md(root, "WORK-100", effort="medium",
                   source_files=["f1.py", "f2.py", "f3.py", "f4.py"])
    result = compute_critique_injection("implementation-cycle", project_root=root)
    assert result is not None
    assert "critique-agent" in result


# ---------------------------------------------------------------------------
# Test 4: Architectural tier produces operator dialogue instruction
# ---------------------------------------------------------------------------


def test_architectural_tier_operator_dialogue(tmp_path):
    """Architectural work items get critique-agent + operator confirmation."""
    root = _write_slim_json(tmp_path, phase="PLAN", work_id="WORK-100")
    _write_work_md(root, "WORK-100", effort="medium", work_type="design",
                   source_files=["f1.py"])
    result = compute_critique_injection("implementation-cycle", project_root=root)
    assert result is not None
    assert "critique-agent" in result
    assert "operator" in result.lower() or "AskUserQuestion" in result


# ---------------------------------------------------------------------------
# Test 5: Non-transition skill produces no injection
# ---------------------------------------------------------------------------


def test_non_transition_skill_no_injection(tmp_path):
    """Skills not in TRANSITION_SKILLS produce no injection."""
    root = _write_slim_json(tmp_path, phase="DO", work_id="WORK-100")
    result = compute_critique_injection("retro-cycle", project_root=root)
    assert result is None


# ---------------------------------------------------------------------------
# Test 6: EXPLORE-to-HYPOTHESIZE transition (investigation)
# ---------------------------------------------------------------------------


def test_explore_to_hypothesize_transition(tmp_path):
    """Investigation cycle EXPLORE phase triggers critique injection."""
    root = _write_slim_json(tmp_path, phase="EXPLORE", work_id="WORK-100")
    # Standard tier (medium effort)
    _write_work_md(root, "WORK-100", effort="medium",
                   source_files=["f1.py", "f2.py", "f3.py", "f4.py"])
    result = compute_critique_injection("investigation-cycle", project_root=root)
    assert result is not None


# ---------------------------------------------------------------------------
# Test 7: Unknown work_id defaults to standard tier
# ---------------------------------------------------------------------------


def test_unknown_work_id_defaults_standard(tmp_path):
    """Unresolvable work_id defaults to standard tier, not silent skip."""
    root = _write_slim_json(tmp_path, phase="PLAN", work_id="unknown")
    # No WORK.md for "unknown" -> detect_tier returns "standard"
    result = compute_critique_injection("implementation-cycle", project_root=root)
    assert result is not None  # Standard tier = full subagent
    assert "critique-agent" in result


# ---------------------------------------------------------------------------
# Test 8: Unknown phase defaults to no injection (fail-permissive)
# ---------------------------------------------------------------------------


def test_unknown_phase_no_injection(tmp_path):
    """Unresolvable phase produces no injection (fail-permissive)."""
    root = _write_slim_json(tmp_path, phase=None, work_id="WORK-100")
    result = compute_critique_injection("implementation-cycle", project_root=root)
    assert result is None


# ---------------------------------------------------------------------------
# Test 9: detect_tier exception handled fail-permissive
# ---------------------------------------------------------------------------


def test_detect_tier_exception_defaults_standard(tmp_path, monkeypatch):
    """detect_tier() exception produces standard injection + warning event."""
    root = _write_slim_json(tmp_path, phase="PLAN", work_id="WORK-100")

    def _raise(*args, **kwargs):
        raise RuntimeError("test error")

    monkeypatch.setattr(tier_detector, "detect_tier", _raise)
    result = compute_critique_injection("implementation-cycle", project_root=root)
    # Falls back to standard on exception
    assert result is not None


# ---------------------------------------------------------------------------
# Test 10: Exhale phase does not trigger injection
# ---------------------------------------------------------------------------


def test_exhale_phase_no_injection(tmp_path):
    """DO phase (exhale) does not trigger critique injection."""
    root = _write_slim_json(tmp_path, phase="DO", work_id="WORK-100")
    _write_work_md(root, "WORK-100", effort="medium",
                   source_files=["f1.py", "f2.py", "f3.py", "f4.py"])
    result = compute_critique_injection("implementation-cycle", project_root=root)
    assert result is None
