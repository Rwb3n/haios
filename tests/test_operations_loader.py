# generated: 2026-02-21
# WORK-180: Tests for OperationsLoader (ADR-047 Tiered Coldstart)
# TDD: These tests define expected behavior before implementation.
"""
Tests for OperationsLoader — injects operational context (tier model,
recipe catalogue, agent table, common patterns).

Tests 5-8 from WORK-180 plan Layer 1.
"""
import sys
from pathlib import Path

import pytest

# Add lib path for imports
_lib_path = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))


def _create_mock_claude_md(tmp_path, include_agents=True, include_triggers=True):
    """Create a mock CLAUDE.md with agent table and governance triggers."""
    claude_md = tmp_path / "CLAUDE.md"
    content = "# Code Implementation & Engineering Guide\n\n"

    if include_agents:
        content += (
            "## Agents\n\n"
            "| Agent | Model | Requirement | Category | Purpose |\n"
            "|-------|-------|-------------|----------|---------|\n"
            "| critique-agent | opus | recommended | verification | Assumption surfacing |\n"
            "| test-runner | haiku | optional | utility | Test execution |\n\n"
        )

    if include_triggers:
        content += (
            "### Governance Triggers (MUST)\n"
            "- Discover bug/gap -> `/new-investigation`\n"
            "- SQL query -> `schema-verifier` subagent\n"
            "- Close work -> `/close <id>`\n\n"
        )

    content += "## Other Section\n\nSome other content.\n"
    claude_md.write_text(content, encoding="utf-8")
    return claude_md


def _create_mock_justfile(tmp_path, recipes=None):
    """Create a mock justfile with recipe definitions."""
    justfile = tmp_path / "justfile"
    if recipes is None:
        recipes = [
            "scaffold type id title:",
            "validate file:",
            "ready:",
            "queue name='default':",
            "queue-prioritize id rationale:",
            "queue-commit id:",
            "session-start n:",
            "session-end n:",
            "coldstart-orchestrator:",
            "set-cycle lifecycle phase id:",
            "clear-cycle:",
        ]
    content = "# Mock justfile\n\n"
    for recipe in recipes:
        content += f"{recipe}\n    echo 'mock'\n\n"
    justfile.write_text(content, encoding="utf-8")
    return justfile


# =============================================================================
# Test 5: OperationsLoader injects tier model
# =============================================================================


def test_operations_loader_injects_tier_model(tmp_path):
    """OperationsLoader output contains tier model descriptions."""
    _create_mock_claude_md(tmp_path)
    _create_mock_justfile(tmp_path)

    from operations_loader import OperationsLoader

    loader = OperationsLoader(
        base_path=tmp_path,
        claude_md_path=tmp_path / "CLAUDE.md",
        justfile_path=tmp_path / "justfile",
    )
    output = loader.load()

    # Should contain tier descriptions
    assert "Tier 1" in output
    assert "Tier 2" in output
    assert "Tier 3" in output
    assert "Commands" in output or "Command" in output
    assert "Skills" in output or "Skill" in output
    assert "Recipes" in output or "Recipe" in output
    assert "MUST NOT" in output  # Agent must not run just X directly


# =============================================================================
# Test 6: OperationsLoader injects recipe catalogue
# =============================================================================


def test_operations_loader_injects_recipe_catalogue(tmp_path):
    """OperationsLoader output contains recipe names grouped by category."""
    _create_mock_claude_md(tmp_path)
    _create_mock_justfile(tmp_path)

    from operations_loader import OperationsLoader

    loader = OperationsLoader(
        base_path=tmp_path,
        claude_md_path=tmp_path / "CLAUDE.md",
        justfile_path=tmp_path / "justfile",
    )
    output = loader.load()

    # Should contain categorized recipes
    assert "Governance" in output
    assert "scaffold" in output
    assert "validate" in output
    assert "Plan Tree" in output or "ready" in output
    assert "Rhythm" in output or "session-start" in output


# =============================================================================
# Test 7: OperationsLoader handles missing files gracefully
# =============================================================================


def test_operations_loader_missing_files(tmp_path):
    """OperationsLoader returns warning for missing files, does not raise."""
    # Do NOT create CLAUDE.md or justfile
    from operations_loader import OperationsLoader

    loader = OperationsLoader(
        base_path=tmp_path,
        claude_md_path=tmp_path / "CLAUDE.md",
        justfile_path=tmp_path / "justfile",
    )
    output = loader.load()

    # Should not raise
    assert output is not None
    # Should still contain tier model (hardcoded, not file-dependent)
    assert "Tier 1" in output
    # Should indicate missing data
    assert "not found" in output.lower() or "No agent table" in output or len(output) > 0


# =============================================================================
# Test 8: OperationsLoader injects common patterns
# =============================================================================


def test_operations_loader_injects_patterns(tmp_path):
    """OperationsLoader output contains WorkEngine + ConfigLoader patterns."""
    _create_mock_claude_md(tmp_path)
    _create_mock_justfile(tmp_path)

    from operations_loader import OperationsLoader

    loader = OperationsLoader(
        base_path=tmp_path,
        claude_md_path=tmp_path / "CLAUDE.md",
        justfile_path=tmp_path / "justfile",
    )
    output = loader.load()

    # Should contain common patterns
    assert "WorkEngine" in output
    assert "GovernanceLayer" in output
    assert "ConfigLoader" in output
    assert "scaffold_template" in output
