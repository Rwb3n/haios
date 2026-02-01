---
template: implementation_plan
status: approved
date: 2026-02-01
backlog_id: WORK-041
title: Design CH-003 GovernanceRules
author: Hephaestus
lifecycle_phase: plan
session: 269
version: '1.5'
generated: 2025-12-21
last_updated: '2026-02-01T14:02:50'
---
# Implementation Plan: Design CH-003 GovernanceRules

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

Formalize governance rule schema, data structure, and evaluation logic so `check_activity()` can enforce the ActivityMatrix in PreToolUse hooks.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | Design-only work item |
| Lines of code affected | 0 | No code changes this work item |
| New files to create | 1 | CH-003-GovernanceRules.md |
| Tests to write | 0 | SKIPPED: Design work (per memory 82789-82792) |
| Dependencies | 0 | Documentation deliverable |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Design doc, no runtime integration |
| Risk of regression | Low | No code changes |
| External dependencies | Low | Only references CH-001, CH-002 |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Rule schema design | 30 min | High |
| Data structure design | 30 min | High |
| Algorithm pseudocode | 45 min | Med |
| Path classification logic | 30 min | High |
| **Total** | ~2.5 hr | High |

---

## Current State vs Desired State

### Current State

**SKIPPED:** This is a design work item creating CH-003-GovernanceRules.md. No existing code to show.

**Current situation:**
- CH-001 ActivityMatrix defines 102 rule cells as table entries (symbols: allow, warn, block, redirect)
- CH-002 StateDefinitions defines 6 states and detection logic
- No formal rule schema exists
- No data structure for fast rule lookup
- No algorithm for context-sensitive evaluation

### Desired State

**SKIPPED:** Design deliverable, not code change.

**Desired situation:**
- Formal rule schema with action, message, path_patterns, tool_inputs, conditions
- Data structure design for O(1) lookup by (primitive, state)
- `check_activity()` algorithm pseudocode
- Path classification algorithm
- Skill restriction rules for DO state

---

## Tests First (TDD)

**SKIPPED:** Design work item (type: design) per memory refs 82789-82792.

> Session 268 decision: "Design work items follow implementation-cycle but with different CHECK criteria. When type: design, the 'Tests First' section can be SKIPPED with rationale. CHECK phase verifies deliverables exist and match plan, not that tests pass."

Tests will be written in CH-004 PreToolUseIntegration when these rules are implemented in code.

---

## Detailed Design

**Note:** This is a design work item. The "Exact Code Change" section is replaced with design specifications that will be documented in CH-003-GovernanceRules.md.

### 1. Rule Schema Design

```yaml
# Governance rule schema - each cell in the ActivityMatrix becomes a rule
rule_schema:
  action: enum           # allow | warn | block | redirect
  message: string        # User-facing message (required for warn/block/redirect)
  redirect_to: string    # For redirect action: what to use instead (e.g., "schema-verifier")
  path_patterns:         # Optional: file path constraints
    - pattern: glob      # e.g., "docs/specs/*", "src/**/*.py"
      valid_in: list     # States where this pattern is allowed
  tool_inputs:           # Optional: tool input constraints
    key: string          # Input key to check (e.g., "command" for Bash)
    pattern: regex       # Regex to match
  conditions:            # Optional: additional conditions
    - type: string       # Condition type (e.g., "file_exists", "cycle_active")
      value: any         # Condition-specific value
```

### 2. Rule Actions Specification

| Action | Hook Behavior | User Experience |
|--------|---------------|-----------------|
| `allow` | Return `None` | Operation proceeds silently |
| `warn` | Return `{"permissionDecision": "allow", "permissionDecisionReason": message}` | Operation proceeds with warning shown |
| `block` | Return `{"permissionDecision": "deny", "permissionDecisionReason": message}` | Operation blocked with guidance |
| `redirect` | Return `{"permissionDecision": "deny", "permissionDecisionReason": redirect_message}` | Operation blocked with alternative guidance |

### 3. Data Structure Design (activity_matrix.yaml)

```yaml
# .claude/haios/config/activity_matrix.yaml
# O(1) lookup by (primitive, state)

version: "1.0"
default_action: allow   # Fail-open for unknown primitives

rules:
  # Category 1: File Operations
  file-read:
    EXPLORE: {action: allow}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: allow, path_patterns: [{pattern: "docs/specs/*", valid_in: [DO]}]}
    CHECK: {action: allow}
    DONE: {action: allow}

  file-write:
    EXPLORE: {action: warn, message: "EXPLORE phase: prefer notes over artifacts"}
    DESIGN: {action: allow, path_patterns: [{pattern: "docs/specs/*"}]}
    PLAN: {action: allow, path_patterns: [{pattern: "**/plans/*"}]}
    DO: {action: allow, path_patterns: [{pattern: "src/**", valid_in: [DO]}]}
    CHECK: {action: warn, message: "CHECK phase: writes should be verdict only"}
    DONE: {action: allow}

  # ... (remaining 15 primitives)

  # Special: user-query (DO phase blocked)
  user-query:
    EXPLORE: {action: allow}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: block, message: "BLOCKED: DO phase is black-box. Spec should be complete - no user queries."}
    CHECK: {action: allow}
    DONE: {action: allow}

  # Special: memory-search (DO phase blocked)
  memory-search:
    EXPLORE: {action: allow}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: block, message: "BLOCKED: DO phase is black-box. Query memory during EXPLORE/DESIGN."}
    CHECK: {action: allow}
    DONE: {action: allow}

  # Special: db-query (always redirect)
  db-query:
    _all_states: {action: redirect, redirect_to: "schema-verifier", message: "BLOCKED: Direct SQL not allowed. Use: Task(prompt='...', subagent_type='schema-verifier')"}
```

### 4. check_activity() Algorithm

```python
def check_activity(primitive: str, state: str, context: dict) -> GateResult:
    """
    Check if an activity is allowed in the current state.

    Args:
        primitive: The primitive being invoked (e.g., "file-write", "user-query")
        state: Current ActivityMatrix state (e.g., "DO", "EXPLORE")
        context: Additional context (file_path, tool_input, etc.)

    Returns:
        GateResult with action and message
    """
    # 1. Load rules (cached after first load)
    rules = _load_activity_matrix()

    # 2. Look up rule for (primitive, state)
    primitive_rules = rules.get(primitive, {})

    # Check for _all_states rule first (e.g., db-query redirect)
    if "_all_states" in primitive_rules:
        rule = primitive_rules["_all_states"]
    elif state in primitive_rules:
        rule = primitive_rules[state]
    else:
        # Unknown primitive or state - use default (fail-open)
        return GateResult(allowed=True, reason="Unknown primitive/state, defaulting to allow")

    # 3. Evaluate action
    action = rule.get("action", "allow")

    if action == "allow":
        return GateResult(allowed=True, reason="Activity allowed")

    if action == "warn":
        return GateResult(allowed=True, reason=rule.get("message", "Warning"))

    if action == "block":
        return GateResult(allowed=False, reason=rule.get("message", "Blocked"))

    if action == "redirect":
        redirect_msg = rule.get("message", f"Use {rule.get('redirect_to', 'alternative')} instead")
        return GateResult(allowed=False, reason=redirect_msg)

    # 4. Path pattern validation (if applicable)
    if "path_patterns" in rule and "file_path" in context:
        if not _path_matches_patterns(context["file_path"], rule["path_patterns"], state):
            return GateResult(
                allowed=False,
                reason=f"Path not allowed in {state} state: {context['file_path']}"
            )

    return GateResult(allowed=True, reason="Activity allowed")
```

### 5. Path Classification Logic

```python
def classify_path(file_path: str) -> str:
    """
    Classify a file path into categories for state-based validation.

    Args:
        file_path: Normalized file path (forward slashes)

    Returns:
        Classification: "notes", "spec", "plan", "artifact", "test", "verdict", "archive", "config", "docs"
    """
    normalized = file_path.replace("\\", "/")

    # Priority order matters - more specific patterns first
    patterns = [
        # Work directory structure
        (r"docs/work/.*/notes/", "notes"),
        (r"docs/work/.*/plans/", "plan"),
        (r"docs/work/.*/CHECK\.md$", "verdict"),
        (r"docs/work/archive/", "archive"),

        # Spec patterns
        (r"docs/specs/", "spec"),
        (r"docs/ADR/", "spec"),
        (r"\.spec\.md$", "spec"),

        # Test patterns
        (r"tests/", "test"),
        (r"\.test\.", "test"),
        (r"test_.*\.py$", "test"),

        # Artifact patterns (code)
        (r"src/", "artifact"),
        (r"lib/", "artifact"),
        (r"\.py$", "artifact"),
        (r"\.ts$", "artifact"),
        (r"\.js$", "artifact"),

        # Config patterns
        (r"\.yaml$", "config"),
        (r"\.json$", "config"),
        (r"\.claude/", "config"),

        # Archive patterns
        (r"docs/checkpoints/", "archive"),

        # Docs patterns
        (r"README\.md$", "docs"),
        (r"\.md$", "docs"),
    ]

    for pattern, classification in patterns:
        if re.search(pattern, normalized, re.IGNORECASE):
            return classification

    # Fallback: unclassified paths default to "artifact"
    # Per CH-001: Fail-restrictive in non-DO phases, permissive in DO
    return "artifact"
```

### 6. Skill Restriction Rules (DO State)

```yaml
# Skills allowed/blocked in DO state
# From CH-001 "Skill Restrictions in DO" section

skill_restrictions:
  DO:
    allowed:
      - validate    # Verification skill
      - status      # Status check
      - implement   # Implementation continuation
      - schema      # Schema lookup

    blocked:
      - critique    # Design-phase skill - spec is frozen
      - reason      # Planning skill - spec is frozen
      - new-*       # Creation skills belong in DESIGN/PLAN
      - close       # Closure belongs in DONE

    block_message: "BLOCKED: Skill '{skill}' not allowed in DO phase. Spec is frozen."
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| YAML for rules | Store in activity_matrix.yaml | Configuration-driven per memory 37910: "required checks should be in a governing configuration artifact" |
| O(1) lookup structure | Nested dict: primitive → state → rule | Fast lookup needed for PreToolUse hook (called every tool invocation) |
| Fail-open default | Unknown primitive/state → allow | Per CH-002: fail-permissive on state detection errors prevents halting work |
| Path classification fallback | Unknown path → "artifact" | Per CH-001: fail-restrictive in non-DO phases, permissive in DO |
| Separate skill restrictions | Dedicated section in config | Skills have different governance (name-based) than primitives (tool-based) |

### Input/Output Examples

**Example 1: AskUserQuestion in DO state**
```python
# Input
check_activity(
    primitive="user-query",
    state="DO",
    context={}
)

# Output
GateResult(
    allowed=False,
    reason="BLOCKED: DO phase is black-box. Spec should be complete - no user queries."
)
```

**Example 2: File write with path check**
```python
# Input
check_activity(
    primitive="file-write",
    state="DO",
    context={"file_path": "docs/specs/TRD-NEW.md"}
)

# Output
GateResult(
    allowed=False,
    reason="Path not allowed in DO state: docs/specs/TRD-NEW.md"
)
```

### Edge Cases

| Case | Handling | Notes |
|------|----------|-------|
| Unknown primitive | Allow with warning | Fail-open for forward compatibility |
| Unknown state | Default to EXPLORE | Per CH-002 fail-permissive design |
| No cycle active | State = EXPLORE | Per CH-002 phase-to-state mapping |
| Subagent context | No state inheritance v1 | Known limitation per CH-002 |
| Multiple path patterns | First match wins | Order patterns by specificity |

### Open Questions

**Q: Should rules be cached or loaded fresh each invocation?**

Cache after first load. PreToolUse is called frequently; re-parsing YAML each time would be slow. Cache invalidation: only on explicit reload or file change detection.

**Q: How to handle skill restrictions with wildcards (new-*)?**

Use fnmatch-style glob matching for skill names in the blocked list. "new-*" matches "new-work", "new-plan", etc.

---

## Open Decisions (MUST resolve before implementation)

**No operator decisions required.** WORK-041 has no `operator_decisions` field populated.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| (none) | - | - | No blocking decisions |

---

## Implementation Steps

**Note:** Design work - steps produce documentation, not code.

### Step 1: Create Chapter File
- [ ] Create `.claude/haios/epochs/E2_4/arcs/activities/CH-003-GovernanceRules.md`
- [ ] Add frontmatter (Chapter ID, Arc, Status, Depends, Enables)

### Step 2: Write Rule Schema Section
- [ ] Document rule_schema YAML structure
- [ ] Define all fields (action, message, redirect_to, path_patterns, tool_inputs, conditions)
- [ ] Show examples

### Step 3: Write Rule Actions Specification
- [ ] Document allow/warn/block/redirect behaviors
- [ ] Show hook return format for each action
- [ ] Document user experience for each

### Step 4: Write Data Structure Design
- [ ] Document activity_matrix.yaml format
- [ ] Show complete structure for O(1) lookup
- [ ] Include examples for key primitives (user-query, file-write, db-query)

### Step 5: Write check_activity() Algorithm
- [ ] Document algorithm pseudocode
- [ ] Show parameter definitions
- [ ] Document return type and values
- [ ] Show example invocations

### Step 6: Write Path Classification Logic
- [ ] Document classify_path() algorithm
- [ ] Show pattern priority order
- [ ] Document fallback behavior
- [ ] Show path → classification mapping table

### Step 7: Write Skill Restriction Rules
- [ ] Document allowed/blocked skills for DO state
- [ ] Show config format
- [ ] Document wildcard matching behavior

### Step 8: Verify Deliverables
- [ ] All 7 deliverables from WORK-041 addressed in chapter file
- [ ] Cross-reference to CH-001 and CH-002 where appropriate

---

## Verification

- [x] Tests pass - **SKIPPED:** Design work (no tests)
- [ ] **MUST:** Chapter file created and complete
- [ ] Design review complete (verify against CH-001 matrix)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment with CH-001 | High | Cross-reference each rule to CH-001 matrix cell |
| Missing edge cases | Med | Review CH-001 "Redirect Behavior" and "Path Classification" sections |
| Integration complexity underestimated | Med | CH-004 will implement; this design should be complete enough for independent implementation |
| Path classification ambiguity | Med | Document fallback behavior and priority order explicitly |
| Skill wildcard matching complexity | Low | Use standard fnmatch library - well-tested |

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

**MUST** read `docs/work/active/WORK-041/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Rule Schema | [ ] | Section in CH-003 with YAML schema |
| Rule Actions Spec | [ ] | Table with allow/warn/block/redirect behaviors |
| Data Structure Design | [ ] | activity_matrix.yaml format documented |
| check_activity() Algorithm | [ ] | Pseudocode with parameters and return type |
| Path Classification Logic | [ ] | classify_path() algorithm with pattern table |
| Skill Restriction Rules | [ ] | DO-phase skill config format documented |
| CH-003-GovernanceRules.md | [ ] | File exists at expected path |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). For design work: "Chapter complete = Done" requires all deliverables documented.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/epochs/E2_4/arcs/activities/CH-003-GovernanceRules.md` | All 6 design sections present | [ ] | |
| N/A | No tests for design work | [x] | SKIPPED per memory 82789-82792 |

**Verification Commands:**
```bash
# Verify chapter file exists and has expected sections
Read(file_path=".claude/haios/epochs/E2_4/arcs/activities/CH-003-GovernanceRules.md")
# Expected: File exists with Rule Schema, Actions, Data Structure, check_activity, Path Classification, Skill Restrictions
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Chapter file has all required sections? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033 - Design Work):**
- [x] Tests pass - **SKIPPED:** Design work (no tests)
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [x] **Runtime consumer exists** - N/A for design work; CH-004 will be the consumer
- [ ] WHY captured (reasoning stored to memory)
- [x] **MUST:** READMEs updated - N/A (no directory structure changes)
- [x] **MUST:** Consumer verification - N/A (no code changes)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **Session 268 Learning (memory 82789-82792):** Design work items follow implementation-cycle but "Tests pass" criterion can be marked N/A with rationale. CHECK verifies deliverables exist and match plan.

---

## References

- @.claude/haios/epochs/E2_4/arcs/activities/CH-001-ActivityMatrix.md (source spec - matrix definitions)
- @.claude/haios/epochs/E2_4/arcs/activities/CH-002-StateDefinitions.md (state definitions)
- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md (parent arc)
- @.claude/haios/modules/governance_layer.py (existing module to extend in CH-004)
- @.claude/hooks/hooks/pre_tool_use.py (current implementation to integrate in CH-004)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ACTIVITY-001, REQ-ACTIVITY-002)

---
