# generated: 2026-01-21
# System Auto: last updated on: 2026-01-21T23:05:34
"""
Tests for the Identity Loader module.

WORK-007: Implement Identity Loader for Configuration Arc
CH-004: Identity Loader chapter

Tests extraction of identity context from manifesto files using the
config-driven extraction DSL from loader.py (WORK-005).
"""
import pytest
from pathlib import Path
import sys

# Add the haios lib directory to path for imports
haios_lib = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
sys.path.insert(0, str(haios_lib))

from identity_loader import IdentityLoader


# =============================================================================
# Test 1: Config Loading
# =============================================================================
def test_identity_loader_loads_config():
    """IdentityLoader loads config from identity.yaml."""
    loader = IdentityLoader()
    assert loader.config is not None
    assert "extract" in loader.config


# =============================================================================
# Test 2: Mission Extraction
# =============================================================================
def test_extracts_mission_from_l0():
    """Extracts prime directive blockquote from L0-telos.md."""
    loader = IdentityLoader()
    result = loader.extract()
    assert "mission" in result
    # Mission should contain key phrases from the prime directive
    mission = result["mission"].lower()
    assert "cognitive load" in mission or "success" in mission or len(result["mission"]) > 20


# =============================================================================
# Test 3: Principles Extraction
# =============================================================================
def test_extracts_principles_from_l3():
    """Extracts core behavioral principles as list."""
    loader = IdentityLoader()
    result = loader.extract()
    assert "principles" in result
    # Should have 7 principles per L3-requirements.md
    assert isinstance(result["principles"], list)
    assert len(result["principles"]) >= 1
    # Check for known principle names
    principles_text = " ".join(str(p) for p in result["principles"]).lower()
    assert "certainty" in principles_text or "evidence" in principles_text


# =============================================================================
# Test 4: Output Under 100 Lines
# =============================================================================
def test_output_under_100_lines():
    """Output is compact: < 100 lines per R4."""
    loader = IdentityLoader()
    output = loader.load()
    line_count = len(output.strip().split('\n'))
    assert line_count < 100, f"Output too long: {line_count} lines"


# =============================================================================
# Test 5: Constraints Extraction
# =============================================================================
def test_extracts_constraints_from_l1():
    """Extracts known constraints from L1-principal.md."""
    loader = IdentityLoader()
    result = loader.extract()
    assert "constraints" in result
    # Should have multiple constraints
    assert isinstance(result["constraints"], list)
    assert len(result["constraints"]) >= 1
    # Check for known constraint
    constraints_text = " ".join(str(c) for c in result["constraints"]).lower()
    assert "burnout" in constraints_text or "time" in constraints_text


# =============================================================================
# Test 6: Companion Relationship Extraction
# =============================================================================
def test_extracts_companion_relationship():
    """Extracts companion relationship items from L0-telos.md."""
    loader = IdentityLoader()
    result = loader.extract()
    assert "companion" in result
    assert isinstance(result["companion"], list)
    # Should have 4 relationship principles
    assert len(result["companion"]) >= 1


# =============================================================================
# Test 7: Full Output Format
# =============================================================================
def test_output_contains_all_sections():
    """Output contains all expected sections."""
    loader = IdentityLoader()
    output = loader.load()

    # Check for section headers or content indicators
    assert "IDENTITY" in output
    assert "Mission" in output
    assert "Principles" in output
    assert "Constraints" in output


# =============================================================================
# Test 8: Config Path Override
# =============================================================================
def test_custom_config_path():
    """IdentityLoader accepts custom config path."""
    # Use the default config path explicitly
    config_path = Path(__file__).parent.parent / ".claude" / "haios" / "config" / "loaders" / "identity.yaml"
    loader = IdentityLoader(config_path=config_path)
    assert loader.config is not None
    result = loader.load()
    assert len(result) > 0


# =============================================================================
# Test 9: Missing Config Raises Error
# =============================================================================
def test_missing_config_raises_error():
    """FileNotFoundError raised for missing config."""
    with pytest.raises(FileNotFoundError):
        IdentityLoader(config_path=Path("/nonexistent/config.yaml"))
