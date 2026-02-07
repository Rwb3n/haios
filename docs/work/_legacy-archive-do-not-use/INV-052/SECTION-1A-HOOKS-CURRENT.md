# generated: 2025-12-29
# System Auto: last updated on: 2025-12-29T23:25:08
# Section 1A: Hooks - Current State

Generated: 2025-12-29 (Session 149)
Purpose: Document current hook architecture before redesign

---

## Current Structure

```
.claude/
├── hooks/
│   ├── hook_dispatcher.py      ← monolithic router
│   ├── hooks/
│   │   ├── user_prompt_submit.py   ← 7 hardcoded responsibilities
│   │   ├── pre_tool_use.py         ← 7 hardcoded checks
│   │   ├── post_tool_use.py        ← 7 hardcoded side effects
│   │   └── stop.py                 ← 1 responsibility
│   ├── memory_retrieval.py
│   └── reasoning_extraction.py
├── lib/                        ← shared modules (scattered)
├── config/
│   └── governance-toggles.yaml ← only 1 toggle exists
└── settings.local.json         ← hook registration
```

---

## Current Handler Inventory

### UserPromptSubmit (7 responsibilities)
1. datetime_context - inject date/time
2. context_threshold - warn at 80%
3. slim_status_refresh - refresh status before read
4. vitals_inject - inject milestone, session delta
5. dynamic_thresholds - APPROACHING/BOTTLENECK alerts
6. lifecycle_guidance - ADR-034 nudges
7. rfc2119_reminders - MUST governance

### PreToolUse (7 checks)
1. sql_blocking - block direct SQL
2. powershell_blocking - block PowerShell through bash
3. plan_validation - require backlog_id
4. memory_ref_warning - warn on missing refs
5. backlog_id_uniqueness - prevent duplicates
6. exit_gates - check node transition criteria
7. path_governance - force slash commands

### PostToolUse (7 side effects)
1. error_capture - store failures to memory
2. timestamp_injection - add timestamps to files
3. template_validation - validate governed docs
4. artifact_refresh - refresh status on skill/agent changes
5. cycle_transition_logging - log phase changes
6. investigation_sync - sync INV status on archive
7. scaffold_on_entry - suggest scaffolds on node change

### Stop (1 responsibility)
1. reasoning_extraction - extract learnings to memory

---

## Problems

1. **Monolithic** - All logic in single files per hook
2. **Hardcoded** - No way to enable/disable individual handlers
3. **No config** - No per-handler configuration
4. **Scattered writes** - PostToolUse writes to 4+ different locations
5. **Session-centric** - Hooks don't know which work item is active
