# generated: 2026-02-24
# Session 445: WORK-165 Ceremony Cards — Tests
"""Tests for ceremony_cards.py (REQ-DISCOVER-003).

Mirrors test_agent_cards.py pattern for ceremony skill discovery.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
from ceremony_cards import CeremonyCard, list_ceremonies, get_ceremony, filter_ceremonies, SKILLS_DIR


# Test 1: CeremonyCard minimal construction
def test_minimal_construction():
    card = CeremonyCard(name="test-ceremony", description="A test", category="closure")
    assert card.name == "test-ceremony"
    assert card.description == "A test"
    assert card.category == "closure"


# Test 2: CeremonyCard optional fields have defaults
def test_optional_fields_have_defaults():
    card = CeremonyCard(name="test-ceremony", description="A test", category="closure")
    assert card.input_contract == []
    assert card.output_contract == []
    assert card.side_effects == []


# Test 3: list_ceremonies returns list
def test_list_ceremonies_returns_list():
    result = list_ceremonies()
    assert isinstance(result, list)


# Test 4: list_ceremonies returns CeremonyCard instances
def test_list_ceremonies_returns_ceremony_cards():
    result = list_ceremonies()
    for item in result:
        assert isinstance(item, CeremonyCard)


# Test 5: list_ceremonies ceremony count (>= 9 to tolerate future additions — critique A1)
def test_ceremony_count():
    result = list_ceremonies()
    assert len(result) >= 9


# Test 6: list_ceremonies excludes non-ceremony skills
def test_excludes_non_ceremony_skills():
    result = list_ceremonies()
    names = {c.name for c in result}
    # Only check skills confirmed as type: lifecycle (retro-cycle is type: ceremony)
    non_ceremony = {"implementation-cycle", "plan-authoring-cycle", "survey-cycle"}
    assert names.isdisjoint(non_ceremony)


# Test 7: known ceremonies present
def test_known_ceremonies_present():
    result = list_ceremonies()
    names = {c.name for c in result}
    expected = {
        "open-epoch-ceremony",
        "close-epoch-ceremony",
        "close-arc-ceremony",
        "close-chapter-ceremony",
        "close-work-cycle",
    }
    assert expected.issubset(names)


# Test 8: get_ceremony known name
def test_get_ceremony_known_name():
    result = get_ceremony("open-epoch-ceremony")
    assert result is not None
    assert result.name == "open-epoch-ceremony"


# Test 9: get_ceremony unknown name returns None
def test_get_ceremony_unknown_returns_none():
    result = get_ceremony("nonexistent-ceremony")
    assert result is None


# Test 10: filter_ceremonies by category
def test_filter_by_category_closure():
    result = filter_ceremonies(category="closure")
    names = {c.name for c in result}
    assert "open-epoch-ceremony" in names
    assert "close-epoch-ceremony" in names
    assert "close-arc-ceremony" in names


# Test 11: filter_ceremonies no filters returns all (>= 9 — critique A1)
def test_filter_no_args_returns_all():
    result = filter_ceremonies()
    assert len(result) >= 9


# Test 12: SKILLS_DIR constant
def test_skills_dir_exists():
    assert SKILLS_DIR.exists()
    # Verify it contains subdirectories with SKILL.md files
    has_skill_files = any(
        (d / "SKILL.md").exists()
        for d in SKILLS_DIR.iterdir()
        if d.is_dir()
    )
    assert has_skill_files


# Test 13: filter_ceremonies multi-category (critique A2)
def test_filter_by_secondary_category():
    result = filter_ceremonies(category="queue")
    names = {c.name for c in result}
    assert "close-work-cycle" in names
