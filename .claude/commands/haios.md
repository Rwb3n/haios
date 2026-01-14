---
allowed-tools: Read, Bash, mcp__haios-memory__memory_stats
description: Show HAIOS system status and active infrastructure
generated: 2025-12-22
last_updated: 2025-12-22T12:38:59
---

# HAIOS System Status

Ref: @.claude/haios-status.json

1. **Refresh Status** (auto-update from all sources):
   ```
   just update-status-slim
   ```

2. Read the refreshed `.claude/haios-status.json`

3. **Query Live Memory Stats** (E2-026):
   Call `mcp__haios-memory__memory_stats` to get real-time counts (may differ from cached JSON)

4. Display dashboard with ALL sections from the JSON + live memory stats:

```
HAIOS System Status (Live)
==========================
Last Updated: <last_updated from JSON>

HOOKS
-----
PreToolUse:    <features from JSON>
UserPromptSubmit: <features from JSON>
PostToolUse:   <features from JSON>
Stop:          <features from JSON>

MEMORY SYSTEM (Live from memory_stats)
--------------------------------------
Concepts:      <from memory_stats>
Entities:      <from memory_stats>
Artifacts:     <from memory_stats>
Traces:        <from memory_stats>
MCP Server:    haios-memory

PROJECT MANAGEMENT
------------------
Active Items:  <pm.active_count>
Last Session:  <pm.last_session>
Priority:      Urgent:<urgent> High:<high> Med:<medium> Low:<low>

LIFECYCLE (Live Files in Transit)
---------------------------------
Total:         <live_files count>
By Status:     <counts_by_status breakdown>
Alignment:     <alignment_issues count or "OK">

AGENTS & SKILLS
---------------
Agents:        <agents list>
Skills:        <skills list>

VALID TEMPLATES
---------------
<valid_templates list>
```

4. If alignment_issues exist, list them as warnings.
