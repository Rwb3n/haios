# generated: 2025-12-05
# System Auto: last updated on: 2025-12-05 20:57:11
# MCP Integration Guide (PROPOSED UPDATE)

> **Progressive Disclosure:** [Quick Reference](README.md) -> [Strategic Overview](epistemic_state.md) -> **MCP Integration (YOU ARE HERE)**
>
> **Navigation:** [Vision](VISION_ANCHOR.md) | [Operations](OPERATIONS.md) | [Schema](specs/memory_db_schema_v3.sql)

---

## Quick Reference

| Tool | Purpose |
|------|---------|
| `memory_search_with_experience` | Hybrid search with ReasoningBank learning |
| `memory_stats` | Database statistics |
| `marketplace_list_agents` | List available agents |
| `marketplace_get_agent` | Get agent details |
| `memory_store` | Store content with Greek Triad classification |
| `extract_content` | Extract entities and concepts from text |
| `interpreter_translate` | Translate operator intent to system directive |
| `ingester_ingest` | Ingest content with auto-classification |

---

This guide explains how to integrate the `haios-memory` MCP server with your agent ecosystem (e.g., Claude Desktop).

## Prerequisites
-   Python 3.10+
-   `haios` project setup with dependencies installed (`pip install -r requirements.txt`)
-   `GOOGLE_API_KEY` set in your environment or `.env` file.

## Configuration

To use the `haios-memory` server, add the following configuration to your MCP client config (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "haios-memory": {
      "command": "python",
      "args": [
        "-m",
        "haios_etl.mcp_server"
      ],
      "cwd": "D:\\PROJECTS\\haios",
      "env": {
        "GOOGLE_API_KEY": "your-api-key-here",
        "DB_PATH": "D:\\PROJECTS\\haios\\haios_memory.db"
      }
    }
  }
}
```

**Note:** Replace `D:\\PROJECTS\\haios` with the actual absolute path to your project if different.

## Available Tools

### Core Memory Tools

#### `memory_search_with_experience(query, space_id=None)`
Searches the memory database using a hybrid approach (Vector + Metadata) and learns from past reasoning traces via ReasoningBank.

**Parameters:**
-   **query** (string): The search query string.
-   **space_id** (string, optional): Optional identifier for the context (e.g., 'dev_copilot', 'salesforce').

**Returns:** JSON containing search results and reasoning trace.

**Example:**
```python
result = memory_search_with_experience(
    query="What are the key architectural decisions?",
    space_id="dev_copilot"
)
```

---

#### `memory_stats()`
Returns comprehensive statistics about the memory database.

**Returns:** JSON object with:
- Artifact count
- Entity count
- Concept count
- Embedding coverage
- Agent registry status
- Database path
- System status

---

### Agent Marketplace Tools

#### `marketplace_list_agents(capability=None)`
Lists all available agents in the marketplace, with optional filtering by capability.

**Parameters:**
-   **capability** (string, optional): Filter by capability (e.g., 'vision-alignment', 'knowledge-classification')

**Returns:** Formatted markdown list of agents with IDs, descriptions, and capabilities.

---

#### `marketplace_get_agent(agent_id)`
Retrieves full details for a specific agent including its input/output schema.

**Parameters:**
-   **agent_id** (string): The ID of the agent to retrieve (e.g., 'agent-interpreter-001')

**Returns:** JSON object containing complete agent card with schema definitions.

---

### Content Ingestion Tools

#### `memory_store(content, content_type, source_path, metadata=None)`
Stores content in memory with Greek Triad classification (episteme/techne/doxa).

**Parameters:**
-   **content** (string): The content to store
-   **content_type** (string): Classification - one of 'episteme' (knowledge/facts), 'techne' (practical skills/how-to), or 'doxa' (opinions/beliefs)
-   **source_path** (string): Source file path for provenance tracking
-   **metadata** (string, optional): JSON string with additional metadata

**Returns:** Confirmation message with stored concept ID.

**Example:**
```python
memory_store(
    content="SQLite uses WAL mode for concurrent access",
    content_type="episteme",
    source_path="docs/ADR/ADR-023.md",
    metadata='{"category": "database", "confidence": 0.95}'
)
```

---

#### `extract_content(file_path, content, extraction_mode="full")`
Extracts entities and concepts from content using LangExtract-based LLM extraction.

**Parameters:**
-   **file_path** (string): Path to the source file (for context and provenance)
-   **content** (string): The text content to extract from
-   **extraction_mode** (string): Mode of extraction - 'full' (default), 'entities_only', or 'concepts_only'

**Returns:** JSON containing extracted entities and concepts with summary counts.

---

### Agent Ecosystem Tools

#### `interpreter_translate(intent)`
Translates natural language operator intent into structured system directives using the Interpreter agent.

**Parameters:**
-   **intent** (string): Natural language intent (e.g., "find all ADRs about security")

**Returns:** JSON containing:
- `directive`: Structured system directive
- `confidence`: 0.0-1.0 confidence score
- `grounded`: Whether relevant context was found
- `context_used`: Memory items used for grounding

**Example:**
```python
interpreter_translate("Show me all concepts related to vector embeddings")
```

---

#### `ingester_ingest(content, source_path, content_type_hint="unknown")`
Ingests content into memory with automatic Greek Triad classification using the Ingester agent.

**Parameters:**
-   **content** (string): The text content to ingest
-   **source_path** (string): Source file path for provenance tracking
-   **content_type_hint** (string): Classification hint - 'episteme', 'techne', 'doxa', or 'unknown' (auto-classify)

**Returns:** JSON containing:
- `concept_ids`: IDs of stored concepts
- `entity_ids`: IDs of stored entities
- `classification`: Final classification (episteme/techne/doxa)
- `ingested_by_agent`: Agent ID for provenance

---

## Tool Usage Patterns

### Search and Retrieval
Use `memory_search_with_experience` for intelligent search that learns from past queries.

### Content Classification
For manual control, use `memory_store` with explicit content_type.
For automatic classification, use `ingester_ingest` which leverages LLM classification.

### Agent Discovery
Use `marketplace_list_agents` to discover available capabilities, then `marketplace_get_agent` for detailed schemas.

### Intent Translation
Use `interpreter_translate` to convert natural language queries into structured directives for automated workflows.

---

## Troubleshooting

-   **Error: "GOOGLE_API_KEY not found"**: Ensure the environment variable is passed correctly in the `env` section of the config.
-   **Error: "Database not found"**: Verify `DB_PATH` points to the correct `haios_memory.db` file.
-   **Error: "Invalid content_type"**: Ensure content_type is one of: episteme, techne, doxa.
-   **Logs**: Check the MCP client logs for detailed error messages.
-   **Agent errors**: If Interpreter/Ingester tools fail, verify agent registry is populated (run `python scripts/register_agents.py`).

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| [Quick Reference](README.md) | Documentation map |
| [Strategic Overview](epistemic_state.md) | System state, knowns/unknowns |
| [Operations](OPERATIONS.md) | ETL runbook |
| [Vision Anchor](VISION_ANCHOR.md) | Architectural vision (ReasoningBank + LangExtract) |
| [System Spec](COGNITIVE_MEMORY_SYSTEM_SPEC.md) | Full specification |
| [Agent Ecosystem Plan](plans/PLAN-AGENT-ECOSYSTEM-001-phase-2.md) | Agent architecture details |

---

*Last Updated: 2025-12-05*
