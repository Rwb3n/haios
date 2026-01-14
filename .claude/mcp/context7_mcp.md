---
template: guide
status: active
date: 2025-09-23
type: mcp
guide_name: context7_mcp
mcp_name: context7
version: 1.0
---
# generated: 2025-09-23
# System Auto: last updated on: 2025-09-23 16:14:17

# Context7 MCP

## Critical Constraints
- **ALWAYS call resolve-library-id first** - Never guess library IDs
- Token parameter is a suggestion, not hard limit (50 tokens → still returns lots)
- Returns ~30 results even for nonsense queries - check trust scores

## Gotchas
- ❌ `get-library-docs("/react/react")` - Guessed ID will fail
- ❌ Assuming first result is best - Check trust score + snippet count
- ❌ Using token < 500 - Too little for useful content
- ✅ `resolve-library-id` → select by trust → `get-library-docs`

## Quick Patterns

### Get React Docs
```
1. mcp__context7__resolve-library-id("react")
2. Select: /websites/react_dev (Trust: 8, Snippets: 1752)
3. mcp__context7__get-library-docs("/websites/react_dev", 2000, "hooks")
```

### Get Specific Version
```
1. resolve-library-id("react-router")
2. Note versions array in results
3. get-library-docs("/remix-run/react-router/7.6.2")
```

## Trust Score Guide
| Score | Action |
|-------|--------|
| 9-10 | Use confidently |
| 7-8 | Good quality |
| 5-6 | Use with caution |
| <5 | Avoid unless necessary |

## Error Handling
| Error | Cause | Solution |
|-------|-------|----------|
| "library...does not exist" | Invalid ID | Go back to resolve-library-id |
| No good matches | All trust < 5 | Try alternative search terms |

## Grounding References (REQUIRED)
- MCP Framework: `@.claude/mcp/README.md`

---
*Context7: Documentation retrieval for any library*