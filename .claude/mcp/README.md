---
template: readme
status: active
date: 2025-12-07
component: mcp
version: 2.0
owner: Template System
---
# generated: 2025-09-23
# System Auto: last updated on: 2025-12-09 23:04:34

# MCP (Model Context Protocol) Framework

## Overview

**Purpose:** Extend Claude's capabilities through external tools and data sources

**Status:** active

**Quick Facts:**
- **Version:** 2.0
- **Owner:** Template System
- **Dependencies:** Claude Code CLI, MCP servers
- **Platform:** Cross-platform
- **HAIOS Memory:** 64,765 concepts, 754 reasoning traces

## Available MCP Servers

### Default (Template-Provided)
- **Context7** (`mcp__context7__*`) - Up-to-date library documentation
- **IDE** (`mcp__ide__*`) - VS Code integration tools

### Project-Specific (HAIOS)
- **HAIOS Memory** (`mcp__haios-memory__*`) - Cognitive memory with ReasoningBank
  - `ingester_ingest(content, source_path, content_type_hint)` - **PRIMARY** - Ingest with auto-classification
  - `memory_stats()` - Database statistics (artifacts, entities, concepts, embeddings)
  - `memory_search_with_experience(query, space_id)` - Semantic search with strategy injection
  - `extract_content(file_path, content, extraction_mode)` - LLM-based entity/concept extraction
  - `interpreter_translate(intent)` - Natural language to structured directive
  - `marketplace_list_agents(capability)` - List available marketplace agents
  - `marketplace_get_agent(agent_id)` - Get agent details and schema
  - `schema_info(table_name)` - **NEW** - Database schema introspection (Session 53)
  - `db_query(sql)` - **NEW** - Read-only SQL queries (SELECT only, Session 53)
  - `memory_store(content, content_type, source_path)` - **DEPRECATED** - Use `ingester_ingest`

## How Claude Discovers MCP Tools

1. **Automatic** - MCP tools appear in my available tools list
2. **Documentation** - Linked from `@CLAUDE.md` under "Available MCP Services"
3. **Guides** - Each MCP has a guide file in this directory

## Adding a New MCP

1. Configure the MCP server in your environment
2. Create a guide file: `.claude/mcp/[name]_mcp.md`
3. Use the guide template: `@templates/guide_template.md`
4. Focus on constraints, gotchas, and patterns

## MCP Usage Pattern

```
1. Check if MCP tool exists (mcp__[server]__*)
2. Read the guide file for constraints
3. Follow the patterns in the guide
4. Handle errors per the guide
```

## Key Principles

- **Guides are references, not tutorials** - Keep them concise
- **Focus on gotchas** - What will cause errors?
- **Provide patterns** - Copy-paste ready examples
- **Document constraints** - Token limits, required parameters, etc.

## Integration with Hooks

MCP operations are read-only and don't trigger PostToolUse hooks. They work seamlessly alongside the template's hook system.

**HAIOS Integration (Epoch 2):**
- **UserPromptSubmit** hook calls `memory_search_with_experience` to inject strategies
- **Stop** hook extracts learnings via `reasoning_extraction.py` and stores to memory
- ReasoningBank loop is CLOSED: strategies are injected at session start and extracted at session end

## Quick Start

Get MCP tools running in under 2 minutes:

```bash
# Check available MCP tools
claud code --list-tools | grep mcp__

# Test Context7 MCP
# Use mcp__context7__resolve-library-id tool with "react" as input

# Verify MCP guides exist
ls .claude/mcp/*_mcp.md
```

**Example:** Using Context7 for documentation
```
1. Call mcp__context7__resolve-library-id with library name
2. Call mcp__context7__get-library-docs with the ID
3. Receive up-to-date documentation
```

For MCP configuration details, see @CLAUDE.md

## Core Concepts

### MCP Servers
External services that provide tools to Claude through a standardized protocol.

### MCP Tools
Appear as `mcp__[server]__[function]` in Claude's tool list.

### MCP Guides
Documentation files in this directory following the pattern `[name]_mcp.md`.

## Usage

### Common Patterns

#### Pattern 1: Documentation Retrieval
```
1. Resolve library ID: mcp__context7__resolve-library-id
2. Get documentation: mcp__context7__get-library-docs
```

#### Pattern 2: IDE Integration
```
1. Get diagnostics: mcp__ide__getDiagnostics
2. Execute code: mcp__ide__executeCode (Jupyter only)
```

#### Pattern 3: HAIOS Memory Search with ReasoningBank
```
1. Check health: mcp__haios-memory__memory_stats
2. Search: mcp__haios-memory__memory_search_with_experience("query")
3. Response includes:
   - results[]: Ranked concepts/traces by semantic similarity
   - reasoning.relevant_strategies[]: Transferable strategies for prompt injection
   - reasoning.learned_from: Count of experiences informing this search
4. Inject strategies into context for improved task performance
```

#### Pattern 4: Store Learnings to Memory
```
1. Use ingester_ingest for auto-classification and entity extraction
2. Store: mcp__haios-memory__ingester_ingest(content, source_path, content_type_hint)
3. content_type_hint: "episteme" (facts), "techne" (how-to), "doxa" (opinions), or "unknown" (auto)
4. Provides provenance tracking automatically
```
NOTE: `memory_store` is DEPRECATED. Use `ingester_ingest` instead.

### Configuration

MCP servers are configured in your environment, not in project files.

### API/Interface

Refer to individual MCP guide files:
- @.claude/mcp/context7_mcp.md - Library documentation
- @.claude/mcp/ide_mcp.md - VS Code integration
- @.claude/mcp/haios_memory_mcp.md - HAIOS cognitive memory

## Reference

### Directory Structure
```
.claude/mcp/
├── README.md              # This file
├── context7_mcp.md        # Context7 documentation guide
├── ide_mcp.md             # IDE integration guide
└── haios_memory_mcp.md    # HAIOS cognitive memory guide
```

### Dependencies

#### Runtime Dependencies
- Claude Code CLI with MCP support
- Configured MCP servers in environment

#### Development Dependencies
- None (MCP is runtime-only)

### Integration Points

#### Used By
- Claude during code sessions for documentation lookup
- Claude for IDE diagnostics and code execution

## Troubleshooting

### Common Issues

#### Issue: MCP tools not appearing
**Symptoms:** `mcp__*` tools missing from tool list
**Solution:** Check MCP server configuration in your environment

#### Issue: Context7 library not found
**Symptoms:** resolve-library-id returns no results
**Solution:** Try variations of the library name or check Context7 availability

### Debug Commands
```bash
# List all available tools
claud code --list-tools

# Check for MCP tools
claud code --list-tools | grep mcp__
```

### Getting Help
- **Documentation:** Individual guide files in this directory
- **MCP Framework:** @.claude/mcp/README.md
- **Support:** Check Claude Code documentation

## Appendix

### Recent Changes
- **2025-12-09:** Added schema_info and db_query MCP tools for database abstraction (Session 53)
- **2025-12-07:** Version 2.0 - Expanded HAIOS Memory tools (8 total), hooks integration, ReasoningBank patterns
- **2025-12-05:** ReasoningBank loop closed - strategy injection via UserPromptSubmit hook
- **2025-11-26:** Added HAIOS Memory MCP server (project-local)
- **2025-09-23:** Initial MCP framework setup
- **2025-09-23:** Added Context7 and IDE MCP guides

### Related Documentation
- @.claude/mcp/context7_mcp.md - Context7 usage patterns
- @.claude/mcp/ide_mcp.md - IDE tool constraints
- @.claude/mcp/haios_memory_mcp.md - HAIOS memory patterns
- @docs/MCP_INTEGRATION.md - Full MCP integration guide
- @CLAUDE.md - MCP integration section

---
*Generated from template: @templates/readme_template.md*
*MCP Framework Documentation v2.0*
*Last Updated: 2025-12-09 (Session 54 - README sync)*