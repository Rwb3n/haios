# generated: 2026-02-01
# System Auto: last updated on: 2026-02-01T14:20:51
# Chapter: GovernanceRules

## Definition

**Chapter ID:** CH-003
**Arc:** activities
**Status:** Draft
**Depends:** CH-001 ActivityMatrix (defines what rules govern), CH-002 StateDefinitions (defines states used in lookup)
**Enables:** CH-004 PreToolUseIntegration (needs rules to enforce)

---

## Problem

CH-001 ActivityMatrix defines 102 rule cells as table entries (symbols: allow, warn, block, redirect). CH-002 StateDefinitions formalizes the 6 states with schemas and detection logic.

**Problem:** The rules themselves exist only as table cells in CH-001. To implement state-aware governance, we need:

1. **Rule schema** - What fields define a governance rule?
2. **Rule lookup data structure** - How are rules stored for fast lookup by (primitive, state)?
3. **Rule application logic** - How does `check_activity()` evaluate rules with context?
4. **Warning vs Block behavior** - When to warn (continue with message) vs block (halt with error)?
5. **Context sensitivity** - How do path patterns, tool inputs affect rule application?

---

## Rule Schema

Each cell in the ActivityMatrix becomes a governance rule with the following structure:

```yaml
# Governance rule schema
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

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | enum | Yes | One of: `allow`, `warn`, `block`, `redirect` |
| `message` | string | For warn/block/redirect | User-facing explanation and guidance |
| `redirect_to` | string | For redirect | Alternative tool/subagent to use |
| `path_patterns` | list | No | File path constraints for write operations |
| `tool_inputs` | dict | No | Tool input validation patterns |
| `conditions` | list | No | Additional runtime conditions |

---

## Rule Actions Specification

### Action Behaviors

| Action | Hook Return | PreToolUse Response | User Experience |
|--------|-------------|---------------------|-----------------|
| `allow` | `None` | No output | Operation proceeds silently |
| `warn` | `{"permissionDecision": "allow", "permissionDecisionReason": message}` | Allow with message | Operation proceeds with warning shown |
| `block` | `{"permissionDecision": "deny", "permissionDecisionReason": message}` | Deny with message | Operation blocked with guidance |
| `redirect` | `{"permissionDecision": "deny", "permissionDecisionReason": redirect_message}` | Deny with alternative | Operation blocked with alternative guidance |

### Action Selection Guidelines

| Use Action | When |
|------------|------|
| `allow` | Activity is fully permitted in this state |
| `warn` | Activity is allowed but unusual/risky in this state |
| `block` | Activity violates state constraints (e.g., user-query in DO) |
| `redirect` | Activity should use a different tool/pattern (e.g., db-query → schema-verifier) |

---

## Data Structure Design

### File Location

```
.claude/haios/config/activity_matrix.yaml
```

### Format

Nested dictionary structure for O(1) lookup by (primitive, state):

```yaml
# .claude/haios/config/activity_matrix.yaml
# O(1) lookup by (primitive, state)

version: "1.0"
default_action: allow   # Fail-open for unknown primitives

rules:
  # Format: primitive -> state -> rule

  # Category 1: File Operations
  file-read:
    EXPLORE: {action: allow}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: allow}
    CHECK: {action: allow}
    DONE: {action: allow}

  file-write:
    EXPLORE: {action: warn, message: "EXPLORE phase: prefer notes over artifacts"}
    DESIGN: {action: allow, path_patterns: [{pattern: "docs/specs/*"}]}
    PLAN: {action: allow, path_patterns: [{pattern: "**/plans/*"}]}
    DO: {action: allow, path_patterns: [{pattern: "src/**"}]}
    CHECK: {action: warn, message: "CHECK phase: writes should be verdict only"}
    DONE: {action: allow}

  file-edit:
    EXPLORE: {action: warn, message: "EXPLORE phase: prefer notes over artifacts"}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: allow}
    CHECK: {action: warn, message: "CHECK phase: edits should be verdict only"}
    DONE: {action: allow}

  file-search:
    _all_states: {action: allow}

  content-search:
    _all_states: {action: allow}

  # Category 2: Execution
  shell-execute:
    EXPLORE: {action: warn, message: "EXPLORE phase: prefer read-only commands"}
    DESIGN: {action: warn, message: "DESIGN phase: prefer read-only commands"}
    PLAN: {action: warn, message: "PLAN phase: prefer read-only commands"}
    DO: {action: allow}
    CHECK: {action: allow}
    DONE: {action: warn, message: "DONE phase: prefer read-only commands"}

  shell-background:
    EXPLORE: {action: block, message: "BLOCKED: Background execution not allowed in EXPLORE"}
    DESIGN: {action: block, message: "BLOCKED: Background execution not allowed in DESIGN"}
    PLAN: {action: block, message: "BLOCKED: Background execution not allowed in PLAN"}
    DO: {action: allow}
    CHECK: {action: allow}
    DONE: {action: block, message: "BLOCKED: Background execution not allowed in DONE"}

  notebook-edit:
    EXPLORE: {action: block, message: "BLOCKED: Notebook edits not allowed in EXPLORE"}
    DESIGN: {action: warn, message: "DESIGN phase: notebook edits unusual"}
    PLAN: {action: warn, message: "PLAN phase: notebook edits unusual"}
    DO: {action: allow}
    CHECK: {action: allow}
    DONE: {action: block, message: "BLOCKED: Notebook edits not allowed in DONE"}

  # Category 3: Web/External
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

  # Category 4: Agent/Task
  task-spawn:
    _all_states: {action: allow}

  skill-invoke:
    EXPLORE: {action: allow}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: allow}  # Additional skill restrictions applied separately
    CHECK: {action: allow}
    DONE: {action: allow}

  user-query:
    EXPLORE: {action: allow}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: block, message: "BLOCKED: DO phase is black-box. Spec should be complete - no user queries."}
    CHECK: {action: allow}
    DONE: {action: allow}

  # Category 5: Memory (HAIOS)
  memory-search:
    EXPLORE: {action: allow}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: block, message: "BLOCKED: DO phase is black-box. Query memory during EXPLORE/DESIGN."}
    CHECK: {action: allow}
    DONE: {action: allow}

  memory-store:
    EXPLORE: {action: warn, message: "EXPLORE phase: prefer notes over memory storage"}
    DESIGN: {action: warn, message: "DESIGN phase: prefer notes over memory storage"}
    PLAN: {action: warn, message: "PLAN phase: prefer notes over memory storage"}
    DO: {action: block, message: "BLOCKED: Memory storage not allowed in DO phase."}
    CHECK: {action: warn, message: "CHECK phase: prefer notes over memory storage"}
    DONE: {action: allow}

  schema-query:
    _all_states: {action: allow}

  db-query:
    _all_states: {action: redirect, redirect_to: "schema-verifier", message: "BLOCKED: Direct SQL not allowed. Use: Task(prompt='...', subagent_type='schema-verifier')"}

  # Category 6: Planning/Governance
  plan-enter:
    EXPLORE: {action: allow}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: block, message: "BLOCKED: Cannot enter plan mode during DO phase."}
    CHECK: {action: allow}
    DONE: {action: allow}

  plan-exit:
    PLAN: {action: allow}
    _other_states: {action: allow}  # N/A in most states

  mcp-list:
    _all_states: {action: allow}

  mcp-read:
    _all_states: {action: allow}
```

### Lookup Semantics

1. **Exact match:** `rules[primitive][state]` → rule
2. **All-states shorthand:** `rules[primitive]["_all_states"]` → applies to all states
3. **Unknown primitive:** Use `default_action` (fail-open: allow)
4. **Unknown state:** Default to EXPLORE state rules (fail-permissive per CH-002)

---

## check_activity() Algorithm

### Function Signature

```python
def check_activity(primitive: str, state: str, context: dict) -> GateResult:
    """
    Check if an activity is allowed in the current state.

    Args:
        primitive: The primitive being invoked (e.g., "file-write", "user-query")
        state: Current ActivityMatrix state (e.g., "DO", "EXPLORE")
        context: Additional context dict:
            - file_path: str (for file operations)
            - tool_input: dict (raw tool input)
            - skill_name: str (for skill-invoke)

    Returns:
        GateResult with allowed flag and reason message
    """
```

### Algorithm Pseudocode

```python
def check_activity(primitive: str, state: str, context: dict) -> GateResult:
    # 1. Load rules (cached after first load)
    rules = _load_activity_matrix()

    # 2. Look up rule for (primitive, state)
    primitive_rules = rules.get("rules", {}).get(primitive, {})

    # Check for _all_states rule first
    if "_all_states" in primitive_rules:
        rule = primitive_rules["_all_states"]
    elif state in primitive_rules:
        rule = primitive_rules[state]
    else:
        # Unknown primitive or state - use default (fail-open)
        default = rules.get("default_action", "allow")
        return GateResult(allowed=True, reason=f"Unknown primitive/state, defaulting to {default}")

    # 3. Evaluate action
    action = rule.get("action", "allow")
    message = rule.get("message", "")

    if action == "allow":
        return GateResult(allowed=True, reason="Activity allowed")

    if action == "warn":
        return GateResult(allowed=True, reason=message)  # Allow with warning

    if action == "block":
        return GateResult(allowed=False, reason=message)

    if action == "redirect":
        redirect_to = rule.get("redirect_to", "alternative")
        redirect_msg = message or f"Use {redirect_to} instead"
        return GateResult(allowed=False, reason=redirect_msg)

    # 4. Path pattern validation (if applicable)
    if "path_patterns" in rule and "file_path" in context:
        file_path = context["file_path"]
        patterns = rule["path_patterns"]

        if not _path_matches_patterns(file_path, patterns, state):
            return GateResult(
                allowed=False,
                reason=f"Path not allowed in {state} state: {file_path}"
            )

    # 5. Skill restrictions (if skill-invoke in DO)
    if primitive == "skill-invoke" and state == "DO" and "skill_name" in context:
        skill_result = _check_skill_restriction(context["skill_name"], state)
        if skill_result is not None:
            return skill_result

    return GateResult(allowed=True, reason="Activity allowed")


def _path_matches_patterns(file_path: str, patterns: list, state: str) -> bool:
    """Check if file path matches any allowed pattern for this state."""
    import fnmatch

    normalized = file_path.replace("\\", "/")

    for pattern_spec in patterns:
        pattern = pattern_spec.get("pattern", "")
        valid_in = pattern_spec.get("valid_in", [])

        # If valid_in specified, check state is in list
        if valid_in and state not in valid_in:
            continue

        if fnmatch.fnmatch(normalized, pattern):
            return True

    return False


def _load_activity_matrix() -> dict:
    """Load and cache activity_matrix.yaml."""
    global _cached_matrix

    if _cached_matrix is not None:
        return _cached_matrix

    config_path = Path(".claude/haios/config/activity_matrix.yaml")
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            _cached_matrix = yaml.safe_load(f) or {}
    else:
        _cached_matrix = {"default_action": "allow", "rules": {}}

    return _cached_matrix
```

### Return Type

```python
@dataclass
class GateResult:
    """Result of a gate check."""
    allowed: bool       # Whether the activity is permitted
    reason: str         # Human-readable explanation/guidance
    degraded: bool = False  # Whether governance is in degraded state
```

---

## Path Classification Logic

### classify_path() Algorithm

```python
def classify_path(file_path: str) -> str:
    """
    Classify a file path into categories for state-based validation.

    Args:
        file_path: File path (forward or back slashes)

    Returns:
        Classification: "notes", "spec", "plan", "artifact", "test",
                       "verdict", "archive", "config", "docs"
    """
    import re

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

### Classification → State Validity

| Classification | Valid States for Write | Rationale |
|----------------|----------------------|-----------|
| `notes` | EXPLORE | Discovery notes only in EXPLORE |
| `spec` | DESIGN | Specifications written during design |
| `plan` | PLAN | Plans written during planning |
| `artifact` | DO | Code/artifacts during implementation |
| `test` | DO, CHECK | Tests during implementation and verification |
| `verdict` | CHECK | Verification output during CHECK |
| `archive` | DONE | Archives during closure |
| `config` | DESIGN, PLAN | Configuration during design/planning |
| `docs` | EXPLORE, DESIGN | Documentation during discovery/design |

### Fallback Behavior

**Unknown paths default to "artifact" classification.**

Implications:
- In DO state: Allowed (artifact writes expected)
- In other states: Subject to state restrictions
- Rationale: Fail-restrictive outside DO, permissive in DO (per CH-001)

---

## Skill Restriction Rules

### Configuration Format

```yaml
# Skills allowed/blocked in DO state
# Part of activity_matrix.yaml or separate file

skill_restrictions:
  DO:
    allowed:
      - validate    # Verification skill
      - status      # Status check skill
      - implement   # Implementation continuation
      - schema      # Schema lookup
      - tree        # Directory listing

    blocked:
      - critique    # Design-phase skill - spec is frozen
      - reason      # Planning skill - spec is frozen
      - new-*       # Creation skills belong in DESIGN/PLAN
      - close       # Closure belongs in DONE

    block_message: "BLOCKED: Skill '{skill}' not allowed in DO phase. Spec is frozen."
```

### Skill Check Algorithm

```python
def _check_skill_restriction(skill_name: str, state: str) -> Optional[GateResult]:
    """
    Check if a skill is allowed in the current state.

    Args:
        skill_name: Name of skill being invoked (e.g., "critique", "new-plan")
        state: Current ActivityMatrix state

    Returns:
        None if allowed, GateResult if blocked
    """
    import fnmatch

    restrictions = _load_skill_restrictions()
    state_rules = restrictions.get(state, {})

    if not state_rules:
        return None  # No restrictions for this state

    allowed = state_rules.get("allowed", [])
    blocked = state_rules.get("blocked", [])
    block_message = state_rules.get("block_message", "Skill not allowed in this state")

    # Check explicit allow list first
    for pattern in allowed:
        if fnmatch.fnmatch(skill_name, pattern):
            return None  # Explicitly allowed

    # Check blocked list (supports wildcards like "new-*")
    for pattern in blocked:
        if fnmatch.fnmatch(skill_name, pattern):
            return GateResult(
                allowed=False,
                reason=block_message.format(skill=skill_name)
            )

    # Default: allow if not in blocked list
    return None
```

### Wildcard Matching

Uses Python's `fnmatch` module for glob-style pattern matching:

| Pattern | Matches | Does Not Match |
|---------|---------|----------------|
| `new-*` | `new-work`, `new-plan`, `new-investigation` | `renew`, `newest` |
| `*-cycle` | `implementation-cycle`, `investigation-cycle` | `cycle`, `cycling` |
| `validate` | `validate` (exact) | `validation`, `validator` |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| YAML for rules | Store in `activity_matrix.yaml` | Configuration-driven per memory 37910: "required checks should be in a governing configuration artifact" |
| O(1) lookup structure | Nested dict: primitive → state → rule | Fast lookup needed for PreToolUse hook (called every tool invocation) |
| Fail-open default | Unknown primitive/state → allow | Per CH-002: fail-permissive on state detection errors prevents halting work |
| Path classification fallback | Unknown path → "artifact" | Per CH-001: fail-restrictive in non-DO phases, permissive in DO |
| Separate skill restrictions | Dedicated section in config | Skills have different governance (name-based) than primitives (tool-based) |
| Cache rules | Load YAML once, cache in memory | Performance: avoid re-parsing on every tool invocation |

---

## Exit Criteria

- [x] Rule Schema defined (YAML structure with action, message, path_patterns, tool_inputs, conditions)
- [x] Rule Actions Specification documented (allow/warn/block/redirect behaviors)
- [x] Data Structure Design complete (activity_matrix.yaml format with O(1) lookup)
- [x] check_activity() Algorithm documented (pseudocode with parameter definitions)
- [x] Path Classification Logic documented (classify_path() with pattern table)
- [x] Skill Restriction Rules documented (DO-phase skill config format)

---

## Memory Refs

Session 265 governed activities decision: 82706-82710
Session 266 ActivityMatrix design: 82745-82751
Session 268 StateDefinitions: 82777-82797
Session 269 GovernanceRules design: (to be added after ingester_ingest)

---

## References

- @.claude/haios/epochs/E2_4/arcs/activities/CH-001-ActivityMatrix.md (source spec)
- @.claude/haios/epochs/E2_4/arcs/activities/CH-002-StateDefinitions.md (state definitions)
- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md (parent arc)
- @.claude/haios/epochs/E2_4/EPOCH.md (epoch decisions)
- @.claude/haios/modules/governance_layer.py (existing module to extend)
- @.claude/hooks/hooks/pre_tool_use.py (current implementation)
- @docs/work/active/WORK-041/WORK.md (work item)
- @docs/work/active/WORK-041/plans/PLAN.md (implementation plan)
