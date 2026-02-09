"""Tests for ceremony contract schema and registry.

WORK-111: Ceremony Contract Schema Design
Chapter: CH-011 (CeremonyContracts)
"""

import sys
from pathlib import Path

import pytest

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))

from ceremony_contracts import (
    CeremonyContract,
    CeremonyRegistry,
    ContractField,
    OutputField,
    load_ceremony_registry,
)


class TestContractField:
    """Test 3: Contract field required attributes."""

    def test_contract_field_required_attributes(self):
        """Each input contract field must have field, type, required, description."""
        field = ContractField(
            field="work_id", type="string", required=True, description="The ID"
        )
        assert field.field == "work_id"
        assert field.type == "string"
        assert field.required is True
        assert field.description == "The ID"

    def test_contract_field_optional_pattern(self):
        """Pattern field is optional."""
        field = ContractField(
            field="work_id",
            type="string",
            required=True,
            description="The ID",
            pattern=r"WORK-\d{3}",
        )
        assert field.pattern == r"WORK-\d{3}"

    def test_contract_field_no_pattern_default(self):
        """Pattern defaults to None when not provided."""
        field = ContractField(
            field="name", type="string", required=False, description="A name"
        )
        assert field.pattern is None


class TestOutputField:
    """Output contract fields use 'guaranteed' instead of 'required'."""

    def test_output_field_attributes(self):
        """Output field has field, type, guaranteed, description."""
        field = OutputField(
            field="success",
            type="boolean",
            guaranteed="always",
            description="Whether it worked",
        )
        assert field.field == "success"
        assert field.type == "boolean"
        assert field.guaranteed == "always"
        assert field.description == "Whether it worked"


class TestCeremonyContract:
    """Test 1: Parse ceremony contract from YAML frontmatter."""

    def test_parse_ceremony_contract(self):
        """Verify contract schema can be parsed from YAML frontmatter."""
        sample_yaml = {
            "name": "queue-commit",
            "category": "queue",
            "input_contract": [
                {
                    "field": "work_id",
                    "type": "string",
                    "required": True,
                    "description": "Work item ID",
                }
            ],
            "output_contract": [
                {
                    "field": "success",
                    "type": "boolean",
                    "guaranteed": "always",
                    "description": "Result",
                }
            ],
            "side_effects": ["Logs event"],
        }
        contract = CeremonyContract.from_frontmatter(sample_yaml)
        assert contract.name == "queue-commit"
        assert contract.category == "queue"
        assert len(contract.input_contract) == 1
        assert contract.input_contract[0].field == "work_id"
        assert contract.input_contract[0].required is True
        assert len(contract.output_contract) == 1
        assert contract.output_contract[0].guaranteed == "always"
        assert contract.side_effects == ["Logs event"]

    def test_empty_contracts_valid(self):
        """Ceremonies with no inputs (e.g., session-start) are valid."""
        contract = CeremonyContract(
            name="session-start",
            category="session",
            input_contract=[],
            output_contract=[],
            side_effects=["Logs SessionStarted event"],
        )
        assert len(contract.input_contract) == 0
        assert len(contract.output_contract) == 0


class TestCategoryValidation:
    """Test 4: Category validation."""

    VALID_CATEGORIES = ["queue", "session", "closure", "feedback", "memory", "spawn"]

    def test_valid_categories_accepted(self):
        """All 6 valid categories must be accepted."""
        for cat in self.VALID_CATEGORIES:
            contract = CeremonyContract(
                name="test",
                category=cat,
                input_contract=[],
                output_contract=[],
                side_effects=[],
            )
            assert contract.category == cat

    def test_invalid_category_rejected(self):
        """Category must be one of the 6 valid categories."""
        with pytest.raises(ValueError, match="Invalid category"):
            CeremonyContract(
                name="test",
                category="invalid",
                input_contract=[],
                output_contract=[],
                side_effects=[],
            )

    def test_dual_category_accepted(self):
        """Dual-category (list) must be accepted for ceremonies like close-work-cycle."""
        contract = CeremonyContract(
            name="close-work",
            category=["closure", "queue"],
            input_contract=[],
            output_contract=[],
            side_effects=[],
        )
        assert contract.category == ["closure", "queue"]

    def test_dual_category_invalid_member_rejected(self):
        """List with invalid category member must be rejected."""
        with pytest.raises(ValueError, match="Invalid category"):
            CeremonyContract(
                name="test",
                category=["closure", "invalid"],
                input_contract=[],
                output_contract=[],
                side_effects=[],
            )


class TestCeremonyRegistry:
    """Test 2: Load ceremony registry."""

    def test_load_ceremony_registry(self):
        """Verify registry YAML loads and contains all 19 ceremonies."""
        registry = load_ceremony_registry()
        assert len(registry.ceremonies) == 19

    def test_registry_has_all_categories(self):
        """Registry must cover all 6 ceremony categories."""
        registry = load_ceremony_registry()
        categories = set()
        for c in registry.ceremonies:
            if isinstance(c.category, list):
                categories.update(c.category)
            else:
                categories.add(c.category)
        assert categories == {"queue", "session", "closure", "feedback", "memory", "spawn"}

    def test_registry_ceremony_fields(self):
        """Each registry entry must have name, category, skill, signature."""
        registry = load_ceremony_registry()
        for c in registry.ceremonies:
            assert c.name, f"Missing name in registry entry"
            assert c.category, f"Missing category for {c.name}"
            assert c.signature, f"Missing signature for {c.name}"
            # skill can be None for unimplemented ceremonies


class TestCeremonyTemplate:
    """Test 5: Template renders valid schema."""

    def test_ceremony_template_exists(self):
        """Ceremony skill template must exist."""
        template_path = Path(".claude/templates/ceremony/SKILL.md")
        assert template_path.exists(), f"Template not found at {template_path}"

    def test_ceremony_template_has_contract_fields(self):
        """Ceremony skill template must contain contract schema placeholders."""
        template_path = Path(".claude/templates/ceremony/SKILL.md")
        content = template_path.read_text()
        assert "category:" in content, "Template missing category field"
        assert "input_contract:" in content, "Template missing input_contract"
        assert "output_contract:" in content, "Template missing output_contract"
        assert "side_effects:" in content, "Template missing side_effects"
