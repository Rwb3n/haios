# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "utils_validators_py_g228",
    "g_annotation_last_modified": 228,
    "version_tag_of_host_at_annotation": "2.0.0"
  },
  "payload": {
    "description": "A shared utility module for loading, caching, and applying JSON schema validation across the OS. Centralizes schema validation logic for consistency and performance.",
    "artifact_type": "UTILITY_MODULE_PYTHON",
    "status_in_lifecycle": "STABLE",
    "purpose_statement": "To provide a single, reliable, and performant mechanism for ensuring all OS Control Files and other data structures adhere to their defined schemas.",
    "authors_and_contributors": [
      {
        "_locked_entry_definition": True,
        "g_contribution": 67, "identifier": "Cody"
      },
      {
        "g_contribution": 228, "identifier": "Cody",
        "contribution_summary": "Remediation (exec_plan_00009): Repaired class structure by indenting methods, fixed imports to be package-relative, removed duplicate exceptions, and pinned dependency versions."
      }
    ],
    "external_dependencies": [
      {
        "name": "jsonschema",
        "version_constraint": ">=4.0,<5.0",
        "reason_or_usage": "Core engine for validating data against JSON Schema definitions."
      }
    ],
    "internal_dependencies": ["..core.exceptions"],
    "key_logic_points_or_summary": [
      "Defines a `Validator` class that loads schema definitions from a specified directory.",
      "Caches compiled `jsonschema` validators in memory to avoid repeated compilation overhead.",
      "Provides a simple `validate(schema_id, data)` method."
    ],
    "quality_notes": {
      "overall_quality_assessment": "NEEDS_IMPROVEMENT"
    },
    "linked_issue_ids": ["issue_00063"]
  }
}
# ANNOTATION_BLOCK_END

import json
import logging
from pathlib import Path
from typing import Any, Dict

import jsonschema
from jsonschema import Draft202012Validator

from core.exceptions import ConfigError

class SchemaNotFoundError(ConfigError):
    """Raised when a schema file cannot be found."""

class SchemaValidationError(ConfigError):
    """Raised when data fails validation against a schema."""

class SchemaInvalidError(ConfigError):
    """Raised when a schema itself is invalid."""

logger = logging.getLogger(__name__)

class Validator:
    """
    A class that loads, caches, and runs JSON schema validations.
    """
    def __init__(self, schema_dir: str):
        """
        Initializes the Validator.

        Args:
            schema_dir: The directory where .schema.json files are stored.
        """
        self.schema_dir = Path(schema_dir)
        self._validator_cache: Dict[str, Draft202012Validator] = {}

    def _load_and_compile_validator(self, schema_id: str) -> Draft202012Validator:
        """Loads a schema from disk, validates it, and compiles a validator."""
        schema_path = self.schema_dir / f"{schema_id}.schema.json"
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
        except FileNotFoundError:
            raise SchemaNotFoundError(f"Schema '{schema_id}' not found at {schema_path}") from None
        except (json.JSONDecodeError, jsonschema.SchemaError) as err:
            raise SchemaInvalidError(f"Schema '{schema_id}' is malformed: {err}") from err

        validator = Draft202012Validator(schema)
        self._validator_cache[schema_id] = validator
        logger.debug("Loaded and cached validator for schema '%s'.", schema_id)
        return validator

    def validate(self, schema_id: str, data_to_validate: Dict[str, Any]) -> None:
        """
        Validates a data object against a specified schema.

        Args:
            schema_id: The ID of the schema to validate against (e.g., 'state').
            data_to_validate: The dictionary object to validate.

        Raises:
            SchemaNotFoundError: If the schema file cannot be found.
            SchemaInvalidError: If the schema file itself is not a valid JSON Schema.
            SchemaValidationError: If validation of the data fails.
        """
        validator = self._validator_cache.get(schema_id)
        if not validator:
            validator = self._load_and_compile_validator(schema_id)

        try:
            validator.validate(data_to_validate)
            logger.debug("Data successfully validated against schema '%s'.", schema_id)
        except jsonschema.ValidationError as e:
            error_path = " -> ".join(map(str, e.path)) if e.path else "root"
            raise SchemaValidationError(
                f"Schema validation failed for '{schema_id}' at '{error_path}': {e.message}"
            ) from e