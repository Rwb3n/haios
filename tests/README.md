# generated: 2025-11-25
# System Auto: last updated on: 2025-12-21 14:09:00
# HAIOS Test Suite

> **Navigation:** [Quick Reference](../docs/README.md) | [Strategic Overview](../docs/epistemic_state.md) | [Library](../.claude/lib/README.md)

This directory contains the test suite for the HAIOS Cognitive Memory System.

## Status

**Current Passing Tests:** 321 (+1 skipped)
**Coverage:** Core ETL, Synthesis, Retrieval, MCP, Agents, Plugin Structure, Hooks, Status, Scaffold, Validate
**Governance:** Slash command verification included in manual test loops.

---

## Test Overview

### Core Library Tests (haios_etl/ and .claude/lib/)

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_synthesis.py` | 42 | Clustering, LLM synthesis, cross-pollination, schema constraints |
| `test_collaboration.py` | 23 | Agent collaboration, handoffs, error handling |
| `test_ingester.py` | 19 | Ingester agent, classification, provenance |
| `test_refinement.py` | 15 | LLM classification, episteme creation, metadata |
| `test_interpreter.py` | 14 | Interpreter agent, intent translation, grounding |
| `test_database.py` | 17 | Database operations, duplicates, metrics, agent registry, modes |
| `test_retrieval.py` | 13 | ReasoningBank, strategy extraction, experience learning |
| `test_processing.py` | 10 | Batch processing, file safety |
| `test_mcp.py` | 9 | MCP tools, marketplace, memory operations |
| `test_extraction.py` | 6 | LLM extraction, retry logic, errors |
| `test_preprocessors.py` | 5 | Format transformation, registry |
| `test_integration.py` | 2 | MCP server end-to-end |

### Plugin Structure Tests (E2-120 Migration)

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_plugin_structure.py` | 6 | Plugin manifest, lib directory, package init |
| `test_lib_database.py` | 7 | Database module from .claude/lib/ |
| `test_lib_retrieval.py` | 4 | Retrieval module from .claude/lib/ |
| `test_lib_status.py` | 28 | Status module: agents, commands, skills, memory, backlog, session delta, milestones |
| `test_lib_scaffold.py` | 23 | Scaffold module: path generation, template loading, variable substitution |
| `test_lib_validate.py` | 22 | Validate module: YAML parsing, field validation, status enums, reference counting |

### Infrastructure Tests

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_hooks.py` | 22 | Python hook dispatcher, all hook types |
| `test_health_checks.py` | 7 | Database health monitoring |
| `test_job_registry.py` | 9 | Background job tracking |
| `test_query_rewriter.py` | 10 | Query rewriting for retrieval |

### Pending/Manual

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_cli.py` | 0 | CLI integration (TODO - pending implementation) |
| `test_quality.py` | 0 | Quality metrics and reports (TODO - pending implementation) |
| `test_extraction_type_discrimination.py` | 0 | Manual test script (run directly, not via pytest) |

---

## Quick Start

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Module
```bash
pytest tests/test_database.py -v
pytest tests/test_retrieval.py -v
pytest tests/test_collaboration.py -v
pytest tests/test_synthesis.py -v
```

### Run with Coverage
```bash
pytest --cov=haios_etl --cov-report=term-missing
```

---

## Test Modules

### test_synthesis.py (Phase 9)

Tests for synthesis and clustering - 24 tests covering clustering, LLM synthesis, cross-pollination, and schema constraints.

### test_collaboration.py (Phase 8)

Tests for agent collaboration framework - 23 tests covering handoffs, error handling, and agent coordination.

### test_ingester.py (Phase 8)

Tests for Ingester agent - 19 tests covering classification, provenance, and error handling.

### test_refinement.py (Phase 7)

Tests for LLM-based classification - 15 tests for episteme creation and metadata handling.

### test_interpreter.py (Phase 8)

Tests for Interpreter agent - 14 tests for intent translation and grounding.

### test_retrieval.py (Phase 4)

Tests for ReasoningBank retrieval - 13 tests for strategy extraction and experience learning.

### test_database.py (Phase 3)

Tests for `DatabaseManager` class - 13 tests including agent registry operations.

### test_processing.py (Phase 3)

Tests for `BatchProcessor` class - 10 tests for file safety and processing.

### test_mcp.py (Phase 8)

Tests for MCP server tools - 9 tests for marketplace and memory operations.

### test_extraction.py (Phase 3)

Tests for `ExtractionManager` class - 6 tests for LLM extraction and retry logic.

### test_preprocessors.py (Phase 3)

Tests for preprocessor system - 5 tests for format transformation.

### test_integration.py (Phase 6)

End-to-end tests for MCP server - 2 tests.

### test_extraction_type_discrimination.py (Session 26)

Manual test script for entity type discrimination - validates correct classification of Directive, Critique, Proposal, and Decision types using real samples. Run directly with `python tests/test_extraction_type_discrimination.py` (not a pytest module).

### test_cli.py (Phase 3)

Tests for CLI module - argument parsing and end-to-end pipeline execution. **TODO:** Pending implementation.

### test_quality.py (Phase 3)

Tests for quality metrics collection and report generation. **TODO:** Pending implementation.

---

## Test Fixtures

Defined in `conftest.py`:

- **TODO:** `temp_database` - Temporary SQLite database
- **TODO:** `temp_directory` - Temporary test directory
- **TODO:** `sample_schema` - Sample extraction schema
- **TODO:** `mock_langextract` - Mocked LLM extraction

---

## Writing New Tests

### Test File Template
```python
import pytest
from unittest.mock import MagicMock, patch

# Import the module under test
from haios_etl.module import ClassName

@pytest.fixture
def mock_dependency():
    """Fixture description."""
    return MagicMock()

def test_function_name_scenario(mock_dependency):
    """Test description."""
    # Arrange
    instance = ClassName(mock_dependency)

    # Act
    result = instance.method()

    # Assert
    assert result == expected
```

### Naming Conventions
- Files: `test_<module>.py`
- Functions: `test_<function>_<scenario>`
- Classes: `Test<ClassName>`

### Best Practices
1. One assertion per test (when possible)
2. Use descriptive test names
3. Mock external dependencies (API calls, file I/O)
4. Test edge cases and error conditions
5. Keep tests independent (no shared state)

---

## Continuous Integration

Tests run automatically on:
- Pull request creation
- Push to main branch

### Running Locally Before Push
```bash
# Run tests
pytest

# Run with coverage check
pytest --cov=haios_etl --cov-fail-under=80
```

---

## Navigation

- [Quick Reference](../docs/README.md) - Documentation map
- [Strategic Overview](../docs/epistemic_state.md) - Current system state
- [Library Package](../.claude/lib/README.md) - Core modules (migrated from haios_etl/)
- [Operations Manual](../.claude/REFS/OPERATIONS.md) - Runbook

---

**Last Updated:** 2025-12-21 (Session 93)
**Status:** E2-120 Phase 2 Complete - Status, Scaffold, Validate Modules
**Tests:** 321 passing, 1 skipped (verified)
