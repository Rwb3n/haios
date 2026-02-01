---
template: implementation_plan
status: complete
date: 2026-02-01
backlog_id: WORK-042
title: CH-004 PreToolUseIntegration Implementation
author: Hephaestus
lifecycle_phase: plan
session: 270
version: '1.5'
generated: 2025-12-21
last_updated: '2026-02-01T14:58:19'
---
# Implementation Plan: CH-004 PreToolUseIntegration Implementation

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

PreToolUse hook enforces state-aware governed activities by calling GovernanceLayer.check_activity() to block, warn, or allow operations based on current workflow state (EXPLORE/DESIGN/PLAN/DO/CHECK/DONE) per the ActivityMatrix rules.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/haios/modules/governance_layer.py`, `.claude/hooks/hooks/pre_tool_use.py` |
| Lines of code affected | ~837 total | `wc -l`: 302 + 535 |
| New files to create | 2 | `activity_matrix.yaml`, `CH-004-PreToolUseIntegration.md` |
| Tests to write | 8 | get_activity_state, map_tool_to_primitive, check_activity (3 actions), _check_skill_restriction, integration |
| Dependencies | 3 | `pre_tool_use.py` → `governance_layer.py` → `activity_matrix.yaml` |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | Hook → Module → Config; must not break existing checks |
| Risk of regression | Med | Pre-existing hook checks (SQL, PowerShell, scaffold) must continue working |
| External dependencies | Low | Only reads `just get-cycle` via subprocess, YAML config |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Config file (activity_matrix.yaml) | 30 min | High |
| GovernanceLayer methods (4 methods) | 60 min | Med |
| PreToolUse hook integration | 30 min | High |
| Tests | 45 min | Med |
| Chapter documentation | 20 min | High |
| **Total** | ~3 hr | Med |

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/hooks/pre_tool_use.py:55-90 - Current handle() function
def handle(hook_data: dict) -> Optional[dict]:
    tool_name = hook_data.get("tool_name", "")
    tool_input = hook_data.get("tool_input", {})

    # Check Bash for SQL and PowerShell
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        result = _check_sql_governance(command)
        if result: return result
        result = _check_powershell_governance(command)
        if result: return result
        result = _check_scaffold_governance(command)
        if result: return result
        return None

    # Check Write/Edit for governance
    if tool_name in ("Write", "Edit"):
        # ... existing path checks ...
        return None

    return None  # Allow all other tools
```

**Behavior:** Hook checks tool + path, but NOT tool + state. Same tool allowed regardless of workflow phase.

**Result:** Agent can use AskUserQuestion during DO phase (violates black-box), can explore during DO, no governed activities enforcement.

### Desired State

```python
# .claude/hooks/hooks/pre_tool_use.py:55-100 - With state-aware check
def handle(hook_data: dict) -> Optional[dict]:
    tool_name = hook_data.get("tool_name", "")
    tool_input = hook_data.get("tool_input", {})

    # NEW: State-aware governed activity check (E2.4 CH-004)
    result = _check_governed_activity(tool_name, tool_input)
    if result:
        return result

    # Existing checks follow...
    if tool_name == "Bash":
        # ... existing checks ...
```

**Behavior:** Hook checks tool + state FIRST via GovernanceLayer.check_activity(). Returns block/warn based on ActivityMatrix rules.

**Result:** Agent blocked from using AskUserQuestion in DO phase, blocked from web-fetch during implementation, governed activities enforced per CH-001 matrix.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: get_activity_state returns state from cycle
```python
def test_get_activity_state_returns_state_from_cycle(mocker):
    """get_activity_state parses cycle/phase and maps to ActivityMatrix state."""
    from governance_layer import GovernanceLayer

    # Mock subprocess to return "implementation-cycle/DO/WORK-042"
    mocker.patch("governance_layer.subprocess.run", return_value=mocker.Mock(
        stdout="implementation-cycle/DO/WORK-042", returncode=0
    ))

    layer = GovernanceLayer()
    state = layer.get_activity_state()

    assert state == "DO"
```

### Test 2: get_activity_state returns EXPLORE on empty cycle
```python
def test_get_activity_state_returns_explore_when_no_cycle(mocker):
    """get_activity_state returns EXPLORE when no cycle active (fail-permissive)."""
    from governance_layer import GovernanceLayer

    mocker.patch("governance_layer.subprocess.run", return_value=mocker.Mock(
        stdout="", returncode=1
    ))

    layer = GovernanceLayer()
    state = layer.get_activity_state()

    assert state == "EXPLORE"
```

### Test 3: map_tool_to_primitive maps tools correctly
```python
def test_map_tool_to_primitive_maps_askuser_to_user_query():
    """map_tool_to_primitive converts tool name to primitive."""
    from governance_layer import GovernanceLayer

    layer = GovernanceLayer()

    assert layer.map_tool_to_primitive("AskUserQuestion", {}) == "user-query"
    assert layer.map_tool_to_primitive("Read", {}) == "file-read"
    assert layer.map_tool_to_primitive("Write", {}) == "file-write"
    assert layer.map_tool_to_primitive("WebFetch", {}) == "web-fetch"
```

### Test 4: check_activity blocks user-query in DO
```python
def test_check_activity_blocks_user_query_in_do():
    """check_activity returns blocked for user-query in DO state."""
    from governance_layer import GovernanceLayer

    layer = GovernanceLayer()
    result = layer.check_activity("user-query", "DO", {})

    assert result.allowed is False
    assert "black-box" in result.reason.lower() or "blocked" in result.reason.lower()
```

### Test 5: check_activity allows user-query in EXPLORE
```python
def test_check_activity_allows_user_query_in_explore():
    """check_activity returns allowed for user-query in EXPLORE state."""
    from governance_layer import GovernanceLayer

    layer = GovernanceLayer()
    result = layer.check_activity("user-query", "EXPLORE", {})

    assert result.allowed is True
```

### Test 6: check_activity handles unknown primitive (fail-open)
```python
def test_check_activity_allows_unknown_primitive():
    """check_activity returns allowed for unknown primitive (fail-open per CH-003)."""
    from governance_layer import GovernanceLayer

    layer = GovernanceLayer()
    result = layer.check_activity("unknown-primitive", "DO", {})

    assert result.allowed is True
```

### Test 7: _check_skill_restriction blocks critique in DO
```python
def test_skill_restriction_blocks_critique_in_do():
    """_check_skill_restriction blocks design-phase skills in DO."""
    from governance_layer import GovernanceLayer

    layer = GovernanceLayer()
    result = layer._check_skill_restriction("critique", "DO")

    assert result is not None
    assert result.allowed is False
```

### Test 8: Backward Compatibility - existing checks still work
```python
def test_existing_sql_check_still_works(mocker):
    """Existing SQL governance check continues to work after integration."""
    # Import after mocking
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "hooks" / "hooks"))

    from pre_tool_use import handle

    # SQL command should still be blocked
    result = handle({
        "tool_name": "Bash",
        "tool_input": {"command": "sqlite3 db.sqlite 'SELECT * FROM concepts'"}
    })

    assert result is not None
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does.
     Future agents should be able to implement from this section alone.

     SOURCE SPECS READ:
     - CH-001-ActivityMatrix.md (17 primitives, 6 states, 102 rules)
     - CH-002-StateDefinitions.md (state detection, phase-to-state mapping)
     - CH-003-GovernanceRules.md (rule schema, check_activity algorithm)
     - governance_layer.py (existing module patterns: sys.path, GateResult dataclass)
     - pre_tool_use.py (existing hook patterns: _deny(), _allow_with_warning())

     MEMORY RESULTS:
     - 82751: "PreToolUse hook needs state detection, primitive mapping, matrix lookup"
     - 37935: "Required checks should be in governing configuration artifact"
     - 80712: Module-first pattern - hooks import from modules, not directly from lib
-->

### Component 1: activity_matrix.yaml

**File:** `.claude/haios/config/activity_matrix.yaml`
**Purpose:** Configuration file with O(1) lookup rules per CH-003 data structure

```yaml
# .claude/haios/config/activity_matrix.yaml
# O(1) lookup: rules[primitive][state] -> rule
version: "1.0"
default_action: allow  # Fail-open for unknown primitives (CH-003 decision)

rules:
  # Category 4: Agent/Task - user-query (THE key DO-phase block)
  user-query:
    EXPLORE: {action: allow}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: block, message: "BLOCKED: DO phase is black-box. Spec should be complete - no user queries."}
    CHECK: {action: allow}
    DONE: {action: allow}

  # Category 5: Memory - memory-search blocked in DO
  memory-search:
    EXPLORE: {action: allow}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: block, message: "BLOCKED: DO phase is black-box. Query memory during EXPLORE/DESIGN."}
    CHECK: {action: allow}
    DONE: {action: allow}

  # Category 3: Web/External - blocked in DO
  web-fetch:
    EXPLORE: {action: allow}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: block, message: "BLOCKED: DO phase is black-box. Web research belongs in EXPLORE."}
    CHECK: {action: allow}
    DONE: {action: allow}

  web-search:
    EXPLORE: {action: allow}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: block, message: "BLOCKED: DO phase is black-box. Web research belongs in EXPLORE."}
    CHECK: {action: allow}
    DONE: {action: allow}

  # Full matrix per CH-003... (truncated for plan, see CH-003 for complete)

# Skill restrictions for DO phase (per CH-001 "Skill Restrictions in DO")
skill_restrictions:
  DO:
    allowed: [validate, status, implement, schema, tree]
    blocked: [critique, reason, "new-*", close]
    block_message: "BLOCKED: Skill '{skill}' not allowed in DO phase. Spec is frozen."

# Phase-to-state mapping (per CH-002)
phase_to_state:
  implementation-cycle/PLAN: PLAN
  implementation-cycle/DO: DO
  implementation-cycle/CHECK: CHECK
  implementation-cycle/DONE: DONE
  investigation-cycle/HYPOTHESIZE: DESIGN
  investigation-cycle/EXPLORE: EXPLORE
  investigation-cycle/CONCLUDE: DONE
  # ... full mapping per CH-002
```

### Component 2: GovernanceLayer Methods

**File:** `.claude/haios/modules/governance_layer.py`
**Location:** Add after line 302 (after `get_toggle` method)

```python
# =========================================================================
# E2.4 CH-004: Governed Activities (State-Aware Governance)
# =========================================================================

# Cache for activity matrix (loaded once)
_activity_matrix_cache: Optional[dict] = None

def get_activity_state(self) -> str:
    """
    Get current ActivityMatrix state from cycle/phase.

    Uses `just get-cycle` to get current cycle state, maps to ActivityMatrix state.

    Returns:
        State name: EXPLORE, DESIGN, PLAN, DO, CHECK, or DONE
        Defaults to EXPLORE on failure (fail-permissive per CH-002)
    """
    import subprocess

    try:
        result = subprocess.run(
            ["just", "get-cycle"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(Path(__file__).parent.parent.parent.parent)  # Project root
        )
        cycle_info = result.stdout.strip()

        if not cycle_info:
            return "EXPLORE"  # No cycle = discovery mode

        # Parse "cycle/phase/work_id"
        parts = cycle_info.split("/")
        if len(parts) < 2:
            return "EXPLORE"

        cycle, phase = parts[0], parts[1]

        # Load phase-to-state mapping
        matrix = self._load_activity_matrix()
        mapping = matrix.get("phase_to_state", {})
        key = f"{cycle}/{phase}"

        return mapping.get(key, "EXPLORE")

    except Exception:
        return "EXPLORE"  # Fail-permissive

def map_tool_to_primitive(self, tool_name: str, tool_input: dict) -> str:
    """
    Map Claude Code tool name to ActivityMatrix primitive.

    Args:
        tool_name: Tool name (e.g., "AskUserQuestion", "Read", "Bash")
        tool_input: Tool input dict (for context-specific mapping)

    Returns:
        Primitive name (e.g., "user-query", "file-read")
    """
    # Direct mappings
    TOOL_TO_PRIMITIVE = {
        "AskUserQuestion": "user-query",
        "Read": "file-read",
        "Write": "file-write",
        "Edit": "file-edit",
        "Glob": "file-search",
        "Grep": "content-search",
        "Bash": "shell-execute",
        "WebFetch": "web-fetch",
        "WebSearch": "web-search",
        "Task": "task-spawn",
        "Skill": "skill-invoke",
        "NotebookEdit": "notebook-edit",
        "EnterPlanMode": "plan-enter",
        "ExitPlanMode": "plan-exit",
        "ListMcpResourcesTool": "mcp-list",
        "ReadMcpResourceTool": "mcp-read",
    }

    # MCP tools
    if tool_name.startswith("mcp__haios-memory__"):
        if "search" in tool_name:
            return "memory-search"
        if "ingest" in tool_name or "store" in tool_name:
            return "memory-store"
        if "schema" in tool_name:
            return "schema-query"
        if "db_query" in tool_name:
            return "db-query"

    return TOOL_TO_PRIMITIVE.get(tool_name, "unknown")

def check_activity(self, primitive: str, state: str, context: dict) -> GateResult:
    """
    Check if activity is allowed in current state.

    Args:
        primitive: The primitive being invoked (e.g., "user-query")
        state: Current ActivityMatrix state (e.g., "DO")
        context: Additional context (file_path, skill_name, etc.)

    Returns:
        GateResult with allowed flag and reason message
    """
    matrix = self._load_activity_matrix()
    rules = matrix.get("rules", {})

    # Look up rule for (primitive, state)
    primitive_rules = rules.get(primitive, {})

    # Check _all_states shorthand first
    if "_all_states" in primitive_rules:
        rule = primitive_rules["_all_states"]
    elif state in primitive_rules:
        rule = primitive_rules[state]
    else:
        # Unknown primitive or state - use default (fail-open per CH-003)
        default = matrix.get("default_action", "allow")
        return GateResult(allowed=True, reason=f"Unknown primitive '{primitive}', defaulting to {default}")

    # Evaluate action
    action = rule.get("action", "allow")
    message = rule.get("message", "")

    if action == "allow":
        return GateResult(allowed=True, reason="Activity allowed")

    if action == "warn":
        return GateResult(allowed=True, reason=message)

    if action == "block":
        return GateResult(allowed=False, reason=message)

    if action == "redirect":
        redirect_to = rule.get("redirect_to", "alternative")
        return GateResult(allowed=False, reason=message or f"Use {redirect_to} instead")

    return GateResult(allowed=True, reason="Activity allowed")

def _check_skill_restriction(self, skill_name: str, state: str) -> Optional[GateResult]:
    """
    Check if skill is allowed in current state.

    Args:
        skill_name: Name of skill being invoked
        state: Current ActivityMatrix state

    Returns:
        None if allowed, GateResult if blocked
    """
    import fnmatch

    matrix = self._load_activity_matrix()
    restrictions = matrix.get("skill_restrictions", {}).get(state, {})

    if not restrictions:
        return None

    allowed = restrictions.get("allowed", [])
    blocked = restrictions.get("blocked", [])
    block_message = restrictions.get("block_message", "Skill not allowed in this state")

    # Check explicit allow list
    for pattern in allowed:
        if fnmatch.fnmatch(skill_name, pattern):
            return None

    # Check blocked list
    for pattern in blocked:
        if fnmatch.fnmatch(skill_name, pattern):
            return GateResult(
                allowed=False,
                reason=block_message.format(skill=skill_name)
            )

    return None  # Default: allow if not blocked

def _load_activity_matrix(self) -> dict:
    """Load and cache activity_matrix.yaml."""
    global _activity_matrix_cache

    if _activity_matrix_cache is not None:
        return _activity_matrix_cache

    config_path = Path(__file__).parent.parent / "config" / "activity_matrix.yaml"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            _activity_matrix_cache = yaml.safe_load(f) or {}
    else:
        _activity_matrix_cache = {"default_action": "allow", "rules": {}}

    return _activity_matrix_cache
```

### Component 3: PreToolUse Hook Integration

**File:** `.claude/hooks/hooks/pre_tool_use.py`
**Location:** Add new function after `_load_governance_toggles()`, call early in `handle()`

```python
def _check_governed_activity(tool_name: str, tool_input: dict) -> Optional[dict]:
    """
    Check governed activity via GovernanceLayer (E2.4 CH-004).

    State-aware governance: same tool can have different rules per workflow state.

    Returns:
        None: Allow operation
        dict: Block/warn response
    """
    try:
        # Import GovernanceLayer (module-first pattern per E2-264)
        modules_dir = Path(__file__).parent.parent.parent / "haios" / "modules"
        if str(modules_dir) not in sys.path:
            sys.path.insert(0, str(modules_dir))

        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()

        # 1. Get current state
        state = layer.get_activity_state()

        # 2. Map tool to primitive
        primitive = layer.map_tool_to_primitive(tool_name, tool_input)

        # 3. Build context
        context = {
            "file_path": tool_input.get("file_path", ""),
            "tool_input": tool_input,
        }

        # 4. Special handling for skill-invoke
        if primitive == "skill-invoke":
            skill_name = tool_input.get("skill", "")
            skill_result = layer._check_skill_restriction(skill_name, state)
            if skill_result is not None and not skill_result.allowed:
                return _deny(skill_result.reason)

        # 5. Check activity
        result = layer.check_activity(primitive, state, context)

        if not result.allowed:
            return _deny(result.reason)

        if result.reason and result.reason != "Activity allowed":
            return _allow_with_warning(result.reason)

        return None  # Allow silently

    except Exception:
        # Fail-permissive on any error
        return None
```

**Integration point in handle():**

```diff
def handle(hook_data: dict) -> Optional[dict]:
    tool_name = hook_data.get("tool_name", "")
    tool_input = hook_data.get("tool_input", {})

+   # NEW: State-aware governed activity check (E2.4 CH-004)
+   result = _check_governed_activity(tool_name, tool_input)
+   if result:
+       return result

    # Check Bash for SQL and PowerShell
    if tool_name == "Bash":
        # ... existing checks ...
```

### Call Chain Context

```
Claude Code invokes tool
    |
    +-> PreToolUse hook (pre_tool_use.py:handle)
            |
            +-> _check_governed_activity(tool_name, tool_input)  # <-- NEW
            |       |
            |       +-> GovernanceLayer.get_activity_state()
            |       |       Returns: "DO" | "EXPLORE" | etc.
            |       |
            |       +-> GovernanceLayer.map_tool_to_primitive()
            |       |       Returns: "user-query" | "file-read" | etc.
            |       |
            |       +-> GovernanceLayer.check_activity(primitive, state, context)
            |       |       Loads: activity_matrix.yaml (cached)
            |       |       Returns: GateResult(allowed, reason)
            |       |
            |       +-> Returns: None (allow) | dict (block/warn)
            |
            +-> _check_sql_governance(command)        # Existing
            +-> _check_powershell_governance(command) # Existing
            +-> ... other existing checks ...
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Check governed activity FIRST | Before SQL/PowerShell checks | State-based blocking is highest priority; if in DO, block user-query before even checking if it's SQL |
| Fail-permissive on errors | Return None (allow) on any exception | Per CH-002: "Blocking on unknown state would halt all work" |
| Cache activity_matrix.yaml | Global cache, load once | Performance: hook called every tool invocation; per CH-003 decision 82803 |
| Module-first imports | Import GovernanceLayer, not lib directly | Per memory 80712: hooks import from modules for Strangler Fig pattern |
| Use existing _deny/_allow_with_warning | Reuse hook helpers | Consistency with existing hook code patterns |
| subprocess for just get-cycle | Not importing CycleRunner | Avoid circular dependencies; hook is outside module hierarchy |

### Input/Output Examples

**Before (current system):**
```
In DO phase (implementation-cycle/DO/WORK-042):
  AskUserQuestion("Which approach?")
  Returns: Allowed (no state awareness)
  Problem: Violates black-box, spec should be complete
```

**After (with governed activities):**
```
In DO phase (implementation-cycle/DO/WORK-042):
  AskUserQuestion("Which approach?")
  Returns: {
    "hookSpecificOutput": {
      "permissionDecision": "deny",
      "permissionDecisionReason": "BLOCKED: DO phase is black-box. Spec should be complete - no user queries."
    }
  }
  Improvement: Agent must complete spec during PLAN phase
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No cycle active | Return state = EXPLORE | Test 2 |
| Unknown tool | Map to "unknown" primitive, fail-open | Test 6 |
| just get-cycle fails | Return EXPLORE (fail-permissive) | Test 2 |
| activity_matrix.yaml missing | Use empty rules, fail-open | Built into _load_activity_matrix |
| Skill in DO | Check skill_restrictions separately | Test 7 |

### Open Questions

**Q: Should we log governed activity decisions?**

Yes, via existing `log_validation_outcome()` pattern in GovernanceLayer. Add logging in `check_activity()` similar to `check_gate()`. This provides audit trail per L4 invariant.

---

## Open Decisions (MUST resolve before implementation)

<!-- No operator_decisions in work item frontmatter - all design decisions resolved in CH-001/CH-002/CH-003 -->

**SKIPPED:** No open decisions. All architectural decisions resolved in CH-001 (ActivityMatrix), CH-002 (StateDefinitions), and CH-003 (GovernanceRules). Implementation follows spec.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add Tests 1-8 to `tests/test_governance_layer.py`
- [ ] Create new test class `TestGovernerActivities`
- [ ] Verify all 8 tests fail (red) - GovernanceLayer doesn't have these methods yet

### Step 2: Create activity_matrix.yaml
- [ ] Create `.claude/haios/config/activity_matrix.yaml`
- [ ] Populate with full matrix from CH-003 (17 primitives × 6 states)
- [ ] Add skill_restrictions section for DO phase
- [ ] Add phase_to_state mapping from CH-002
- [ ] Tests 4, 5, 6 remain red (methods not implemented yet)

### Step 3: Implement GovernanceLayer Methods
- [ ] Add `get_activity_state()` - Tests 1, 2 pass (green)
- [ ] Add `map_tool_to_primitive()` - Test 3 passes (green)
- [ ] Add `check_activity()` - Tests 4, 5, 6 pass (green)
- [ ] Add `_check_skill_restriction()` - Test 7 passes (green)
- [ ] Add `_load_activity_matrix()` (caching helper)

### Step 4: Integrate into PreToolUse Hook
- [ ] Add `_check_governed_activity()` function to `pre_tool_use.py`
- [ ] Call it FIRST in `handle()` function
- [ ] Test 8 passes (backward compatibility)

### Step 5: Integration Verification
- [ ] Run `pytest tests/test_governance_layer.py -v` - all 8 new tests pass
- [ ] Run `pytest tests/test_pre_tool_use.py -v` - existing tests still pass
- [ ] Run full test suite: `pytest tests/ -v` - no regressions

### Step 6: Create Chapter Documentation
- [ ] Create `.claude/haios/epochs/E2_4/arcs/activities/CH-004-PreToolUseIntegration.md`
- [ ] Document implementation details, integration points
- [ ] Mark CH-004 status as "Complete" in ARC.md

### Step 7: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` - document new methods
- [ ] **MUST:** Update `.claude/haios/config/README.md` - document activity_matrix.yaml
- [ ] **MUST:** Verify README content matches actual file state

### Step 8: Consumer Verification
- [ ] Verify `pre_tool_use.py` properly imports from `governance_layer.py`
- [ ] Verify `activity_matrix.yaml` loaded correctly
- [ ] Manual test: Enter DO phase, try AskUserQuestion - should be blocked

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Spec misalignment:** check_activity algorithm differs from CH-003 | High | MUST read CH-003 pseudocode, implement exactly as specified |
| **Integration regression:** Existing hook checks break | High | Test 8 verifies backward compatibility; run full test suite |
| **State detection failure:** just get-cycle unreliable | Med | Fail-permissive (return EXPLORE); log warning for visibility |
| **Performance:** YAML parsing on every tool invocation | Med | Cache activity_matrix.yaml globally; load once per session |
| **Circular imports:** governance_layer imports hook code | Low | Hook imports module (one-way); use subprocess for just get-cycle |
| **Scope creep:** Implementing full matrix when subset sufficient | Low | Start with DO-phase blocks only (user-query, memory-search, web-*); expand later |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-042/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| **activity_matrix.yaml** | [ ] | File exists at `.claude/haios/config/activity_matrix.yaml` |
| **GovernanceLayer.get_activity_state()** | [ ] | Method exists, returns valid state string |
| **GovernanceLayer.map_tool_to_primitive()** | [ ] | Method exists, maps tools correctly |
| **GovernanceLayer.check_activity()** | [ ] | Method exists, returns GateResult |
| **GovernanceLayer._check_skill_restriction()** | [ ] | Method exists, blocks critique in DO |
| **PreToolUse integration** | [ ] | Hook calls check_activity(), blocks in DO |
| **Unit tests** | [ ] | 8 new tests pass in test_governance_layer.py |
| **CH-004-PreToolUseIntegration.md** | [ ] | Chapter file exists and documents implementation |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/config/activity_matrix.yaml` | O(1) lookup rules for 17 primitives × 6 states | [ ] | |
| `.claude/haios/modules/governance_layer.py` | 4 new methods: get_activity_state, map_tool_to_primitive, check_activity, _check_skill_restriction | [ ] | |
| `.claude/hooks/hooks/pre_tool_use.py` | _check_governed_activity function, called first in handle() | [ ] | |
| `tests/test_governance_layer.py` | TestGovernedActivities class with 8 tests | [ ] | |
| `.claude/haios/epochs/E2_4/arcs/activities/CH-004-PreToolUseIntegration.md` | Chapter file documenting implementation | [ ] | |
| `.claude/haios/modules/README.md` | **MUST:** Documents new GovernanceLayer methods | [ ] | |
| `.claude/haios/config/README.md` | **MUST:** Documents activity_matrix.yaml | [ ] | |

**Verification Commands:**
```bash
# Run governed activities tests
pytest tests/test_governance_layer.py::TestGovernedActivities -v
# Expected: 8 tests passed

# Run full test suite to verify no regressions
pytest tests/ -v --tb=short
# Expected: All existing tests still pass
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @.claude/haios/epochs/E2_4/arcs/activities/CH-001-ActivityMatrix.md (primitives, states, rules matrix)
- @.claude/haios/epochs/E2_4/arcs/activities/CH-002-StateDefinitions.md (state detection, phase-to-state mapping)
- @.claude/haios/epochs/E2_4/arcs/activities/CH-003-GovernanceRules.md (rule schema, check_activity algorithm)
- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md (parent arc)
- @.claude/hooks/hooks/pre_tool_use.py (integration point)
- @.claude/haios/modules/governance_layer.py (module to extend)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ACTIVITY-001, REQ-ACTIVITY-002)
- @docs/work/active/WORK-042/WORK.md (work item)

---
