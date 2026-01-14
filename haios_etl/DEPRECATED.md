# generated: 2025-12-21
# System Auto: last updated on: 2025-12-21T14:23:36
# DEPRECATED: haios_etl/ has moved

**As of Session 92 (2025-12-21)**, all Python code has been migrated to `.claude/lib/`.

## New Location

```
.claude/lib/
├── __init__.py
├── database.py
├── retrieval.py
├── synthesis.py
├── refinement.py
├── mcp_server.py
├── cli.py
├── status.py        # From UpdateHaiosStatus.ps1
├── scaffold.py      # From ScaffoldTemplate.ps1
├── validate.py      # From ValidateTemplate.ps1
└── agents/
    ├── __init__.py
    ├── ingester.py
    └── interpreter.py
```

## Why?

1. **Plugin Portability**: HAIOS is now a self-contained Claude Code plugin
2. **PowerShell Elimination**: All .ps1 scripts migrated to Python (E2-120)
3. **Single Location**: All code in `.claude/` for easy installation into any project

## Migration

If you have code importing from `haios_etl`:

```python
# OLD (deprecated)
from haios_etl.database import DatabaseManager

# NEW (correct)
import sys
sys.path.insert(0, '.claude/lib')
from database import DatabaseManager
```

## Reference

- **E2-120**: Plugin Architecture Migration
- **Session 92-94**: Migration implementation
- **Memory refs**: 76938-77016
