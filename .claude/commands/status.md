---
allowed-tools: Bash, Read
description: Show HAIOS system health (tests, memory, validation, git)
generated: '2026-01-05'
last_updated: '2026-01-05T21:10:25'
---

# System Status

Run the following diagnostics:

1. **Tests:** `pytest --collect-only -q 2>/dev/null | tail -1`
2. **Memory:** Query haios_memory.db for concept count
3. **Git:** `git status --short`
4. **Session:** Extract from latest checkpoint filename in `docs/checkpoints/`
5. **Health Check:** Run health check:
   ```
   just health
   ```

Present as a compact dashboard:
```
HAIOS Status
============
Tests:      <count>
Memory:     <count> concepts
Git:        <count> modified
Session:    <number>
```
