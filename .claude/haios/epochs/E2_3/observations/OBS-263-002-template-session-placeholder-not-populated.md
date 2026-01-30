---
id: OBS-263-002
title: Investigation template session number not populated by scaffold
session: 263
date: 2026-01-30
work_id: WORK-036
dimension: infrastructure
priority: low
status: pending
generated: 2026-01-30
last_updated: '2026-01-30T19:29:33'
---
# OBS-263-002: Investigation template session number not populated by scaffold

## What Happened

When WORK-036 investigation was created in Session 262, the investigation document at:
`docs/work/active/WORK-036/investigations/001-investigation-template-vs-explore-agent-effectiveness.md`

Had `session: 247` in frontmatter instead of `session: 262`.

This required manual correction:
```
session: 247  # Wrong
→
session: 263  # Fixed during this session
```

## Root Cause

The investigation template has `session: {{SESSION}}` placeholder, but the scaffold doesn't read the current session number from `.claude/session`.

## Impact

Low - cosmetic issue. Session tracker in document body also showed wrong session.

## Potential Fix

Update scaffold.py to read session number from `.claude/session` when populating investigation templates:
```python
def get_current_session():
    with open('.claude/session') as f:
        lines = f.readlines()
        # Last non-empty line is current session
        return int(lines[-1].strip())
```

---

## Related

- Scaffold library: `.claude/haios/lib/scaffold.py`
- Investigation template: `.claude/templates/investigation.md`
