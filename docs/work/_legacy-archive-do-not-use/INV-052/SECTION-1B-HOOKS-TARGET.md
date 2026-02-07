# generated: 2025-12-29
# System Auto: last updated on: 2025-12-30T22:22:07
# Section 1B: Hooks - Target Architecture

Generated: 2025-12-29 (Session 149)
Purpose: Normalized, configurable, extensible hook system

---

## Target Structure

```
.claude/haios/                      ← HAIOS plugin home
├── hooks/
│   ├── dispatcher.py               ← thin router, loads config
│   ├── hook-handlers.yaml          ← handler registry + config
│   └── handlers/                   ← individual handler modules
│       ├── datetime_context.py
│       ├── work_context_inject.py  ← NEW
│       ├── work_item_gate.py       ← NEW
│       ├── work_item_state_update.py ← NEW
│       └── ...
├── lib/                            ← shared modules
├── config/
│   ├── hook-handlers.yaml
│   ├── cycle-definitions.yaml
│   ├── gates.yaml
│   └── thresholds.yaml
└── haios-status*.json              ← moved from .claude/
```

---

## Final Handler Count (After Consolidation)

| Hook | Original | Final | Change |
|------|----------|-------|--------|
| UserPromptSubmit | 7 | 7 | work_context_inject replaces lifecycle_guidance |
| PreToolUse | 7 | 5 | work_item_gate consolidates 3 handlers |
| PostToolUse | 7 | 5 | work_item_state_update consolidates 3 handlers |
| Stop | 1 | 2 | +work_item_incomplete_mark |
| **Total** | **22** | **19** | **-3** |

---

## Key New Handlers

### work_context_inject (UserPromptSubmit)
Injects active work item state, node, phase, next gate.

### work_item_gate (PreToolUse)
Work-item-aware gating. Validates edits against current node. Checks exit gates on transitions.

### work_item_state_update (PostToolUse)
Single writer to WORK.md node_history. Records transitions, gate results, memory_refs.

### work_item_incomplete_mark (Stop)
Marks node_history entry as incomplete on session end/crash.

---

## Configuration: hook-handlers.yaml

```yaml
user_prompt_submit:
  - handler: datetime_context
    priority: 10
    enabled: true
  - handler: context_threshold
    priority: 20
    config:
      warn_at: 80
      force_checkpoint_at: 90
  - handler: work_context_inject
    priority: 30
    enabled: true
  # ... (7 total)

pre_tool_use:
  - handler: sql_blocking
    priority: 10
  - handler: work_item_gate
    priority: 20
    config:
      strict_mode: false
      nodes:
        backlog:
          allowed_edits: [WORK.md]
          exit_gate: null
        discovery:
          allowed_edits: [WORK.md, "investigations/*"]
          exit_gate: investigation_complete
        plan:
          allowed_edits: [WORK.md, "plans/*"]
          exit_gate: plan_approved
        implement:
          allowed_edits: [WORK.md, "plans/*", "**/*"]
          exit_gate: tests_pass_and_why_captured
        close:
          allowed_edits: [WORK.md, "observations/*"]
          exit_gate: dod_validated
  # ... (5 total)

post_tool_use:
  - handler: work_item_state_update
    priority: 10
  - handler: timestamp_injection
    priority: 20
  # ... (5 total)

stop:
  - handler: reasoning_extraction
    priority: 10
  - handler: work_item_incomplete_mark
    priority: 20
```

---

## Dispatcher Logic

```python
def dispatch(hook_data: dict) -> Optional[str | dict]:
    config = load_config("hook-handlers.yaml")
    handlers = get_enabled_handlers(config, hook_data["hook_event_name"])

    for handler in sorted(handlers, key=lambda h: h["priority"]):
        result = handler.handle(hook_data, handler.get("config", {}))
        if result and is_deny(result):
            return result  # Short-circuit on PreToolUse DENY

    return combine_results(results)
```

---

## Single Writer Principle

**PostToolUse** is the only writer to WORK.md node_history:
- Records node transitions
- Records gate results
- Records outcomes
- Links memory_refs
- Marks recovery_from on crash recovery
