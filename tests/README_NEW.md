# generated: 2025-11-25
# System Auto: last updated on: 2025-12-05 20:30:00
# HAIOS Test Suite

> **Navigation:** [Quick Reference](../docs/README.md) | [Strategic Overview](../docs/epistemic_state.md) | [ETL Package](../haios_etl/README.md)

This directory contains the test suite for the HAIOS Cognitive Memory System.

**Status:** 154 tests passing (Phase 8 Complete - Agent Ecosystem MVP Operational)

---

## Test Overview

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_collaboration.py` | 25 | Agent collaboration, handoffs, error handling |
| `test_database.py` | 13 | Database operations, duplicates, metrics, agent registry |
| `test_extraction.py` | 6 | LLM extraction, retry logic, errors |
| `test_ingester.py` | 18 | Ingester agent, classification, provenance |
| `test_integration.py` | 2 | MCP server end-to-end |
| `test_interpreter.py` | 13 | Interpreter agent, intent translation, grounding |
| `test_mcp.py` | 8 | MCP tools, marketplace, memory operations |
| `test_preprocessors.py` | 5 | Format transformation, registry |
| `test_processing.py` | 10 | Batch processing, file safety |
| `test_refinement.py` | 13 | LLM classification, episteme creation, metadata |
| `test_retrieval.py` | 11 | ReasoningBank, strategy extraction, experience learning |
| `test_synthesis.py` | 30 | Clustering, LLM synthesis, cross-pollination, schema constraints |
