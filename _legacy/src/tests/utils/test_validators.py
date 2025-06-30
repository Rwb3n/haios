# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {"artifact_id_of_host": "test_validators_py_g76"},
    "payload": {
        "description": "Unit tests for the shared Validator utility. Covers successful validation, schema loading failures, and data validation failures.",
        "artifact_type": "TEST_SCRIPT_PYTHON_PYTEST",
        "purpose_statement": "To provide evidence that the central schema validation mechanism is correct and robust.",
    },
}
# ANNOTATION_BLOCK_END

import json
from pathlib import Path

import pytest

from utils.validators import SchemaNotFoundError, SchemaValidationError, Validator


@pytest.fixture
def schema_dir(tmp_path: Path) -> Path:
    """Creates a temporary directory and a valid schema file within it."""
    schema_content = {
        "title": "Test Schema",
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    }
    schema_path = tmp_path / "test_schema.schema.json"
    schema_path.write_text(json.dumps(schema_content))
    return tmp_path


def test_validator_successful_validation(schema_dir: Path):
    validator = Validator(str(schema_dir))
    valid_data = {"name": "test"}
    # Should not raise an exception
    validator.validate("test_schema", valid_data)


def test_validator_raises_on_invalid_data(schema_dir: Path):
    validator = Validator(str(schema_dir))
    invalid_data = {"wrong_key": "test"}  # Missing 'name'
    with pytest.raises(SchemaValidationError, match=r"'name' is a required property"):
        validator.validate("test_schema", invalid_data)


def test_validator_raises_on_missing_schema(schema_dir: Path):
    validator = Validator(str(schema_dir))
    with pytest.raises(SchemaNotFoundError, match="Schema 'nonexistent' not found"):
        validator.validate("nonexistent", {})


def test_validator_caches_compiled_schemas(schema_dir: Path, mocker):
    validator = Validator(str(schema_dir))
    spy = mocker.spy(validator, "_load_and_compile_validator")

    # First call should load and compile
    validator.validate("test_schema", {"name": "a"})
    assert spy.call_count == 1

    # Second call should use the cache
    validator.validate("test_schema", {"name": "b"})
    assert spy.call_count == 1  # Unchanged
