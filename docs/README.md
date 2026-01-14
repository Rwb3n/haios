# generated: 2025-11-30
# System Auto: last updated on: 2026-01-14T20:29:05
# HAIOS Documentation - Quick Reference

> **Progressive Disclosure:** Quick Reference (YOU ARE HERE) -> [Strategic Overview](epistemic_state.md) -> [Detailed Specs](specs/)

**System Status:** OPERATIONAL | 81k+ concepts | 18 skills | 13 MCP tools | Epoch 2.2 Active

---

## Cold Start Guide (Read This First)

If you're a new agent or resuming after context loss:

1. **CRITICAL - Vision Alignment:** [vision/VISION-INTERPRETATION-SESSION.md](vision/2025-11-30-VISION-INTERPRETATION-SESSION.md) - MANDATORY FIRST READ
2. **Technical Vision:** [VISION_ANCHOR.md](VISION_ANCHOR.md) - Architecture (ReasoningBank + LangExtract)
3. **Current State:** [epistemic_state.md](epistemic_state.md) - What's done, what's next
4. **Latest Handoff:** [Investigation Handoff](handoff/2025-11-30-INVESTIGATION-HANDOFF-vision-gap-analysis.md) - Gap analysis mission
5. **Run Tests:** `pytest` - Verify system integrity (154 tests should pass)

---

## Quick Status

| Component | Status | Evidence |
|-----------|--------|----------|
| Governance Suite | OPERATIONAL | System Awareness, Hooks, Templates Active |
| ETL Pipeline | COMPLETE | Data Quality Gaps Resolved |
| Embeddings | COMPLETE | 100% coverage (verified) |
| ReasoningBank | OPERATIONAL | Strategy Extraction Active (Loop Closed) |
| Memory Synthesis | OPERATIONAL | 2 insights created |
| Agent Registry | OPERATIONAL | 2 agents (Interpreter, Ingester) |
| MCP Server | ONLINE | 13 tools exposed |
| Schema v3 | AUTHORITATIVE | 17 tables |

**Test:** `python -m pytest tests/ -v` (154 passing)

---

## Documentation Hierarchy

### Layer 0: Vision Alignment (CRITICAL)
| Document | Purpose | When to Read |
|----------|---------|--------------|
| [vision/](vision/) | Vision directory index | Understanding true intent |
| [Vision Interpretation Session](vision/2025-11-30-VISION-INTERPRETATION-SESSION.md) | Canonical vision definition | MANDATORY on cold start |

### Layer 1: Quick Reference (Entry Points)
| Document | Purpose | When to Read |
|----------|---------|--------------|
| **This file** | Navigation hub | Always start here |
| [CLAUDE.md](../CLAUDE.md) | Agent instructions | Cold start |
| [VISION_ANCHOR.md](VISION_ANCHOR.md) | Technical architecture | Cold start |

### Layer 2: Strategic Overview
| Document | Purpose | When to Read |
|----------|---------|--------------|
| [epistemic_state.md](epistemic_state.md) | Current state, knowns, unknowns | Understanding system state |
| [OPERATIONS.md](OPERATIONS.md) | How to operate the system | Running commands |
| [MCP_INTEGRATION.md](MCP_INTEGRATION.md) | Agent ecosystem connection | Setting up MCP |

### Layer 3: Detailed Documentation
| Document | Purpose | When to Read |
|----------|---------|--------------|
| [COGNITIVE_MEMORY_SYSTEM_SPEC.md](COGNITIVE_MEMORY_SYSTEM_SPEC.md) | Full system specification | Deep understanding |
| [specs/TRD-ETL-v2.md](specs/TRD-ETL-v2.md) | ETL technical requirements | Implementation details |
| [specs/memory_db_schema_v3.sql](specs/memory_db_schema_v3.sql) | Database schema (AUTHORITATIVE) | DB work |

### Layer 4: Historical Context
| Location | Content | When to Read |
|----------|---------|--------------|
| [checkpoints/](checkpoints/) | Session summaries | Understanding past decisions |
| [handoff/](handoff/) | Handoff documents | Resuming work |
| [plans/](plans/) | Implementation plans | Following structured work |
| [walkthroughs/](walkthroughs/) | Implementation walkthroughs | Understanding how things were built |
| [reports/](reports/) | Investigation reports | Debugging, analysis |
| [anti-patterns/](anti-patterns/) | Known failure modes | Avoiding common mistakes |
| [specs/](specs/) | Technical specifications | Implementation details |

### Layer 5: Reference Materials
| Location | Content | When to Read |
|----------|---------|--------------|
| [CONSTRAINTS_AND_MITIGATIONS.md](CONSTRAINTS_AND_MITIGATIONS.md) | System constraints analysis | Understanding limitations |
| [libraries/](libraries/) | External library guides | Integration work |
| [risks-decisions/](risks-decisions/) | Risk assessments | Understanding constraints |
| [archive/](archive/) | Resolved handoffs, old checkpoints | Historical context |

### Layer 6: Risk Decisions (RD)
| Document | Risk | Mitigation |
|----------|------|------------|
| [RD-001](risks-decisions/RD-001-llm-non-determinism.md) | LLM Non-determinism | Retry logic, validation |
| [RD-002](risks-decisions/RD-002-api-rate-limits.md) | API Rate Limits | Backoff, quota management |
| [RD-003](risks-decisions/RD-003-processing-time.md) | Processing Time | Batch processing, checkpoints |
| [RD-004](risks-decisions/RD-004-sqlite-limitations.md) | SQLite Limitations | WAL mode, connection pooling |

### Layer 7: Library References
| Document | Library | Purpose |
|----------|---------|---------|
| [langextract_reference.md](libraries/langextract_reference.md) | google/langextract | Structured extraction |
| [sqlite_vec_reference.md](libraries/sqlite_vec_reference.md) | sqlite-vec | Vector similarity search |

---

## Key Commands

### Test & Verify
```bash
pytest                                    # Run all 154 tests
pytest tests/test_synthesis.py -v         # Synthesis tests only
python scripts/verify_live_db_constraints.py  # Verify schema
```

### Governance (Epoch 2)
```bash
/coldstart                                # Initialize session
/haios                                    # System Dashboard
/status                                   # Quick Health Check
/validate <file>                          # Validation Check
/new-plan <backlog_id> <title>            # Create Plan
/new-checkpoint <session> <title>         # Save Checkpoint
/new-handoff <type> <name>                # Create Handoff
/new-adr <number> <title>                 # Create ADR
/new-report <name>                        # Create Report
/schema [table_name]                      # Quick schema lookup
/workspace                                # Outstanding work status
```

### ETL Operations
```bash
python -m haios_etl.cli status            # Check processing status
python -m haios_etl.cli process HAIOS-RAW # Process files
python -m haios_etl.cli synthesis stats   # Synthesis statistics
python -m haios_etl.cli synthesis run --dry-run --limit 10  # Preview synthesis
python scripts/complete_concept_embeddings.py  # Complete embeddings (739 remaining)
```

### MCP Server
```bash
python -m haios_etl.mcp_server            # Start MCP server
```

### Diagnostics
```bash
python scripts/query_progress.py          # ETL progress
python scripts/query_progress.py --errors # Error analysis
```

---

## Project Structure

```
haios/
+-- CLAUDE.md                    # Agent instructions (READ FIRST)
+-- haios_etl/                   # Core implementation
|   +-- database.py              # DB operations (uses schema v3)
|   +-- extraction.py            # LangExtract integration
|   +-- retrieval.py             # ReasoningBank retrieval
|   +-- synthesis.py             # Memory synthesis pipeline
|   +-- mcp_server.py            # MCP server (10 tools)
|   +-- cli.py                   # Command-line interface
|   +-- migrations/              # Schema migrations (001-008)
+-- tests/                       # Test suite (154 tests)
+-- docs/                        # Documentation (YOU ARE HERE)
|   +-- README.md                # Quick Reference (this file)
|   +-- epistemic_state.md       # Strategic Overview
|   +-- VISION_ANCHOR.md         # Core Architecture
|   +-- OPERATIONS.md            # Operations Manual
|   +-- MCP_INTEGRATION.md       # MCP Guide
|   +-- specs/                   # Technical specifications
|   |   +-- memory_db_schema_v3.sql  # AUTHORITATIVE schema
|   |   +-- TRD-ETL-v2.md        # ETL specification
|   +-- checkpoints/             # Session checkpoints
|   +-- handoff/                 # Handoff documents
|   +-- plans/                   # Implementation plans
+-- scripts/                     # Utility scripts
+-- haios_memory.db              # SQLite database
```

---

## Session History

190 sessions from October 2025 to January 2026. See [checkpoints/](checkpoints/) for individual session documents.

**Current Focus (Epoch 2.2):** Skill decomposition, pressure dynamics, session manifest loading.

---

## Key Design Decisions (Recent)

| ID | Decision | Reference |
|----|----------|-----------|
| DD-010 | Schema source of truth is `memory_db_schema_v3.sql` | Session 16 |
| DD-011 | `source_type` includes 'cross' for bridge insights | Session 16 |
| DD-005 to DD-009 | Synthesis pipeline decisions | [PLAN-SYNTHESIS-001](plans/PLAN-SYNTHESIS-001-memory-consolidation.md) |
| DD-001 to DD-004 | Phase integration decisions | [S4-specification](plans/25-11-27-01-phase-integration/S4-specification-deliverable.md) |

---

## Bi-directional References

### This Document Links To:
- [CLAUDE.md](../CLAUDE.md) - Agent instructions
- [epistemic_state.md](epistemic_state.md) - Strategic overview
- [VISION_ANCHOR.md](VISION_ANCHOR.md) - Core architecture
- [OPERATIONS.md](OPERATIONS.md) - Operations manual
- [specs/memory_db_schema_v3.sql](specs/memory_db_schema_v3.sql) - Schema
- [checkpoints/](checkpoints/) - All session checkpoints
- [handoff/](handoff/) - All handoff documents

### Documents That Link Here:
- [CLAUDE.md](../CLAUDE.md) (Key Reference Locations)
- [epistemic_state.md](epistemic_state.md) (Navigation header)
- All checkpoint files (Navigation header)
- All handoff files (Navigation header)

---

**Last Updated:** 2026-01-14 (Session 190)
**Navigation:** [Strategic Overview](epistemic_state.md) | [Vision](VISION_ANCHOR.md) | [Operations](OPERATIONS.md) | [MCP](MCP_INTEGRATION.md)
