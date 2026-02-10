"""Tests for ceremony contract validation and governance (WORK-113).

Chapter: CH-011 (CeremonyContracts)
Critique items addressed: A3 (missing success warning), A5 (governance gate),
    A6 (test file name), A7 (import re), A8 (success field coupling documented),
    A9 (registry field explicit)
"""

import sys
from pathlib import Path

import pytest
import yaml

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))

from ceremony_contracts import (
    CeremonyContract,
    ContractField,
    OutputField,
    ValidationResult,
    enforce_ceremony_contract,
    load_ceremony_registry,
    validate_ceremony_input,
    validate_ceremony_output,
)


# --- Input Validation Tests ---


class TestValidateInput:
    """Tests 1-4, 10: Input contract validation."""

    def test_validate_input_valid(self):
        """Test 1: Valid input passes validation."""
        contract = CeremonyContract.from_frontmatter(
            {
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
                "output_contract": [],
                "side_effects": [],
            }
        )
        result = validate_ceremony_input(contract, {"work_id": "WORK-113"})
        assert result.valid is True
        assert result.errors == []

    def test_validate_input_missing_required(self):
        """Test 2: Missing required input fails."""
        contract = CeremonyContract.from_frontmatter(
            {
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
                "output_contract": [],
                "side_effects": [],
            }
        )
        result = validate_ceremony_input(contract, {})
        assert result.valid is False
        assert any("work_id" in e for e in result.errors)

    def test_validate_input_optional_absent(self):
        """Test 3: Optional input may be absent."""
        contract = CeremonyContract.from_frontmatter(
            {
                "name": "queue-commit",
                "category": "queue",
                "input_contract": [
                    {
                        "field": "work_id",
                        "type": "string",
                        "required": True,
                        "description": "ID",
                    },
                    {
                        "field": "rationale",
                        "type": "string",
                        "required": False,
                        "description": "Why",
                    },
                ],
                "output_contract": [],
                "side_effects": [],
            }
        )
        result = validate_ceremony_input(contract, {"work_id": "WORK-113"})
        assert result.valid is True

    def test_validate_input_pattern_match(self):
        """Test 4: Pattern validation (regex match and mismatch)."""
        contract = CeremonyContract.from_frontmatter(
            {
                "name": "queue-commit",
                "category": "queue",
                "input_contract": [
                    {
                        "field": "work_id",
                        "type": "string",
                        "required": True,
                        "description": "ID",
                        "pattern": r"WORK-\d{3}",
                    }
                ],
                "output_contract": [],
                "side_effects": [],
            }
        )
        result = validate_ceremony_input(contract, {"work_id": "WORK-113"})
        assert result.valid is True

        result_bad = validate_ceremony_input(contract, {"work_id": "invalid"})
        assert result_bad.valid is False
        assert any("pattern" in e for e in result_bad.errors)

    def test_validate_input_empty_contract(self):
        """Test 10: Ceremony with no input contract accepts any input."""
        contract = CeremonyContract(
            name="session-start",
            category="session",
            input_contract=[],
            output_contract=[],
            side_effects=[],
        )
        result = validate_ceremony_input(contract, {"anything": "goes"})
        assert result.valid is True


# --- Output Validation Tests ---


class TestValidateOutput:
    """Tests 5, 6, 11, 16: Output contract validation."""

    def test_validate_output_valid(self):
        """Test 5: Valid output passes validation."""
        contract = CeremonyContract.from_frontmatter(
            {
                "name": "queue-commit",
                "category": "queue",
                "input_contract": [],
                "output_contract": [
                    {
                        "field": "success",
                        "type": "boolean",
                        "guaranteed": "always",
                        "description": "Result",
                    }
                ],
                "side_effects": [],
            }
        )
        result = validate_ceremony_output(contract, {"success": True})
        assert result.valid is True

    def test_validate_output_missing_always(self):
        """Test 6: Missing guaranteed=always output fails."""
        contract = CeremonyContract.from_frontmatter(
            {
                "name": "queue-commit",
                "category": "queue",
                "input_contract": [],
                "output_contract": [
                    {
                        "field": "success",
                        "type": "boolean",
                        "guaranteed": "always",
                        "description": "Result",
                    }
                ],
                "side_effects": [],
            }
        )
        result = validate_ceremony_output(contract, {})
        assert result.valid is False
        assert any("success" in e for e in result.errors)

    def test_validate_output_conditional_fields(self):
        """Test 11: on_success fields only required when success=True."""
        contract = CeremonyContract.from_frontmatter(
            {
                "name": "test",
                "category": "queue",
                "input_contract": [],
                "output_contract": [
                    {
                        "field": "success",
                        "type": "boolean",
                        "guaranteed": "always",
                        "description": "Result",
                    },
                    {
                        "field": "data",
                        "type": "string",
                        "guaranteed": "on_success",
                        "description": "Payload",
                    },
                    {
                        "field": "error",
                        "type": "string",
                        "guaranteed": "on_failure",
                        "description": "Error msg",
                    },
                ],
                "side_effects": [],
            }
        )
        # Success case: data required, error not
        result = validate_ceremony_output(
            contract, {"success": True, "data": "ok"}
        )
        assert result.valid is True

        # Failure case: error required, data not
        result = validate_ceremony_output(
            contract, {"success": False, "error": "failed"}
        )
        assert result.valid is True

    def test_output_validation_warns_missing_success_field(self):
        """Test 16 (A3): Warn when contract has on_success/on_failure but no success:always."""
        contract = CeremonyContract.from_frontmatter(
            {
                "name": "test",
                "category": "queue",
                "input_contract": [],
                "output_contract": [
                    {
                        "field": "data",
                        "type": "string",
                        "guaranteed": "on_success",
                        "description": "Payload",
                    }
                ],
                "side_effects": [],
            }
        )
        result = validate_ceremony_output(contract, {"data": "ok"})
        assert result.valid is False
        assert any("no 'success' field" in e for e in result.errors)


# --- Vocabulary Validation Tests ---


class TestVocabularyValidation:
    """Tests 7, 8: ContractField.type and OutputField.guaranteed vocabulary."""

    def test_output_field_guaranteed_vocabulary(self):
        """Test 7 (A5): guaranteed must be one of: always, on_success, on_failure."""
        valid_values = ["always", "on_success", "on_failure"]
        for val in valid_values:
            field = OutputField(
                field="x", type="string", guaranteed=val, description="test"
            )
            assert field.guaranteed == val

        with pytest.raises(ValueError, match="Invalid guaranteed"):
            OutputField(
                field="x",
                type="string",
                guaranteed="sometimes",
                description="test",
            )

    def test_contract_field_type_vocabulary(self):
        """Test 8 (A6): type must be one of: string, boolean, list, path, integer."""
        valid_types = ["string", "boolean", "list", "path", "integer"]
        for t in valid_types:
            field = ContractField(
                field="x", type=t, required=True, description="test"
            )
            assert field.type == t

        with pytest.raises(ValueError, match="Invalid type"):
            ContractField(
                field="x", type="float", required=True, description="test"
            )


# --- Registry Tests ---


class TestRegistrySelfVerification:
    """Tests 9, 17: Registry ceremony_count self-verification."""

    def test_registry_ceremony_count_matches_actual(self):
        """Test 9 (A10): ceremony_count must equal actual ceremony list length."""
        registry = load_ceremony_registry()
        assert registry.ceremony_count == len(registry.ceremonies), (
            f"Registry declares {registry.ceremony_count} "
            f"but has {len(registry.ceremonies)}"
        )

    def test_registry_ceremony_count_field_explicit(self):
        """Test 17 (A9): ceremony_count must be explicitly declared in YAML."""
        registry_path = Path(".claude/haios/config/ceremony_registry.yaml")
        with open(registry_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "ceremony_count" in data, (
            "ceremony_count field must be explicitly declared in registry YAML"
        )


# --- Governance Gate Tests ---


class TestEnforceCeremonyContract:
    """Tests 13, 14, 15: enforce_ceremony_contract governance gate."""

    def test_enforce_warn_mode_returns_result(self, tmp_path):
        """Test 13 (A5): In warn mode, returns ValidationResult, does not raise."""
        config = tmp_path / "haios.yaml"
        config.write_text(
            "toggles:\n  ceremony_contract_enforcement: warn\n"
        )
        contract = CeremonyContract(
            name="test",
            category="queue",
            input_contract=[
                ContractField(
                    field="x", type="string", required=True, description="X"
                )
            ],
            output_contract=[],
            side_effects=[],
        )
        result = enforce_ceremony_contract(contract, {}, config_path=config)
        assert result.valid is False
        assert len(result.errors) > 0  # errors returned, not raised

    def test_enforce_block_mode_raises(self, tmp_path):
        """Test 14 (A5): In block mode, raises ValueError on invalid input."""
        config = tmp_path / "haios.yaml"
        config.write_text(
            "toggles:\n  ceremony_contract_enforcement: block\n"
        )
        contract = CeremonyContract(
            name="test",
            category="queue",
            input_contract=[
                ContractField(
                    field="x", type="string", required=True, description="X"
                )
            ],
            output_contract=[],
            side_effects=[],
        )
        with pytest.raises(ValueError, match="enforcement=block"):
            enforce_ceremony_contract(contract, {}, config_path=config)

    def test_enforce_valid_input_passes(self, tmp_path):
        """Test 15: Valid input passes regardless of enforcement mode."""
        config = tmp_path / "haios.yaml"
        config.write_text(
            "toggles:\n  ceremony_contract_enforcement: block\n"
        )
        contract = CeremonyContract(
            name="test",
            category="queue",
            input_contract=[
                ContractField(
                    field="x", type="string", required=True, description="X"
                )
            ],
            output_contract=[],
            side_effects=[],
        )
        result = enforce_ceremony_contract(
            contract, {"x": "val"}, config_path=config
        )
        assert result.valid is True


# --- Backward Compatibility ---


class TestBackwardCompatibility:
    """Test 12: Existing contract parsing unchanged."""

    def test_existing_contract_parsing_unchanged(self):
        """WORK-111/112 contract parsing still works."""
        sample = {
            "name": "queue-commit",
            "category": "queue",
            "input_contract": [
                {
                    "field": "work_id",
                    "type": "string",
                    "required": True,
                    "description": "ID",
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
        contract = CeremonyContract.from_frontmatter(sample)
        assert contract.name == "queue-commit"
        assert len(contract.input_contract) == 1
        assert len(contract.output_contract) == 1
