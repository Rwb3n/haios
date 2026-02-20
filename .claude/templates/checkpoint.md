---
template: checkpoint
session: {{SESSION}}
prior_session: {{PREV_SESSION}}
date: {{DATE}}
work_id: {{WORK_ID}}
plan_ref: {{PLAN_REF}}

load_principles: []
# Add principles relevant to pending work (coldstart injects these)

load_memory_refs: []
# Populate with concept IDs from this session's ingester_ingest calls

# What's pending for next session
pending: []

# Drift from principles observed this session (if any)
drift_observed: []

# Work completed this session (for git log, not for next session)
completed: []
---
