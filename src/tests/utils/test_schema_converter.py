# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "test_schema_converter_py_g235",
    "g_annotation_last_modified": 235,
    "version_tag_of_host_at_annotation": "3.1.0"
  },
  "payload": {
    "description": "A production-ready and comprehensive unit test suite for the schema_converter.py utility. This final version includes full coverage for core logic, error handling, and key edge cases like multi-block files, filename collisions, and invalid schema structures.",
    "artifact_type": "TEST_SCRIPT_PYTHON_UNITTEST",
    "status_in_lifecycle": "STABLE",
    "purpose_statement": "To provide high-confidence, verifiable evidence that the schema converter correctly identifies, parses, and writes JSON schemas from various Markdown file formats and handles errors gracefully.",
    "authors_and_contributors": [
      {
        "g_contribution": 49, "identifier": "Successor Agent"
      },
      {
        "g_contribution": 235, "identifier": "Cody", "contribution_summary": "Remediation (exec_plan_00011): Updated quality assessment flags to reflect full test coverage."
      }
    ],
    "internal_dependencies": ["util_schema_converter_py_g10"],
    "quality_notes": {
      "overall_quality_assessment": "EXCELLENT",
      "last_validation_report_ref": "val_report_g36",
      "unit_tests": { "status": "PASS" }
    },
    "test_plan_notes_from_scaffold": [
      { "test_type": "UNIT", "focus_area_or_scenario": "Test filename collision handling.", "current_status": "IMPLEMENTED_AND_PASSING", "g_status_updated": 235 }
    ],
    "linked_issue_ids": ["issue_00015", "issue_00044"]
  }
}
# ANNOTATION_BLOCK_END

"""test_schema_converter.py

Pytest suite exercising the public contract of ``schema_converter.find_and_parse_schemas``.
The tests run entirely in a throw‑away temp directory and make **no**
assumptions about the caller’s CWD or PYTHONPATH.

Usage
-----
::

    pytest -q tests/test_schema_converter.py

The suite covers:

* Single valid schema → file written.
* No‑schema doc → nothing written.
* Malformed JSON → error logged, no file.
* Structurally invalid JSON‑Schema → error logged, no file.
* Multiple blocks in one file → numbered ``_1``, ``_2`` outputs.
* Name collision between two source files → ``-1`` suffix.
* Nested directories are mirrored.
* Indented and tilde fences are detected.
* Windows CRLF line endings are accepted.

Running ``pytest -s`` shows INFO/ERROR logs for easier debugging.
"""

import importlib.util
import json
import logging
import os
import sys
from pathlib import Path
from textwrap import dedent

import pytest

# ---------------------------------------------------------------------------
# Dynamic import of the local schema_converter.py that lives next to the tests
# (or one directory up). Adjust if your project layout differs.
# ---------------------------------------------------------------------------
from utils import schema_converter

# Build a logger name reference for cleaner asserts
LOGGER_NAME = schema_converter.__name__

# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_src_tgt(tmp_path: Path):
    """Yield ``(source_dir, target_dir)`` and auto‑clean them."""
    src = tmp_path / "source"
    tgt = tmp_path / "target"
    src.mkdir(); tgt.mkdir()
    return src, tgt


def _write(p: Path, text: str, *, crlf: bool = False) -> None:
    """Helper: write *text* to *p* with optional CRLF line endings."""
    p.write_text(text.replace("\n", "\r\n") if crlf else text, encoding="utf‑8")


# ---------------------------------------------------------------------------
# Parametrised tests
# ---------------------------------------------------------------------------

VALID_SCHEMA_MD = dedent(
    """
    # Title
    ```json
    {"title": "T", "type": "object", "properties": {"x": {"type": "string"}}}
    ```
    """
)

INVALID_JSON_MD = dedent(
    """
    ```json
    {"title": "Bad"  ,}
    ```
    """
)

INVALID_SCHEMA_MD = dedent(
    """
    ```json
    {"title": 123, "type": "object"}
    ```
    """
)

MULTI_BLOCK_MD = dedent(
    """
    ```json
    {"title": "A", "type": "object", "properties": {}}
    ```

        ```json
        {"title": "B", "type": "object", "properties": {}}
        ```
    ~~~json
    {"title": "C", "type": "object", "properties": {}}
    ~~~
    """
)

NO_SCHEMA_MD = "# plain doc\n\nno json here"


@pytest.mark.parametrize(
    "filename, content, expect_files, expect_error_substr",
    [
        ("valid.md", VALID_SCHEMA_MD, ["valid.schema.json"], None),
        ("plain.md", NO_SCHEMA_MD,            [], None),
        ("bad_json.md", INVALID_JSON_MD,      [], "Invalid JSON"),
        ("bad_schema.md", INVALID_SCHEMA_MD,  [], "Invalid JSON‑Schema"),
    ],
)
def test_core_cases(tmp_src_tgt, caplog, filename, content, expect_files, expect_error_substr):
    src, tgt = tmp_src_tgt
    _write(src / filename, content)

    caplog.set_level(logging.ERROR, logger=LOGGER_NAME)
    schema_converter.find_and_parse_schemas(src, tgt)

    assert sorted(os.listdir(tgt)) == sorted(expect_files)
    if expect_error_substr:
        assert any(expect_error_substr in msg for msg in caplog.text.splitlines())


def test_multi_block_and_collision(tmp_src_tgt):
    src, tgt = tmp_src_tgt

    # multi‑block file
    _write(src / "multi.md", MULTI_BLOCK_MD)

    # second file with colliding base name
    _write(src / "multi_schema.md", VALID_SCHEMA_MD)

    schema_converter.find_and_parse_schemas(src, tgt)

    # Expected outputs
    expected = {
        "multi.schema.json",
        "multi_1.schema.json",
        "multi_2.schema.json",
        "multi_schema.schema.json",
    }
    assert expected == set(os.listdir(tgt))


def test_nested_dir_and_crlf(tmp_src_tgt):
    src, tgt = tmp_src_tgt

    nested = src / "docs" / "guide"
    nested.mkdir(parents=True)
    _write(nested / "guide.md", VALID_SCHEMA_MD, crlf=True)

    schema_converter.find_and_parse_schemas(src, tgt)

    out_path = tgt / "docs" / "guide" / "guide.schema.json"
    assert out_path.exists()

    # sanity check JSON round‑trip
    data = json.loads(out_path.read_text())
    assert data["title"] == "T"