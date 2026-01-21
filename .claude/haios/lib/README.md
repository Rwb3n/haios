# generated: 2026-01-21
# System Auto: last updated on: 2026-01-21T21:00:19
# HAIOS Library

Portable plugin utilities for the HAIOS system.

## Migration

These modules were migrated from `.claude/lib/` in Session 221 (WORK-006) to enable
the portable plugin directory (`.claude/haios/`) to function independently.

## Modules

| Module | Purpose |
|--------|---------|
| `loader.py` | Config-driven content extraction from markdown (WORK-005) |
| `database.py` | Database connection and query utilities (DatabaseManager class) |
| `scaffold.py` | File scaffolding for templates |
| `work_item.py` | Work item parsing and manipulation |
| `config.py` | Configuration loading |
| `status.py` | System status generation |
| `validate.py` | File validation against templates |
| `observations.py` | Observation capture and triage |
| `cascade.py` | Work item cascade operations |
| `spawn.py` | Work item spawning |
| `backfill.py` | Backlog content backfill |
| `node_cycle.py` | Node lifecycle transitions |
| `governance_events.py` | Governance event logging |
| `routing.py` | Work routing decisions |
| `dependencies.py` | Dependency resolution |
| `retrieval.py` | Memory retrieval (requires haios_etl) |
| `synthesis.py` | Content synthesis (requires haios_etl) |
| `extraction.py` | Content extraction (requires haios_etl) |
| `error_capture.py` | Error tracking |
| `audit.py` | System audit operations |
| `errors.py` | Error definitions |
| `cli.py` | CLI utilities (requires haios_etl) |
| `mcp_server.py` | MCP server utilities (requires haios_etl) |

## Usage

### From modules (inside .claude/haios/)

```python
# Relative import (preferred for modules)
from ..lib.database import DatabaseManager

# Or via sys.path
import sys
from pathlib import Path
lib_path = Path(__file__).parent / "lib"
sys.path.insert(0, str(lib_path))
from database import DatabaseManager
```

### From hooks (outside .claude/haios/)

```python
import sys
from pathlib import Path
haios_lib = Path(__file__).parent.parent.parent / "haios" / "lib"
sys.path.insert(0, str(haios_lib))
from validate import validate_template
```

## Notes

- Some modules (retrieval, synthesis, extraction, cli, mcp_server) have dependencies on
  `haios_etl` package. These are used for ETL pipeline operations.
- Core modules (database, scaffold, validate, node_cycle, etc.) have no external dependencies
  beyond standard library and can be imported standalone.
