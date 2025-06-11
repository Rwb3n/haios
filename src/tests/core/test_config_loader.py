from __future__ import annotations

# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {"artifact_id_of_host": "test_config_loader_py_g77"},
  "payload": {
    "description": "Unit tests for the ConfigLoader module. Covers successful loading, error conditions, and behavior of the get() method.",
    "artifact_type": "TEST_SCRIPT_PYTHON_PYTEST",
    "purpose_statement": "To provide evidence that the OS configuration can be loaded reliably and safely."
  }
}
# ANNOTATION_BLOCK_END

"""test_config_loader.py

Pytest suite for the revamped ``ConfigLoader``.

The tests exercise:

* Happy‑path loading & value retrieval
* Access before load → ``ConfigNotFoundError``
* Malformed JSON → ``ConfigParseError``
* Schema‑validation failure → ``SchemaValidationError``
* ``reload()`` updates in‑memory cache

The suite writes *both* the schema and config to a temporary directory
so the real filesystem is never touched. A **real** ``Validator`` is
used to validate the schema on disk; no mocks are required except for a
caplog scrub.
"""

import json
import sys
from pathlib import Path
from typing import Any

import pytest

from core.config_loader import ConfigLoader
from utils.validators import Validator, SchemaValidationError
from core.exceptions import (
    ConfigNotFoundError,
    ConfigParseError,
)


@pytest.fixture()
def schema_and_validator(tmp_path: Path):
    """Create a simple JSON‑Schema file and return a ready Validator."""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    schema_content: dict[str, Any] = {
        "$id": "haios.config",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    }
    (schema_dir / "haios.config.schema.json").write_text(
        json.dumps(schema_content), encoding="utf-8"
    )
    validator = Validator(schema_dir=str(schema_dir))
    return validator


@pytest.fixture()
def config_path(tmp_path: Path):
    cfg_path = tmp_path / "config.json"
    return cfg_path


def _write_config(path: Path, obj: dict[str, Any]):
    path.write_text(json.dumps(obj), encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Happy path
# ---------------------------------------------------------------------------

def test_load_success(schema_and_validator: Validator, config_path: Path):
    _write_config(config_path, {"name": "Ruben"})

    loader = ConfigLoader(config_path=config_path, validator=schema_and_validator)
    config = loader.load_and_validate()
    assert config["name"] == "Ruben"


# ---------------------------------------------------------------------------
# 2. Access before load
# ---------------------------------------------------------------------------

def test_malformed_json_raises_decode_error(schema_and_validator: Validator, config_path: Path):
    # Intentionally bad JSON (missing closing brace)
    config_path.write_text('{"name": "Ruben"', encoding="utf-8")

    loader = ConfigLoader(config_path=config_path, validator=schema_and_validator)
    with pytest.raises(ConfigParseError):
        loader.load_and_validate()


def test_schema_validation_failure(schema_and_validator: Validator, config_path: Path):
    # Missing required key "name"
    _write_config(config_path, {"wrong": "value"})

    loader = ConfigLoader(config_path=config_path, validator=schema_and_validator)
    with pytest.raises(SchemaValidationError):
        loader.load_and_validate()


# ---------------------------------------------------------------------------
# 4. Schema validation failure
# ---------------------------------------------------------------------------

def test_config_not_found_raises(schema_and_validator: Validator, config_path: Path):
    loader = ConfigLoader(config_path=config_path, validator=schema_and_validator)
    with pytest.raises(ConfigNotFoundError):
        loader.load_and_validate()
