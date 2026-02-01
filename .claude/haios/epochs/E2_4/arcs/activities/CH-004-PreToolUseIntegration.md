# generated: 2026-02-01
# System Auto: last updated on: 2026-02-01T14:56:52
# Chapter: PreToolUseIntegration

## Definition

**Chapter ID:** CH-004
**Arc:** activities
**Status:** Complete
**Session:** 270
**Depends:** CH-001 ActivityMatrix, CH-002 StateDefinitions, CH-003 GovernanceRules
**Completes:** Activities arc

---

## Problem

The ActivityMatrix (CH-001), StateDefinitions (CH-002), and GovernanceRules (CH-003) define 102 governance rules across 17 primitives and 6 states. These exist only as documentation. The PreToolUse hook has no state-awareness - it checks tool + path, not tool + state.

**Goal:** Wire the governed activities system into the PreToolUse hook to enforce state-aware governance at runtime.

---

## Solution

### Components Implemented

| Component | Location | Purpose |
|-----------|----------|---------|
| `activity_matrix.yaml` | `.claude/haios/config/` | O(1) lookup rules (17 primitives × 6 states) |
| `get_activity_state()` | `governance_layer.py:308` | Returns current state from `just get-cycle` |
| `map_tool_to_primitive()` | `governance_layer.py:350` | Maps tool names to primitives |
| `check_activity()` | `governance_layer.py:394` | Evaluates rule, returns GateResult |
| `_check_skill_restriction()` | `governance_layer.py:445` | DO-phase skill blocklist |
| `_load_activity_matrix()` | `governance_layer.py:484` | Caches YAML config |
| `_check_governed_activity()` | `pre_tool_use.py:133` | Hook integration point |

### Integration Flow

```
PreToolUse hook receives tool invocation
    |
    +-> _check_governed_activity(tool_name, tool_input)
            |
            +-> GovernanceLayer.get_activity_state()
            |       Uses: just get-cycle
            |       Returns: EXPLORE/DESIGN/PLAN/DO/CHECK/DONE
            |
            +-> GovernanceLayer.map_tool_to_primitive()
            |       Maps: AskUserQuestion -> "user-query"
            |
            +-> GovernanceLayer.check_activity(primitive, state, context)
            |       Loads: activity_matrix.yaml (cached)
            |       Evaluates: rules[primitive][state]
            |       Returns: GateResult(allowed, reason)
            |
            +-> Returns: None (allow) | _deny() | _allow_with_warning()
```

### Key Behaviors

| State | Blocked Primitives | Message |
|-------|-------------------|---------|
| DO | user-query | "DO phase is black-box. Spec should be complete - no user queries." |
| DO | memory-search | "DO phase is black-box. Query memory during EXPLORE/DESIGN." |
| DO | web-fetch, web-search | "DO phase is black-box. Web research belongs in EXPLORE." |
| DO | memory-store | "Memory storage not allowed in DO phase." |

### Skill Restrictions (DO Phase)

| Allowed | Blocked |
|---------|---------|
| validate, status, implement, schema, tree | critique, reason, new-*, close |

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Fail-open default | Unknown primitive/state → allow | Per CH-002: fail-permissive prevents halting all work |
| Cache activity_matrix.yaml | Instance attribute, load once | Performance: hook called every tool invocation |
| Check governed activity FIRST | Before SQL/PowerShell checks | State-based blocking is highest priority |
| subprocess for state detection | `just get-cycle` | Avoids circular imports; hook outside module hierarchy |
| Module-first imports | Import GovernanceLayer from modules | Per E2-264 Strangler Fig pattern |

---

## Tests

8 unit tests in `tests/test_governance_layer.py::TestGovernedActivities`:

1. `test_get_activity_state_returns_state_from_cycle` - Parses cycle/phase to state
2. `test_get_activity_state_returns_explore_when_no_cycle` - Fail-permissive on empty
3. `test_map_tool_to_primitive_maps_askuser_to_user_query` - Tool→primitive mapping
4. `test_check_activity_blocks_user_query_in_do` - DO blocks user-query
5. `test_check_activity_allows_user_query_in_explore` - EXPLORE allows user-query
6. `test_check_activity_allows_unknown_primitive` - Fail-open for unknowns
7. `test_skill_restriction_blocks_critique_in_do` - Skill blocklist works
8. `test_skill_restriction_allows_validate_in_do` - Skill allowlist works

All 8 tests pass. Full governance test suite: 40 tests pass.

---

## Artifacts Created

| Artifact | Path |
|----------|------|
| Activity Matrix Config | `.claude/haios/config/activity_matrix.yaml` |
| GovernanceLayer Methods | `.claude/haios/modules/governance_layer.py` (lines 305-494) |
| PreToolUse Integration | `.claude/hooks/hooks/pre_tool_use.py` (lines 71-75, 133-183) |
| Unit Tests | `tests/test_governance_layer.py::TestGovernedActivities` |
| justfile Recipe | `just get-cycle` (lines 295-296) |

---

## Exit Criteria

- [x] `activity_matrix.yaml` created with O(1) lookup structure
- [x] GovernanceLayer methods implemented (5 methods)
- [x] PreToolUse hook integration complete
- [x] Unit tests pass (8/8)
- [x] Full test suite shows no regressions (40 governance tests pass)
- [x] Demo verified: DO phase blocks user-query, web-fetch, memory-search

---

## Memory Refs

Session 265 governed activities decision: 82706-82710
Session 269 GovernanceRules design: 82798-82803
Session 270 implementation: (to be added after ingester_ingest)

---

## References

- @.claude/haios/epochs/E2_4/arcs/activities/CH-001-ActivityMatrix.md
- @.claude/haios/epochs/E2_4/arcs/activities/CH-002-StateDefinitions.md
- @.claude/haios/epochs/E2_4/arcs/activities/CH-003-GovernanceRules.md
- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ACTIVITY-001, REQ-ACTIVITY-002)
- @docs/work/active/WORK-042/WORK.md
- @docs/work/active/WORK-042/plans/PLAN.md
