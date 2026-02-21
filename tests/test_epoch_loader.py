# generated: 2026-02-21
# WORK-180: Tests for EpochLoader (ADR-047 Tiered Coldstart)
# TDD: These tests define expected behavior before implementation.
"""
Tests for EpochLoader — extracts epoch context from EPOCH.md + ARC.md files.

Tests 1-4 from WORK-180 plan Layer 1.
"""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

# Add lib path for imports
_lib_path = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))


def _create_mock_epoch(tmp_path, epoch_name="Agent UX", epoch_status="Active"):
    """Create a mock EPOCH.md file with realistic structure."""
    epoch_dir = tmp_path / ".claude" / "haios" / "epochs" / "E2_8"
    epoch_dir.mkdir(parents=True, exist_ok=True)
    epoch_file = epoch_dir / "EPOCH.md"
    epoch_file.write_text(
        f"---\nstatus: active\n---\n"
        f"# Epoch 2.8: {epoch_name}\n\n"
        f"## L4 Object Definition\n\n"
        f"**Epoch ID:** E2.8\n"
        f"**Name:** {epoch_name}\n"
        f"**Status:** {epoch_status}\n\n"
        f"---\n\n"
        f"## Exit Criteria\n\n"
        f"- [x] Confirmed bugs resolved\n"
        f"- [ ] Governance overhead reduced\n"
        f"- [ ] Lightweight coldstart variant exists\n\n"
        f"---\n",
        encoding="utf-8",
    )
    return epoch_file


def _create_mock_arc(tmp_path, arc_name, chapters=None):
    """Create a mock ARC.md file with chapter table."""
    arcs_dir = tmp_path / ".claude" / "haios" / "epochs" / "E2_8" / "arcs" / arc_name
    arcs_dir.mkdir(parents=True, exist_ok=True)
    arc_file = arcs_dir / "ARC.md"

    chapter_rows = ""
    if chapters:
        for ch in chapters:
            chapter_rows += f"| {ch['id']} | {ch['title']} | {ch.get('work', 'New')} | {ch.get('reqs', 'REQ-001')} | None | {ch['status']} |\n"

    arc_file.write_text(
        f"# Arc: {arc_name}\n\n"
        f"## Chapters\n\n"
        f"| CH-ID | Title | Work Items | Requirements | Dependencies | Status |\n"
        f"|-------|-------|------------|--------------|--------------|--------|\n"
        f"{chapter_rows}\n"
        f"---\n",
        encoding="utf-8",
    )
    return arc_file


def _create_mock_haios_yaml(tmp_path, active_arcs=None):
    """Create a mock haios.yaml pointing to epoch files in tmp_path."""
    config_dir = tmp_path / ".claude" / "haios" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    haios_yaml = config_dir / "haios.yaml"

    if active_arcs is None:
        active_arcs = ["call", "query"]

    config = {
        "epoch": {
            "current": "E2.8",
            "epoch_file": ".claude/haios/epochs/E2_8/EPOCH.md",
            "arcs_dir": ".claude/haios/epochs/E2_8/arcs",
            "active_arcs": active_arcs,
        }
    }
    haios_yaml.write_text(yaml.dump(config), encoding="utf-8")
    return haios_yaml


# =============================================================================
# Test 1: EpochLoader extracts epoch context
# =============================================================================


def test_epoch_loader_extracts_status_and_arcs(tmp_path):
    """EpochLoader extracts epoch name, status, arc names, chapter statuses."""
    # Setup: mock EPOCH.md + 2 ARC.md files + haios.yaml
    _create_mock_epoch(tmp_path, epoch_name="Agent UX", epoch_status="Active")
    _create_mock_arc(tmp_path, "call", chapters=[
        {"id": "CH-058", "title": "ProportionalGovernance", "status": "Complete"},
        {"id": "CH-059", "title": "CeremonyAutomation", "status": "In Progress"},
    ])
    _create_mock_arc(tmp_path, "query", chapters=[
        {"id": "CH-062", "title": "ProgressiveContracts", "status": "Planning"},
    ])
    haios_yaml = _create_mock_haios_yaml(tmp_path, active_arcs=["call", "query"])

    from epoch_loader import EpochLoader

    loader = EpochLoader(haios_config_path=haios_yaml, base_path=tmp_path)
    output = loader.load()

    # Assertions
    assert "Agent UX" in output
    assert "Active" in output
    assert "call" in output
    assert "query" in output
    assert "CH-058" in output
    assert "CH-059" in output
    assert "CH-062" in output
    assert "Complete" in output
    assert "In Progress" in output
    assert "Planning" in output


# =============================================================================
# Test 2: EpochLoader handles missing EPOCH.md gracefully
# =============================================================================


def test_epoch_loader_missing_epoch_file(tmp_path):
    """EpochLoader returns warning when EPOCH.md is missing, does not raise."""
    # Setup: haios.yaml points to nonexistent EPOCH.md
    haios_yaml = _create_mock_haios_yaml(tmp_path)
    # Do NOT create EPOCH.md

    from epoch_loader import EpochLoader

    loader = EpochLoader(haios_config_path=haios_yaml, base_path=tmp_path)
    output = loader.load()

    # Should not raise, should contain warning
    assert "error" in output.lower() or "not found" in output.lower()
    assert "EPOCH" in output


# =============================================================================
# Test 3: EpochLoader handles missing ARC.md gracefully
# =============================================================================


def test_epoch_loader_missing_arc_file(tmp_path):
    """EpochLoader includes available arcs and warns about missing ones."""
    # Setup: EPOCH.md exists, call ARC.md exists, query ARC.md missing
    _create_mock_epoch(tmp_path)
    _create_mock_arc(tmp_path, "call", chapters=[
        {"id": "CH-058", "title": "ProportionalGovernance", "status": "Complete"},
    ])
    # Do NOT create query ARC.md
    haios_yaml = _create_mock_haios_yaml(tmp_path, active_arcs=["call", "query"])

    from epoch_loader import EpochLoader

    loader = EpochLoader(haios_config_path=haios_yaml, base_path=tmp_path)
    output = loader.load()

    # Should include call arc data
    assert "call" in output
    assert "CH-058" in output

    # Should warn about missing query arc
    assert "query" in output
    assert "not found" in output.lower() or "warning" in output.lower() or "Warning" in output


# =============================================================================
# Test 4: EpochLoader extracts exit criteria
# =============================================================================


def test_epoch_loader_extracts_exit_criteria(tmp_path):
    """EpochLoader output contains checked/unchecked exit criteria from EPOCH.md."""
    _create_mock_epoch(tmp_path)
    haios_yaml = _create_mock_haios_yaml(tmp_path, active_arcs=[])

    from epoch_loader import EpochLoader

    loader = EpochLoader(haios_config_path=haios_yaml, base_path=tmp_path)
    output = loader.load()

    # Should contain exit criteria
    assert "Exit Criteria" in output
    assert "[x]" in output  # Checked item
    assert "[ ]" in output  # Unchecked item
    assert "Confirmed bugs resolved" in output
    assert "Governance overhead reduced" in output
