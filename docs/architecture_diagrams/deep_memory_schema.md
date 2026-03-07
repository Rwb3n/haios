# Deep Detail: Memory SQLite Schema & Abstraction

```text
┌─────────────────────────────────────────────────────────────┐
│                    MCP TOOLS (mcp_server.py)                │
│                                                             │
│  • memory_search_with_experience()                          │
│  • extract_content()                                        │
│  • schema_info() / db_query()     (Replaces bash SQLite)    │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────┐
│            DATABASE MANAGER (database.py Abstraction)       │
│                                                             │
│  • insert_entity()        • insert_concept()                │
│  • insert_embedding()     • insert_concept_embedding()      │
│  • search_memories()      • query_read_only()               │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────┐
│                    haios_memory.db schemas                  │
│                                                             │
│  ┌────────────────┐ ┌────────────────┐ ┌─────────────────┐  │
│  │    ENTITIES    │ │    CONCEPTS    │ │    ARTIFACTS    │  │
│  │ - id           │ │ - id           │ │ - id            │  │
│  │ - type         │ │ - type         │ │ - file_path     │  │
│  │ - value        │ │ - content      │ │ - file_hash     │  │
│  │                │ │ - source_adr   │ │ - version       │  │
│  └────────────────┘ └────────────────┘ └─────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────┐ ┌───────────────────┐  │
│  │        REASONING_TRACES         │ │     EMBEDDINGS    │  │
│  │ - id                            │ │ (sqlite-vec       │  │
│  │ - query, approach, outcome      │ │  extension)       │  │
│  │ - strategy_title/_description   │ │                   │  │
│  └─────────────────────────────────┘ └───────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Description
The `database.py` file acts as an abstraction layer above raw SQLite queries (allowing potential eventual migration to Postgres). 
- It houses explicitly defined tables mapping the extraction outputs (`Entities`, `Concepts`).
- The `ReasoningBank` specifications directly map to the `reasoning_traces` table.
- Direct Agent queries to SQLite using bash are actively blocked by Governance; instead, they must route through the MCP tools `schema_info()` and `db_query()`, ensuring safe read-only operations.
