# generated: 2025-11-27
# System Auto: last updated on: 2025-11-30 19:45:47
# HAiOS ETL Operations Manual

> **Progressive Disclosure:** [Quick Reference](README.md) -> [Strategic Overview](epistemic_state.md) -> **Operations (YOU ARE HERE)**
>
> **Navigation:** [Vision](VISION_ANCHOR.md) | [MCP](MCP_INTEGRATION.md) | [Schema](specs/memory_db_schema_v3.sql)

---

## Quick Reference

| Task | Command |
|------|---------|
| **Process Corpus** | `python -m haios_etl.cli process HAIOS-RAW` |
| **Check Status** | `python -m haios_etl.cli status` |
| **Reset Database** | `python -m haios_etl.cli reset` |
| **Run Synthesis** | `python -m haios_etl.cli synthesis run --dry-run` |
| **Synthesis Stats** | `python -m haios_etl.cli synthesis stats` |
| **Run Tests** | `pytest` |
| **Ingest File** | `python -m haios_etl.cli ingest <path>` |
| **Diagnostics** | `python scripts/query_progress.py` |

---

**Version:** 1.3
**Last Updated:** 2025-12-04

This document provides definitive operational procedures for the HAiOS ETL pipeline. It serves as the "Runbook" for operators and agents to ensure confident execution and troubleshooting.

## 1. Governance & Workflow (Epoch 2)

**Primary Interface:** Slash commands in Claude Code.

### Session Management
*   **Initialize:** `/coldstart` (Load instructions & context)
*   **Check Health:** `/haios` (System dashboard) or `/status` (Quick check)
*   **Save Progress:** `/checkpoint <session_num> <title>`
*   **Switch Context:** `/handoff <type> <name>`

### Artifact Creation (Scaffolding)
*   **Plan:** `/new-plan <name>` (Creates TRD-compliant plan)
*   **Report:** `/new-report <name>` (Creates formal report)

### Quality Assurance
*   **Validate:** `/validate <file>` (Run compliance checks)

## 2. Core Execution (ETL Pipeline)

### Standard Run
To process the corpus (idempotent - skips already processed files):
```powershell
python -m haios_etl.cli process HAIOS-RAW
```

### Checking Status
To view processing statistics and errors:
```powershell
python -m haios_etl.cli status
```

### Ingesting Files (Agent Ecosystem)
To ingest a specific file or directory using the Agent Ecosystem pipeline (Interpreter + Ingester):
```powershell
# Single file
python -m haios_etl.cli ingest path/to/file.md

# Directory (recursive)
python -m haios_etl.cli ingest path/to/dir -r
```

### Diagnostics & Analysis
For detailed progress analysis and error investigation:
```powershell
# Quick status summary
python scripts/query_progress.py

# Daily breakdown (see current vs historical status)
python scripts/query_progress.py --by-date

# Error analysis (group by type, show samples)
python scripts/query_progress.py --errors

# Full processing timeline
python scripts/query_progress.py --timeline
```

**Why use diagnostics?** The `status` command shows all-time errors, making it hard to distinguish current failures from historical ones that have since been resolved. The diagnostic utilities query the processing log to show:
- Current vs historical error state
- Success/error rates by date
- Error categorization (quota, file system, API issues)

**See:** [Scripts Directory](../scripts/README.md) for full utility documentation.

## 2. Database Inspection
**Database File:** `haios_memory.db`

### Key Tables
*   **`processing_log`**: Tracks the status of every file attempted.
    *   Columns: `file_path` (PK), `status` ('success', 'error', 'skipped'), `error_message`, `last_attempt_at`.
*   **`artifacts`**: Stores successfully ingested file metadata.
    *   Columns: `id`, `file_path`, `file_hash`, `version`, `last_processed_at`.
*   **`entities`** & **`concepts`**: Extracted knowledge.

### Common Queries
**Check specific file status:**
```sql
SELECT status, error_message FROM processing_log WHERE file_path LIKE '%filename%';
```

**Verify ingestion (Flexible Path):**
```sql
SELECT id, file_path, file_hash FROM artifacts WHERE file_path LIKE '%filename%';
```

**Verify Data Quality (AntiPatterns):**
```sql
SELECT COUNT(*) FROM entities WHERE type='AntiPattern';
```

## 3. Developer Guide: Scripting & Debugging

**Context Efficiency Rule:** Always check `docs/specs/memory_db_schema_v3.sql` before writing queries.

### Instantiating DatabaseManager
When writing verification scripts (e.g., in `scripts/`), handle the optional `db_path` argument correctly:
```python
from haios_etl.database import DatabaseManager

# Correct instantiation for scripts in project root
try:
    db = DatabaseManager() 
except TypeError:
    # Fallback if signature changes or specific path needed
    db = DatabaseManager("haios_memory.db")
```

### Path Matching Pitfalls
File paths in the DB are absolute. When querying for a file, prefer **wildcard matching** over exact paths to avoid drive letter or casing mismatches:
- **BAD:** `SELECT * FROM artifacts WHERE file_path = 'd:\foo\bar.json'`
- **GOOD:** `SELECT * FROM artifacts WHERE file_path LIKE '%bar.json'`

## 4. Troubleshooting & Edge Cases

### Non-Standard Format Handling (Preprocessors)
*   **Issue:** Some source files are not plain markdown (e.g., Gemini API session dumps in JSON format).
*   **Solution:** The system uses a **preprocessor architecture** to transform non-standard formats into plain text before extraction.
*   **Architecture:** See `@docs/specs/TRD-ETL-v2.md` section 4.7 for full specification.
*   **Current Preprocessors:**
    -   **Gemini Dumps:** Automatically detected by `"runSettings"` and `"chunkedPrompt"` markers. Extracts text fields via regex.
    -   Implementation: `haios_etl/preprocessors/gemini_dump.py`
*   **Procedure:**
    1.  Do **not** manually convert files - preprocessors run automatically.
    2.  If new format types appear, implement a new preprocessor following `haios_etl/preprocessors/base.py`.

### "Failed to parse JSON content" Errors
*   **Cause:** File format not recognized by any preprocessor, or preprocessor extraction failed.
*   **Fix:** Check if a preprocessor exists for this format type, or implement one following the base interface.

### Resetting a File
To force reprocessing of a specific file, delete its record from `processing_log`:
```sql
DELETE FROM processing_log WHERE file_path = 'path/to/file';
```

## 4. Memory Synthesis Pipeline

The synthesis pipeline consolidates similar memories into higher-order insights.

### Running Synthesis
```powershell
# Preview what would be synthesized (no changes)
python -m haios_etl.cli synthesis run --dry-run --limit 100

# Run actual synthesis on first 100 items
python -m haios_etl.cli synthesis run --limit 100

# Synthesize only concepts (skip traces)
python -m haios_etl.cli synthesis run --concepts-only

# Synthesize only traces (skip concepts)
python -m haios_etl.cli synthesis run --traces-only

# Skip cross-pollination stage
python -m haios_etl.cli synthesis run --skip-cross
```

### Checking Synthesis Stats
```powershell
python -m haios_etl.cli synthesis stats
```

Output shows:
- Total Concepts/Traces available
- Synthesized Concepts created
- Pending/Completed Clusters
- Cross-pollination Links

### Inspecting Clusters
```powershell
python -m haios_etl.cli synthesis inspect <cluster_id>
```

Shows cluster details including member IDs and synthesized content.

### Pipeline Stages
1. **CLUSTER** - Group similar memories by vector similarity (>0.85)
2. **SYNTHESIZE** - LLM extracts meta-pattern from cluster
3. **STORE** - Save synthesized concept with provenance
4. **CROSS-POLLINATE** - Bridge concepts and traces
5. **PRUNE** - Archive redundant entries (optional)

## 5. File Locations
*   **Source Corpus:** `HAIOS-RAW/`
*   **Database:** `haios_memory.db` (Root directory)
*   **Logs:** `logs/` (if configured) or stdout.

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| [Quick Reference](README.md) | Documentation map |
| [Strategic Overview](epistemic_state.md) | System state, knowns/unknowns |
| [MCP Integration](MCP_INTEGRATION.md) | Agent ecosystem connection |
| [Vision Anchor](VISION_ANCHOR.md) | Architectural vision |
| [ETL Spec](specs/TRD-ETL-v2.md) | Technical requirements |
| [Scripts README](../scripts/README.md) | Utility scripts reference |

---

*Last Updated: 2025-11-27*
