# generated: 2025-12-30
# System Auto: last updated on: 2025-12-30T23:13:45
# Section 13: MCP Servers

Generated: 2025-12-30 (Session 151)
Purpose: Document MCP server integration, tool exposure, and external service patterns
Status: COMPLETE

---

## Gaps Identified (S152 Analysis)

| Gap | Description | Target Fix |
|-----|-------------|------------|
| **context7 not in .mcp.json** | Only haios-memory is configured. context7 is external/global | Clarify: context7 is external utility, not HAIOS core |
| **MCP is static infrastructure** | No dynamic server loading based on context | Future: work-context-aware MCP |

---

## Overview

MCP (Model Context Protocol) servers expose external tools to the agent. They run as separate processes and communicate via JSON-RPC.

**HAIOS Core:**
- **Configuration:** `.mcp.json`
- **Servers:** 1 (haios-memory)
- **Tools:** 10

**External (Claude Code ecosystem, not HAIOS-specific):**
- **context7:** Documentation lookup utility (2 tools)
- **Other MCPs:** Available but not part of HAIOS plugin

---

## MCP Configuration

```json
// .mcp.json (HAIOS plugin config)
{
  "mcpServers": {
    "haios-memory": {
      "command": "python",
      "args": [".claude/lib/mcp_server.py"],
      "env": {
        "DB_PATH": "haios_memory.db",
        "PYTHONPATH": ".claude/lib"
      }
    }
  }
}
```

**Note:** context7 is NOT configured in `.mcp.json`. It's an external MCP available in the Claude Code ecosystem for querying library documentation. It's used BY agents within HAIOS but is not PART OF HAIOS.

---

## Server: haios-memory (10 tools)

**Purpose:** Memory database access (concepts, entities, search, ingest)
**Implementation:** `.claude/lib/mcp_server.py`
**Database:** `haios_memory.db`

### Tool Inventory

| Tool | Purpose | Category |
|------|---------|----------|
| `memory_search_with_experience` | Query with strategy injection | Retrieval |
| `memory_stats` | Database counts | Retrieval |
| `memory_store` | (DEPRECATED) Manual storage | Storage |
| `ingester_ingest` | Auto-classifying storage | Storage |
| `extract_content` | Entity/concept extraction | Storage |
| `schema_info` | Table/column info | Schema |
| `db_query` | Read-only SQL | Schema |
| `marketplace_list_agents` | List available agents | Marketplace |
| `marketplace_get_agent` | Get agent details | Marketplace |
| `interpreter_translate` | Intent → directive | Interpreter |

### Key Tools

**`memory_search_with_experience`**
```python
# Modes: semantic, session_recovery, knowledge_lookup
mcp__haios-memory__memory_search_with_experience(
    query="strategies for X",
    mode='semantic'
)
```

**`ingester_ingest`**
```python
# Auto-classifies to episteme/techne/doxa
mcp__haios-memory__ingester_ingest(
    content="Learning: X because Y",
    source_path="docs/work/E2-123/WORK.md"
)
```

**`schema_info`** / **`db_query`**
```python
# Schema-verifier subagent uses these
mcp__haios-memory__schema_info(table_name="concepts")
mcp__haios-memory__db_query(sql="SELECT COUNT(*) FROM concepts")
```

---

## Server: context7 (2 tools)

**Purpose:** External documentation lookup
**Implementation:** NPM package `@anthropic/context7-mcp`

### Tool Inventory

| Tool | Purpose |
|------|---------|
| `resolve-library-id` | Find library ID for docs |
| `query-docs` | Query library documentation |

### Usage Pattern

```python
# Step 1: Resolve library
mcp__context7__resolve-library-id(
    libraryName="fastmcp",
    query="how to create MCP server"
)

# Step 2: Query docs
mcp__context7__query-docs(
    libraryId="/anthropic/fastmcp",
    query="tool definition"
)
```

---

## MCP in the Layer Stack

```
LAYER -2: MCP SERVERS
─────────────────────
External processes exposing tools via JSON-RPC

┌─────────────────┐    ┌─────────────────┐
│  haios-memory   │    │    context7     │
│                 │    │                 │
│  Python process │    │  Node process   │
│  13 tools       │    │  2 tools        │
│  haios_memory.db│    │  External APIs  │
└─────────────────┘    └─────────────────┘
        │                      │
        └──────────┬───────────┘
                   │
            JSON-RPC Protocol
                   │
                   ▼
         ┌─────────────────┐
         │  Claude Agent   │
         │                 │
         │  Invokes via:   │
         │  mcp__<srv>__<t>│
         └─────────────────┘
```

MCP sits **below** all other layers - it provides primitive capabilities.

---

## Tool Naming Convention

```
mcp__<server>__<tool>

Examples:
mcp__haios-memory__ingester_ingest
mcp__haios-memory__memory_search_with_experience
mcp__context7__resolve-library-id
mcp__context7__query-docs
```

---

## MCP vs Built-in Tools

| Aspect | Built-in | MCP |
|--------|----------|-----|
| Latency | Low | Higher (IPC) |
| Reliability | High | Can fail (process crash) |
| Capabilities | Fixed | Extensible |
| Governance | Hook-controlled | Server-controlled |
| State | Stateless | Can maintain state |

---

## When to Use MCP

| Use Case | Use MCP? | Alternative |
|----------|----------|-------------|
| Database access | Yes | Direct SQLite (blocked) |
| External API | Yes | WebFetch (limited) |
| Documentation lookup | Yes | WebSearch (generic) |
| File operations | No | Built-in (Read, Write, Edit) |
| Shell execution | No | Bash tool |
| Memory query/store | Yes | Required |

---

## Adding New MCP Server

### 1. Create Server Script
```python
# .claude/lib/my_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def my_tool(arg: str) -> str:
    """Tool description."""
    return result
```

### 2. Add to Configuration
```json
// .mcp.json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": [".claude/lib/my_server.py"]
    }
  }
}
```

### 3. Document in MCP Directory
```
.claude/mcp/my_server_mcp.md
```

### 4. Add Permissions
```json
// .claude/settings.local.json
{
  "permissions": {
    "allow": ["mcp__my-server__*"]
  }
}
```

---

## MCP Safety Considerations

### Read-Only Enforcement
```python
# db_query blocks INSERT/UPDATE/DELETE
if any(keyword in sql.upper() for keyword in ['INSERT', 'UPDATE', 'DELETE', 'DROP']):
    return {"error": "Only SELECT queries allowed"}
```

### Process Isolation
- MCP servers run as separate processes
- Crash doesn't affect agent
- Can be restarted independently

### Hook Integration
- MCP calls are NOT hook-gated currently
- Potential enhancement: PreToolUse checks for MCP

---

## Key Patterns

### Pattern: Memory Before Assume
```python
# Query memory before implementing
result = mcp__haios-memory__memory_search_with_experience(
    query="how to implement X",
    mode='knowledge_lookup'
)
# If relevant results, use them
# If not, proceed with implementation
```

### Pattern: Store After Complete
```python
# Store learnings after work
mcp__haios-memory__ingester_ingest(
    content="Learned: Y because Z",
    source_path="docs/work/E2-123/WORK.md",
    content_type_hint="techne"
)
```

### Pattern: Schema Before Query
```python
# Verify schema before SQL
schema = mcp__haios-memory__schema_info(table_name="concepts")
# Then construct query
result = mcp__haios-memory__db_query(sql="SELECT ...")
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Tool not found | Server not running | Restart Claude Code |
| Timeout | Server process stuck | Kill and restart |
| Permission denied | Not in allow list | Add to settings.local.json |
| Database locked | Concurrent access | Use WAL mode |

---

*Populated Session 151*
