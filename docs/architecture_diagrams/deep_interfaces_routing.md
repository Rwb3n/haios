# Deep Detail: Code Interfaces & Entry Routing

```text
┌─────────────────────────────────────────────────────────────┐
│                 CLI COMMANDS (cli.py / cmds)                │
│                                                             │
│  • haios_etl.cli:                                           │
│    - ingest, process, refine, synthesize                    │
│                                                             │
│  • Claude Code Plugins (.claude/commands/):                 │
│    - /coldstart, /new-work, /new-investigation              │
│    - /status, /haios, /close                                │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────┐
│             MCP SERVER (haios_etl/mcp_server.py)            │
│                                                             │
│  ┌──────────────────────┐   ┌────────────────────────────┐  │
│  │ Memory & Extraction  │   │     Agent Orchestration    │  │
│  ├──────────────────────┤   ├────────────────────────────┤  │
│  │ • memory_search_...  │   │ • marketplace_list_agents  │  │
│  │ • extract_content    │   │ • interpreter_translate    │  │
│  │ • memory_stats       │   │ • ingester_ingest          │  │
│  └──────────────────────┘   └────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────┐                                   │
│  │ Schema Introspection │                                   │
│  ├──────────────────────┤                                   │
│  │ • schema_info        │                                   │
│  │ • db_query (Read)    │                                   │
│  └──────────────────────┘                                   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────┐
│                  INTERNAL PHYTHON MODULES                   │
│   (database.py, extraction.py, retrieval.py, agents/*.py)   │
└─────────────────────────────────────────────────────────────┘
```

## Description
The **Interfaces** subsystem bridges raw user intent and programmatic MCP tool use into internal Python library paths:
- CLI commands (`cli.py`) run heavy batch processes.
- Claude Code Plugins (`.claude/commands`) scaffold the user environment and enforce the workspace state.
- `mcp_server.py` exposes tightly controlled, safe tools to GUI clients (Claude Desktop). Notice how direct SQL modifications are abstracted away behind `db_query` (read-only) and agent orchestrations.
