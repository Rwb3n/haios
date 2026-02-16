"""Tests for ceremony skill contract retrofit.

WORK-112: Retrofit Ceremony Skills with Contracts
Chapter: CH-011 (CeremonyContracts)

Verifies that ceremony skills have YAML frontmatter contracts
and that the ceremony registry reflects contract coverage.
WORK-148: 4 feedback stub skills removed (arc-review, chapter-review,
epoch-review, requirements-review). Registry entries retained with has_skill: false.
"""

import sys
from pathlib import Path

import pytest

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))

from ceremony_contracts import CeremonyContract, load_ceremony_registry
from helpers import load_frontmatter

# --- Constants ---

SKILLS_DIR = Path(".claude/skills")

# 12 existing skills that should be retrofitted with contract frontmatter
# WORK-145: observation-capture-cycle removed (deprecated, replaced by retro-cycle)
EXISTING_CEREMONY_SKILLS = [
    "queue-intake",
    "queue-prioritize",
    "queue-commit",
    "queue-unpark",
    "close-work-cycle",
    "close-chapter-ceremony",
    "close-arc-ceremony",
    "close-epoch-ceremony",
    "retro-cycle",
    "observation-triage-cycle",
    "checkpoint-cycle",
    "session-start-ceremony",   # De-stubbed by WORK-120 (CH-014)
    "session-end-ceremony",     # De-stubbed by WORK-120 (CH-014)
    "memory-commit-ceremony",   # De-stubbed by WORK-133 (CH-016)
]

# Remaining stub skills (WORK-112)
# WORK-148: 4 feedback stubs removed (arc-review, chapter-review, epoch-review, requirements-review)
STUB_CEREMONY_SKILLS = [
    "spawn-work-ceremony",
]

ALL_CEREMONY_SKILLS = EXISTING_CEREMONY_SKILLS + STUB_CEREMONY_SKILLS

# Required contract fields in YAML frontmatter
CONTRACT_FIELDS = ["category", "input_contract", "output_contract", "side_effects"]



class TestExistingSkillsRetrofitted:
    """Test 1: All 11 existing ceremony skills have contract fields in frontmatter."""

    @pytest.mark.parametrize("skill_name", EXISTING_CEREMONY_SKILLS)
    def test_skill_has_contract_frontmatter(self, skill_name):
        """Each existing ceremony skill must have category, input_contract,
        output_contract, and side_effects in its YAML frontmatter."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Skill file not found: {skill_path}"

        data = load_frontmatter(skill_path)

        for field in CONTRACT_FIELDS:
            assert field in data, (
                f"Skill '{skill_name}' missing contract field '{field}' in frontmatter"
            )

    @pytest.mark.parametrize("skill_name", EXISTING_CEREMONY_SKILLS)
    def test_skill_category_valid(self, skill_name):
        """Category must be a valid ceremony category string or list."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        data = load_frontmatter(skill_path)

        valid_categories = {"queue", "session", "closure", "feedback", "memory", "spawn"}
        category = data["category"]
        if isinstance(category, list):
            for cat in category:
                assert cat in valid_categories, (
                    f"Skill '{skill_name}' has invalid category '{cat}'"
                )
        else:
            assert category in valid_categories, (
                f"Skill '{skill_name}' has invalid category '{category}'"
            )


class TestStubSkillsCreated:
    """Test 2: Remaining stub ceremony skills exist and have contract fields."""

    @pytest.mark.parametrize("skill_name", STUB_CEREMONY_SKILLS)
    def test_stub_skill_exists(self, skill_name):
        """Each stub ceremony skill file must exist."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Stub skill file not found: {skill_path}"

    @pytest.mark.parametrize("skill_name", STUB_CEREMONY_SKILLS)
    def test_stub_has_contract_frontmatter(self, skill_name):
        """Each stub ceremony skill must have all contract fields."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        data = load_frontmatter(skill_path)

        for field in CONTRACT_FIELDS:
            assert field in data, (
                f"Stub '{skill_name}' missing contract field '{field}' in frontmatter"
            )

    @pytest.mark.parametrize("skill_name", STUB_CEREMONY_SKILLS)
    def test_stub_category_valid(self, skill_name):
        """Stub category must be a valid ceremony category."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        data = load_frontmatter(skill_path)

        valid_categories = {"queue", "session", "closure", "feedback", "memory", "spawn"}
        category = data["category"]
        if isinstance(category, list):
            for cat in category:
                assert cat in valid_categories
        else:
            assert category in valid_categories


class TestRegistryContractCoverage:
    """Test 3: Registry shows 20/20 has_contract: true."""

    def test_all_ceremonies_have_contracts(self):
        """All 20 ceremonies in registry must have has_contract: true."""
        registry = load_ceremony_registry()
        missing = [c.name for c in registry.ceremonies if not c.has_contract]
        assert len(missing) == 0, (
            f"Ceremonies missing contracts: {missing}"
        )

    def test_registry_count_still_20(self):
        """Registry must still contain exactly 20 ceremonies."""
        registry = load_ceremony_registry()
        assert len(registry.ceremonies) == 20

    def test_new_stubs_have_skill_entries(self):
        """The remaining stub ceremonies must have has_skill: true and skill set."""
        registry = load_ceremony_registry()
        # WORK-148: 4 feedback stubs removed; only these remain as has_skill: true stubs
        stub_ceremony_names = [
            "session-start", "session-end", "memory-commit", "spawn-work",
        ]
        for name in stub_ceremony_names:
            entry = next((c for c in registry.ceremonies if c.name == name), None)
            assert entry is not None, f"Registry entry not found for '{name}'"
            assert entry.has_skill, f"Registry entry '{name}' should have has_skill: true"
            assert entry.skill is not None, f"Registry entry '{name}' should have skill set"

    def test_removed_feedback_stubs_have_no_skill(self):
        """WORK-148: Feedback ceremony stubs removed — has_skill must be false."""
        registry = load_ceremony_registry()
        removed_ceremony_names = [
            "chapter-review", "arc-review", "epoch-review", "requirements-review",
        ]
        for name in removed_ceremony_names:
            entry = next((c for c in registry.ceremonies if c.name == name), None)
            assert entry is not None, f"Registry entry not found for '{name}'"
            assert not entry.has_skill, f"Registry entry '{name}' should have has_skill: false (stub removed)"


class TestContractsParseable:
    """Test 4: Contract fields parse via CeremonyContract.from_frontmatter()."""

    @pytest.mark.parametrize("skill_name", ALL_CEREMONY_SKILLS)
    def test_frontmatter_parses_to_contract(self, skill_name):
        """Each skill's frontmatter must successfully parse into a CeremonyContract."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        data = load_frontmatter(skill_path)

        # Should not raise
        contract = CeremonyContract.from_frontmatter(data)

        assert contract.name == data["name"]
        assert contract.category == data["category"]
        assert isinstance(contract.input_contract, list)
        assert isinstance(contract.output_contract, list)
        assert isinstance(contract.side_effects, list)

    @pytest.mark.parametrize("skill_name", ALL_CEREMONY_SKILLS)
    def test_contract_has_at_least_one_side_effect(self, skill_name):
        """Every ceremony must declare at least one side effect."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        data = load_frontmatter(skill_path)

        assert len(data.get("side_effects", [])) > 0, (
            f"Skill '{skill_name}' must declare at least one side effect"
        )


class TestRegistrySkillCrossReference:
    """Test 5 (A1): Registry skill field resolves to actual SKILL.md with matching name."""

    def test_registry_skill_resolves_to_skill_file(self):
        """Every registry entry with has_skill: true must have a SKILL.md
        whose frontmatter name matches the registry skill field."""
        registry = load_ceremony_registry()
        for entry in registry.ceremonies:
            if not entry.has_skill or entry.skill is None:
                continue
            skill_path = SKILLS_DIR / entry.skill / "SKILL.md"
            assert skill_path.exists(), (
                f"Registry '{entry.name}' references skill '{entry.skill}' "
                f"but {skill_path} does not exist"
            )
            data = load_frontmatter(skill_path)
            assert data["name"] == entry.skill, (
                f"Registry '{entry.name}' references skill '{entry.skill}' "
                f"but SKILL.md has name '{data['name']}'"
            )


class TestStubSkillsMarked:
    """Test 6 (A7): Stub skills have stub: true to distinguish from functional skills."""

    @pytest.mark.parametrize("skill_name", STUB_CEREMONY_SKILLS)
    def test_stub_has_stub_marker(self, skill_name):
        """Each stub ceremony skill must have stub: true in frontmatter."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        data = load_frontmatter(skill_path)
        assert data.get("stub") is True, (
            f"Stub '{skill_name}' must have 'stub: true' in frontmatter"
        )

    @pytest.mark.parametrize("skill_name", EXISTING_CEREMONY_SKILLS)
    def test_existing_skills_not_marked_stub(self, skill_name):
        """Existing functional skills must NOT have stub: true."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        data = load_frontmatter(skill_path)
        assert data.get("stub") is not True, (
            f"Existing skill '{skill_name}' should not be marked as stub"
        )
