# generated: 2025-12-30
# System Auto: last updated on: 2025-12-30T23:12:04
# Section 8: Memory Integration

Generated: 2025-12-30 (Session 151)
Purpose: Document MCP server + session-memory flow
Status: COMPLETE

---

## Gaps Identified (S152 Analysis)

| Gap | Description | Target Fix |
|-----|-------------|------------|
| **Tool count discrepancy** | Section says 13 tools, actual is 10 | Update to 10 tools |
| **No work item auto-linking** | ingester_ingest doesn't update WORK.md memory_refs | Add work_id parameter, PostToolUse auto-update |
| **ReasoningBank strategy injection** | memory_search queries reasoning_patterns but not documented here | Add strategy injection flow |

---

## Target Architecture: Work-Aware Memory

```yaml
# .claude/haios/config/memory-integration.yaml
memory:
  auto_link:
    enabled: true
    extract_work_id_from_path: true    # Parse E2-xxx/INV-xxx from source_path
    update_work_file: true             # Auto-append to memory_refs via PostToolUse

  strategy_injection:
    enabled: true
    table: reasoning_traces
    inject_on: [semantic, session_recovery]

  toon_encoding:
    enabled: true
    fallback: json
    token_reduction: 57%
```

**Flow with auto-linking:**
```
ingester_ingest(content, source_path="docs/work/active/E2-150/...")
    │
    ▼
Store concept → get concept_id
    │
    ▼
PostToolUse detects MCP ingest
    │
    ▼
Extract work_id from source_path (E2-150)
    │
    ▼
Update WORK.md: memory_refs: [..., concept_id]
```

---

## Overview

Memory integration connects session work to durable knowledge storage via the haios-memory MCP server.

**Database:** `haios_memory.db` (SQLite, ~80k concepts, ~9k entities)
**Schema:** `docs/specs/memory_db_schema_v3.sql`
**MCP Server:** `.claude/lib/mcp_server.py`

---

## MCP Server: haios-memory

### Configuration
```json
// .mcp.json
{
  "mcpServers": {
    "haios-memory": {
      "command": "python",
      "args": [".claude/lib/mcp_server.py"]
    }
  }
}
```

### Key Components
```python
# .claude/lib/mcp_server.py
from database import DatabaseManager         # Database operations
from extraction import ExtractionManager     # Entity/concept extraction
from retrieval import ReasoningAwareRetrieval # Strategy-enhanced search
```

---

## Tool Inventory (10 tools)

### Storage Tools

| Tool | Purpose | Used By |
|------|---------|---------|
| `ingester_ingest` | Store with auto-classification (Greek Triad) | checkpoint-cycle, close-work-cycle, why-capturer |
| `memory_store` | (DEPRECATED) Manual storage | - |
| `extract_content` | Entity/concept extraction | extract-content skill |

### Retrieval Tools

| Tool | Purpose | Modes |
|------|---------|-------|
| `memory_search_with_experience` | Query with strategy injection | semantic, session_recovery, knowledge_lookup |
| `memory_stats` | Database counts | - |

### Schema Tools

| Tool | Purpose | Safety |
|------|---------|--------|
| `schema_info` | Table/column info | Read-only |
| `db_query` | Execute SELECT queries | Read-only (INSERT/UPDATE/DELETE blocked) |

### Agent Marketplace Tools

| Tool | Purpose |
|------|---------|
| `marketplace_list_agents` | List available agents |
| `marketplace_get_agent` | Get agent details + schema |

### Interpreter Tool

| Tool | Purpose |
|------|---------|
| `interpreter_translate` | Intent → directive translation |

---

## Retrieval Modes (ADR-037)

| Mode | Purpose | Use Case |
|------|---------|----------|
| `semantic` | Pure vector similarity | General queries |
| `session_recovery` | Excludes synthesis | coldstart context load |
| `knowledge_lookup` | Filters to episteme/techne | Facts and how-to |

---

## Greek Triad Classification

| Type | Meaning | Examples |
|------|---------|----------|
| `episteme` | Knowledge, facts | "SQLite WAL mode enables concurrent reads" |
| `techne` | Skills, how-to | "To add a cycle: 1) Create SKILL.md..." |
| `doxa` | Opinions, beliefs | "Python is better than PowerShell for hooks" |

Classification is automatic via `ingester_ingest`. Optional `content_type_hint` can guide.

---

## Session-Memory Flow

### Cold Start (Session Recovery)
```
/coldstart
    │
    ▼
memory_search_with_experience(
    query="learnings for {backlog_ids} {focus}",
    mode='session_recovery'
)
    │
    ▼
reasoning_traces table (ReasoningBank)
    │
    ▼
Inject strategies into session context
```

### During Session (Context Augmentation)
```
memory-agent skill
    │
    ▼
memory_search_with_experience(
    query="strategies for {task}",
    mode='semantic'
)
    │
    ▼
Return relevant concepts + strategies
```

### Session End (Learning Capture)
```
checkpoint-cycle CAPTURE phase
    │
    ▼
ingester_ingest(
    content="Key learning: {insight}",
    source_path="docs/checkpoints/SESSION-N.md"
)
    │
    ▼
concepts table + entities table
    │
    ▼
memory_refs added to checkpoint frontmatter
```

### Work Closure (WHY Capture)
```
close-work-cycle MEMORY phase
    │
    ▼
why-capturer subagent
    │
    ▼
ingester_ingest(
    content="WHY: {decision rationale}",
    source_path="docs/work/archive/{id}/WORK.md"
)
```

---

## Database Schema (Key Tables)

| Table | Purpose | Records |
|-------|---------|---------|
| `concepts` | Stored knowledge | ~80k |
| `entities` | Named entities | ~9k |
| `embeddings` | Vector representations | ~80k |
| `reasoning_traces` | ReasoningBank (strategy storage) | ~1k |
| `synthesis_results` | Cross-concept bridges | ~500 |
| `agents` | Marketplace agent registry | ~10 |

---

## Memory Hooks

| Hook | Memory Action |
|------|---------------|
| `Stop` | ReasoningBank extraction (trace learnings) |
| `PostToolUse (E2-130)` | Error capture to memory |

---

## TOON Encoding

Output is TOON-encoded (57% smaller than JSON) when available:
```python
if TOON_AVAILABLE:
    return toon_encode(result)
```

TOON format: `results[10,]{id,type,content}:...`

---

## Key Patterns

### Query Before Assume
```
# Before implementing, check memory
mcp__haios-memory__memory_search_with_experience(
    query="how to implement X",
    mode='knowledge_lookup'
)
```

### Store After Complete
```
# After learning, persist
mcp__haios-memory__ingester_ingest(
    content="Learned: Y because Z",
    source_path="path/to/work.md"
)
```

### Schema Before Query
```
# Before SQL, verify schema
mcp__haios-memory__schema_info(table_name="concepts")
```

---

*Populated Session 151*
