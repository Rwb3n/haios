---
description: Quick database schema lookup for haios_memory.db
allowed-tools: mcp__haios-memory__schema_info
argument-hint: [table_name]
---
# generated: 2025-12-09
# System Auto: last updated on: 2025-12-10 18:34:16
# Schema Lookup

**MAY** use for quick table/column lookups. For complex queries, **MUST** use schema-verifier subagent instead.

Arguments: $ARGUMENTS

Quick schema verification for haios_memory.db using MCP abstraction layer.

## Usage

- `/schema` - List all tables
- `/schema <table>` - Show columns for specific table

## Execute

Call the MCP tool:

```
mcp__haios-memory__schema_info(table_name=$ARGUMENTS or null)
```

If $ARGUMENTS is empty, call with no argument to list tables.
If $ARGUMENTS has a table name, pass it to get column info.

Format the result cleanly for the user.
