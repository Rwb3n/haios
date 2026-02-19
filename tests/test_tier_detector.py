# generated: 2026-02-19
"""
Tests for tier_detector.py — Governance Tier Detection (WORK-167).

Covers all 4 tiers (trivial/small/standard/architectural) plus edge cases
for missing fields, malformed YAML, empty lists, and boundary conditions.

Predicate spec: REQ-LIFECYCLE-005 (functional_requirements.md).
Pattern: session_end_actions.py (fail-permissive, _default_project_root).
"""
import sys
from pathlib import Path

import pytest

# Add lib/ to path for direct import
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))

from tier_detector import detect_tier


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def _write_work_md(
    tmp_path: Path,
    work_id: str,
    effort: str = None,
    source_files: list = None,
    traces_to: list = None,
    work_type: str = None,
) -> Path:
    """Write a minimal WORK.md with specified frontmatter fields.

    Maps parameter names to YAML frontmatter keys:
    - work_type -> type (YAML reserved word avoidance in Python)
    - source_files -> source_files
    - traces_to -> traces_to
    - effort -> effort
    """
    work_dir = tmp_path / "docs" / "work" / "active" / work_id
    work_dir.mkdir(parents=True, exist_ok=True)

    lines = ["---"]
    lines.append(f"id: {work_id}")
    if work_type is not None:
        lines.append(f"type: {work_type}")
    if effort is not None:
        lines.append(f"effort: {effort}")
    if source_files is not None:
        lines.append("source_files:")
        for sf in source_files:
            lines.append(f"  - {sf}")
    if traces_to is not None:
        lines.append("traces_to:")
        for tr in traces_to:
            lines.append(f"  - {tr}")
    lines.append("---")
    lines.append(f"# {work_id}")
    lines.append("")

    work_file = work_dir / "WORK.md"
    work_file.write_text("\n".join(lines), encoding="utf-8")
    return work_file


def _write_plan(tmp_path: Path, work_id: str) -> Path:
    """Write a minimal PLAN.md to make plan-existence check return True."""
    plan_dir = tmp_path / "docs" / "work" / "active" / work_id / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    plan_file = plan_dir / "PLAN.md"
    plan_file.write_text("---\nstatus: draft\n---\n# Plan\n", encoding="utf-8")
    return plan_file


# ---------------------------------------------------------------------------
# Test 1-5: Core tier classification
# ---------------------------------------------------------------------------

class TestTierClassification:
    """Tests for the four governance tiers."""

    def test_detect_tier_trivial(self, tmp_path):
        """effort=small, source_files<=2, no plan, no ADR, no type=design -> trivial"""
        _write_work_md(
            tmp_path, "WORK-001",
            effort="small",
            source_files=["a.py", "b.py"],
            traces_to=["REQ-CEREMONY-005"],
            work_type="implementation",
        )
        result = detect_tier("WORK-001", project_root=tmp_path)
        assert result == "trivial"

    def test_detect_tier_small(self, tmp_path):
        """effort=small, source_files<=3, no ADR, no type=design, plan exists -> small"""
        _write_work_md(
            tmp_path, "WORK-002",
            effort="small",
            source_files=["a.py", "b.py", "c.py"],
            traces_to=["REQ-CEREMONY-005"],
            work_type="implementation",
        )
        _write_plan(tmp_path, "WORK-002")
        result = detect_tier("WORK-002", project_root=tmp_path)
        assert result == "small"

    def test_detect_tier_standard(self, tmp_path):
        """effort=medium -> standard (default)"""
        _write_work_md(
            tmp_path, "WORK-003",
            effort="medium",
            source_files=["a.py", "b.py"],
            traces_to=[],
            work_type="implementation",
        )
        result = detect_tier("WORK-003", project_root=tmp_path)
        assert result == "standard"

    def test_detect_tier_architectural_design(self, tmp_path):
        """type=design -> architectural"""
        _write_work_md(
            tmp_path, "WORK-004",
            effort="small",
            source_files=["a.py"],
            traces_to=[],
            work_type="design",
        )
        result = detect_tier("WORK-004", project_root=tmp_path)
        assert result == "architectural"

    def test_detect_tier_architectural_adr(self, tmp_path):
        """ADR in traces_to -> architectural"""
        _write_work_md(
            tmp_path, "WORK-005",
            effort="small",
            source_files=["a.py"],
            traces_to=["ADR-045"],
            work_type="implementation",
        )
        result = detect_tier("WORK-005", project_root=tmp_path)
        assert result == "architectural"


# ---------------------------------------------------------------------------
# Test 6-9: Edge cases — missing/absent fields
# ---------------------------------------------------------------------------

class TestConservativeDefaults:
    """Tests for conservative safe defaults (REQ-LIFECYCLE-005 invariant)."""

    def test_detect_tier_missing_effort_defaults_standard(self, tmp_path):
        """Absent effort field -> standard (conservative safe default)"""
        _write_work_md(
            tmp_path, "WORK-006",
            effort=None,
            source_files=["a.py"],
            traces_to=[],
            work_type="implementation",
        )
        result = detect_tier("WORK-006", project_root=tmp_path)
        assert result == "standard"

    def test_detect_tier_missing_source_files_defaults_standard(self, tmp_path):
        """Absent source_files -> standard (conservative safe default)"""
        _write_work_md(
            tmp_path, "WORK-007",
            effort="small",
            source_files=None,
            traces_to=[],
            work_type="implementation",
        )
        result = detect_tier("WORK-007", project_root=tmp_path)
        assert result == "standard"

    def test_detect_tier_all_absent_defaults_standard(self, tmp_path):
        """All fields absent/empty -> standard (conservative, not trivial or architectural)"""
        _write_work_md(
            tmp_path, "WORK-008",
            effort=None,
            source_files=None,
            traces_to=None,
            work_type=None,
        )
        result = detect_tier("WORK-008", project_root=tmp_path)
        assert result == "standard"

    def test_detect_tier_nonexistent_work_returns_standard(self, tmp_path):
        """Missing WORK.md -> standard (fail-permissive)"""
        result = detect_tier("WORK-999", project_root=tmp_path)
        assert result == "standard"


# ---------------------------------------------------------------------------
# Test 10-12: Boundary conditions and error handling
# ---------------------------------------------------------------------------

class TestBoundaryConditions:
    """Tests for predicate boundaries and error paths."""

    def test_detect_tier_two_files_with_plan_returns_small(self, tmp_path):
        """effort=small, source_files=2, plan exists -> small (plan disqualifies trivial)"""
        _write_work_md(
            tmp_path, "WORK-010",
            effort="small",
            source_files=["a.py", "b.py"],
            traces_to=["REQ-CEREMONY-005"],
            work_type="implementation",
        )
        _write_plan(tmp_path, "WORK-010")
        result = detect_tier("WORK-010", project_root=tmp_path)
        assert result == "small"

    def test_detect_tier_malformed_yaml_returns_standard(self, tmp_path):
        """Malformed YAML frontmatter -> standard (fail-permissive)"""
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-011"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text(
            "---\neffort: : bad yaml\n---\n", encoding="utf-8"
        )
        result = detect_tier("WORK-011", project_root=tmp_path)
        assert result == "standard"

    def test_detect_tier_empty_source_files_returns_standard(self, tmp_path):
        """source_files=[] (empty list) -> standard (REQ-LIFECYCLE-005 invariant)"""
        _write_work_md(
            tmp_path, "WORK-012",
            effort="small",
            source_files=[],
            traces_to=[],
            work_type="implementation",
        )
        result = detect_tier("WORK-012", project_root=tmp_path)
        assert result == "standard"
