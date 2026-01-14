---
template: guide
status: active
date: 2025-09-23
type: mcp
guide_name: ide_mcp
mcp_name: ide
version: 1.0
---
# generated: 2025-09-23
# System Auto: last updated on: 2025-09-23 16:14:51

# IDE MCP

## Critical Constraints
- **getDiagnostics** requires file to be open/analyzed in VS Code
- **executeCode** only works in Jupyter notebook context
- File URIs must use: `file:///d:/path/to/file` format

## Gotchas
- ❌ getDiagnostics on unopened file - Returns empty array
- ❌ executeCode outside notebook - Will fail
- ❌ Using backslashes in URI - Use forward slashes
- ✅ Check file is open in VS Code before getDiagnostics

## Quick Patterns

### Get TypeScript Errors
```
1. Ensure file is open in VS Code
2. mcp__ide__getDiagnostics("file:///d:/project/file.ts")
3. Parse diagnostics array for errors/warnings
```

### Execute Notebook Code
```
1. Confirm in Jupyter notebook context
2. mcp__ide__executeCode("import pandas as pd")
3. Code persists across calls unless kernel restarted
```

### Get All Diagnostics
```
mcp__ide__getDiagnostics()  // No URI = all open files
```

## Error Handling
| Error | Cause | Solution |
|-------|-------|----------|
| Empty diagnostics | File not analyzed | Open file in VS Code first |
| executeCode fails | Not in notebook | Use only in .ipynb files |

## Grounding References (REQUIRED)
- MCP Framework: `@.claude/mcp/README.md`

---
*IDE MCP: VS Code integration tools*