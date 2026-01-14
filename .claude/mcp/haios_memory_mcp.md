---
template: guide
status: active
date: 2025-11-26
type: mcp
guide_name: haios_memory_mcp
mcp_name: haios-memory
version: 1.0
---
# generated: 2025-11-26
# System Auto: last updated on: 2025-11-26 21:12:49

# HAIOS Memory MCP

## Critical Constraints
- **Requires embeddings** - Vector search only works for artifacts with embeddings
- **API key required** - `GOOGLE_API_KEY` for embedding generation
- **Cold start latency** - First query loads sqlite-vec extension (~200ms)

## Gotchas
- Empty results with 0 embeddings - Run `scripts/generate_embeddings.py` first
- `GOOGLE_API_KEY not found` - Set in `.env` file
- `Database not found` - Check `DB_PATH` in `.mcp.json`
- Missing sqlite-vec - Graceful fallback returns empty results

## Quick Patterns

### Check System Health
```
1. mcp__haios-memory__memory_stats
2. Verify status is "online"
3. Check embeddings > 0 for vector search
```

### Semantic Search
```
1. mcp__haios-memory__memory_search_with_experience("your query")
2. Results sorted by similarity (higher score = better match)
3. Returns top 10 with file_path and score
```

### Scoped Search
```
1. mcp__haios-memory__memory_search_with_experience("query", "space_id")
2. Filters results by space_id column
3. Useful for multi-tenant or context-specific queries
```

## Response Format

### memory_stats
```json
{
  "artifacts": 625,
  "entities": 6046,
  "embeddings": 468,
  "status": "online"
}
```

### memory_search_with_experience
```json
{
  "results": [{"id": 60, "file_path": "...", "score": 0.65}],
  "reasoning": {
    "outcome": "success",
    "strategy_used": "default_hybrid",
    "execution_time_ms": 266
  }
}
```

## Error Handling
| Error | Cause | Solution |
|-------|-------|----------|
| Empty results | No embeddings | Run generate_embeddings.py |
| API key error | Missing env var | Set GOOGLE_API_KEY in .env |
| Database error | Wrong path | Check .mcp.json DB_PATH |

## Grounding References (REQUIRED)
- MCP Framework: @.claude/mcp/README.md
- Integration Guide: @docs/MCP_INTEGRATION.md

---
*HAIOS Memory: Cognitive retrieval for AI agents*
