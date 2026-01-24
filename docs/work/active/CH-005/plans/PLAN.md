---
template: implementation_plan
status: complete
date: 2026-01-24
backlog_id: CH-005
title: Session Loader - Build session context loader for coldstart Phase 2
author: Hephaestus
lifecycle_phase: plan
session: 229
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-24T19:08:42'
---
# Implementation Plan: Session Loader - Build session context loader for coldstart Phase 2

@docs/README.md
@docs/epistemic_state.md

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

A single `just session-context` command will output formatted session context (prior session completed work, memory refs content, drift warnings, pending items) for coldstart Phase 2 injection, eliminating 6 manual agent steps.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | justfile, coldstart.md, context_loader.py (registration) |
| Lines of code affected | ~30 | Registration + recipe additions |
| New files to create | 2 | session.yaml, session_loader.py |
| Tests to write | 5 | test_session_loader.py |
| Dependencies | 2 | loader.py (base), MCP memory tools |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | MCP memory query, checkpoint file parsing |
| Risk of regression | Low | New files, existing IdentityLoader pattern proven |
| External dependencies | Medium | MCP haios-memory server for ID lookup |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests + session.yaml config | 30 min | High |
| SessionLoader class | 45 min | High |
| Recipe + wiring | 15 min | High |
| **Total** | ~90 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# coldstart.md - Step 4-6 (manual agent steps)
## Step 4: Load Checkpoint Manifest
Find the most recent checkpoint in `docs/checkpoints/` and read its frontmatter.
ls -t docs/checkpoints/*.md | head -1

## Step 5: Load Principles (from manifest)
For each file in `load_principles`: Read the file

## Step 6: Load Memory (from manifest)
For each concept ID in `load_memory_refs`:
SELECT id, type, content FROM concepts WHERE id IN ({load_memory_refs})
```

**Behavior:** Agent manually executes 6 steps: find checkpoint, read file, parse frontmatter, query each memory ID individually, surface drift warnings, surface pending.

**Result:** Token waste (~500 tokens per coldstart), fragile multi-step process, easy to skip memory queries.

### Desired State

```python
# .claude/haios/lib/session_loader.py
class SessionLoader:
    """Extract session context from latest checkpoint + memory."""

    def load(self) -> str:
        """Returns formatted session context for injection."""
        extracted = self.extract()  # checkpoint fields + memory content
        return self.format(extracted)  # ~30 lines injection-ready
```

**Behavior:** Single `just session-context` command outputs complete session context.

**Result:** Token-efficient (~30 lines), reliable, memory refs always queried.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: SessionLoader loads from config
```python
def test_session_loader_loads_config():
    """SessionLoader reads session.yaml config file."""
    loader = SessionLoader()
    assert loader.config is not None
    assert "sources" in loader.config
```

### Test 2: Extract finds latest checkpoint
```python
def test_extract_finds_latest_checkpoint(tmp_path):
    """extract() finds and parses latest checkpoint file."""
    # Setup: create two checkpoint files
    cp_dir = tmp_path / "docs" / "checkpoints"
    cp_dir.mkdir(parents=True)
    (cp_dir / "2026-01-22-session-228.md").write_text("---\nsession: 228\n---")
    (cp_dir / "2026-01-24-session-229.md").write_text("---\nsession: 229\npending: []\n---")

    loader = SessionLoader(checkpoint_dir=cp_dir)
    extracted = loader.extract()

    assert extracted["prior_session"] == 229  # Latest by name sort
```

### Test 3: Extract parses memory_refs
```python
def test_extract_parses_memory_refs(tmp_path):
    """extract() gets load_memory_refs from checkpoint frontmatter."""
    cp_dir = tmp_path / "docs" / "checkpoints"
    cp_dir.mkdir(parents=True)
    (cp_dir / "2026-01-24-checkpoint.md").write_text("""---
session: 229
load_memory_refs:
  - 82302
  - 82303
---""")

    loader = SessionLoader(checkpoint_dir=cp_dir)
    extracted = loader.extract()

    assert extracted["memory_refs"] == [82302, 82303]
```

### Test 4: Format produces output with drift prominent
```python
def test_format_drift_prominent():
    """format() makes drift warnings visually prominent."""
    loader = SessionLoader()
    extracted = {
        "prior_session": 228,
        "completed": ["WORK-009"],
        "pending": ["Next task"],
        "drift_observed": ["Stale work item"],
        "memory_content": "Prior reasoning..."
    }

    formatted = loader.format(extracted)

    # Drift warnings should be prominent (e.g., with === or WARNING markers)
    assert "DRIFT" in formatted.upper() or "WARNING" in formatted.upper()
    assert "Stale work item" in formatted
```

### Test 5: Load returns injection-ready string
```python
def test_load_returns_string(tmp_path):
    """load() returns formatted string for context injection."""
    cp_dir = tmp_path / "docs" / "checkpoints"
    cp_dir.mkdir(parents=True)
    (cp_dir / "2026-01-24-checkpoint.md").write_text("""---
session: 229
completed: [WORK-009]
pending: [Pick next work]
drift_observed: []
load_memory_refs: []
---""")

    loader = SessionLoader(checkpoint_dir=cp_dir)
    result = loader.load()

    assert isinstance(result, str)
    assert "SESSION" in result.upper()
    assert "229" in result
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does.
     Future agents should be able to implement from this section alone.
     This section bridges the gap between tests (WHAT) and steps (HOW).

     MUST INCLUDE (per Session 88 enhancement):
     1. Actual current code that will be changed (copy from source)
     2. Exact diff/change to be made
     3. Function signature details with context
     4. Input/output examples with REAL data from the system

     PATTERN VERIFICATION (E2-255 Learning):
     IF creating a new module that imports from siblings:
       - MUST read at least one sibling module for import/error patterns
       - Verify: try/except conditional imports? sys.path manipulation? error types?
       - Use the SAME patterns as existing siblings (consistency > preference)

     IF modifying existing module:
       - Follow existing patterns in that file

     IF creating module with no siblings (new directory):
       - Document chosen patterns in Key Design Decisions with rationale -->

### New File 1: session.yaml config

**File:** `.claude/haios/config/loaders/session.yaml`

```yaml
# Session context extraction config per CH-005 spec
# Extracts checkpoint frontmatter + queries memory refs

# Checkpoint is found dynamically (latest in directory)
checkpoint_dir: "docs/checkpoints/"

# Fields to extract from checkpoint frontmatter
extract:
  prior_session:
    field: session
    type: frontmatter
  completed:
    field: completed
    type: frontmatter
  pending:
    field: pending
    type: frontmatter
  drift_observed:
    field: drift_observed
    type: frontmatter
  memory_refs:
    field: load_memory_refs
    type: frontmatter

# Memory query (uses MCP tool)
memory:
  method: query_ids
  ids_field: memory_refs
  query_fields: [id, type, content]

# Output formatting
output:
  template: |
    === SESSION CONTEXT ===
    Prior Session: {prior_session}

    Completed last session:
    {completed}

    === DRIFT WARNINGS ===
    {drift_observed}

    Memory from prior session:
    {memory_content}

    Pending:
    {pending}
  list_separator: "\n- "
```

### New File 2: SessionLoader class

**File:** `.claude/haios/lib/session_loader.py`

```python
"""
Session Loader for Configuration Arc.

CH-005: Implements session context loading for coldstart Phase 2.
Follows IdentityLoader pattern (WORK-007).

Extracts checkpoint frontmatter and queries memory refs for
token-efficient session context injection.
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml

CONFIG_DIR = Path(__file__).parent.parent / "config" / "loaders"
DEFAULT_CONFIG = CONFIG_DIR / "session.yaml"
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class SessionLoader:
    """
    Extract session context from latest checkpoint + memory.

    Uses session.yaml config to extract:
    - Prior session number
    - Completed work
    - Pending items
    - Drift warnings (PROMINENT)
    - Memory refs content
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        checkpoint_dir: Optional[Path] = None,
        memory_query_fn: Optional[callable] = None,
    ):
        self.config_path = config_path or DEFAULT_CONFIG
        self._checkpoint_dir = checkpoint_dir
        self._memory_query_fn = memory_query_fn
        self._load_config()

    def _load_config(self) -> None:
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {}

    @property
    def checkpoint_dir(self) -> Path:
        if self._checkpoint_dir:
            return self._checkpoint_dir
        return PROJECT_ROOT / self.config.get("checkpoint_dir", "docs/checkpoints/")

    def _find_latest_checkpoint(self) -> Optional[Path]:
        """Find most recent checkpoint by filename sort."""
        checkpoints = sorted(self.checkpoint_dir.glob("*.md"), reverse=True)
        checkpoints = [cp for cp in checkpoints if cp.name != "README.md"]
        return checkpoints[0] if checkpoints else None

    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown."""
        if not content.strip().startswith("---"):
            return {}
        import re
        match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError:
                return {}
        return {}

    def _query_memory_ids(self, ids: List[int]) -> str:
        """Query memory for concept IDs."""
        if not ids:
            return "(no memory refs)"
        if self._memory_query_fn:
            return self._memory_query_fn(ids)
        # Default: format IDs for manual query (fallback)
        return f"Memory IDs to query: {ids}"

    def extract(self) -> Dict[str, Any]:
        """Extract session context from checkpoint + memory."""
        result = {
            "prior_session": None,
            "completed": [],
            "pending": [],
            "drift_observed": [],
            "memory_refs": [],
            "memory_content": "",
        }

        checkpoint = self._find_latest_checkpoint()
        if not checkpoint:
            return result

        content = checkpoint.read_text(encoding="utf-8")
        fm = self._parse_frontmatter(content)

        result["prior_session"] = fm.get("session")
        result["completed"] = fm.get("completed", [])
        result["pending"] = fm.get("pending", [])
        result["drift_observed"] = fm.get("drift_observed", [])
        result["memory_refs"] = fm.get("load_memory_refs", [])
        result["memory_content"] = self._query_memory_ids(result["memory_refs"])

        return result

    def format(self, extracted: Dict[str, Any]) -> str:
        """Format extracted data for injection."""
        output_config = self.config.get("output", {})
        template = output_config.get("template", "")
        sep = output_config.get("list_separator", "\n- ")

        if not template:
            # Default template with drift prominence
            template = """=== SESSION CONTEXT ===
Prior Session: {prior_session}

Completed last session:
{completed}

=== DRIFT WARNINGS ===
{drift_observed}

Memory from prior session:
{memory_content}

Pending:
{pending}"""

        # Format lists
        format_vals = {}
        for k, v in extracted.items():
            if isinstance(v, list):
                format_vals[k] = sep.join(str(i) for i in v) if v else "(none)"
            else:
                format_vals[k] = v if v is not None else "(unknown)"

        return template.format(**format_vals)

    def load(self) -> str:
        """Extract and format in one call."""
        return self.format(self.extract())


if __name__ == "__main__":
    loader = SessionLoader()
    print(loader.load())
```

### Call Chain Context

```
just session-context
    |
    +-> python -c "...SessionLoader().load()"
            |
            +-> SessionLoader.load()
            |       |
            |       +-> extract() -> finds checkpoint, parses frontmatter
            |       |       |
            |       |       +-> _query_memory_ids() -> formats memory content
            |       |
            |       +-> format() -> applies template
            |
            Returns: str (injection-ready)
```

### Function/Component Signatures

```python
class SessionLoader:
    def __init__(
        self,
        config_path: Optional[Path] = None,
        checkpoint_dir: Optional[Path] = None,
        memory_query_fn: Optional[callable] = None,
    ):
        """
        Initialize session loader.

        Args:
            config_path: Path to session.yaml (default: standard location)
            checkpoint_dir: Override checkpoint directory (for testing)
            memory_query_fn: Optional function to query memory IDs

        Raises:
            FileNotFoundError: If config file not found (graceful degradation)
        """

    def extract(self) -> Dict[str, Any]:
        """
        Extract session context from latest checkpoint.

        Returns:
            Dict with: prior_session, completed, pending, drift_observed,
                       memory_refs, memory_content
        """

    def format(self, extracted: Dict[str, Any]) -> str:
        """
        Format extracted data using output template.

        Args:
            extracted: Dict from extract()

        Returns:
            Formatted string with drift warnings prominent
        """

    def load(self) -> str:
        """
        Extract and format in one call.

        Returns:
            Injection-ready string (~30 lines)
        """
```

### Behavior Logic

**Current Flow (manual steps):**
```
Coldstart → Agent reads coldstart.md → Executes 6 manual steps → Context loaded
                                            |
                                            +-> Often skips memory_refs query
```

**New Flow:**
```
Coldstart → just session-context → SessionLoader.load()
                                        |
                                        +-> find_latest_checkpoint()
                                        +-> parse_frontmatter()
                                        +-> query_memory_ids() (ALWAYS)
                                        +-> format() with drift PROMINENT
                                        |
                                    Returns: ~30 lines injection-ready
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Follow IdentityLoader pattern | Yes | Proven pattern from WORK-007, same base Loader class, consistent API |
| Memory query as optional callable | Inject via constructor | Testability - can mock memory query without MCP dependency in tests |
| Drift warnings prominent | Dedicated `=== DRIFT WARNINGS ===` header | CH-005 R3 requirement - agent cannot miss drift |
| No memory semantic search | ID lookup only | CH-005 Non-Goal - semantic search is separate concern |
| Graceful degradation | Return defaults if no checkpoint | Avoid crashes on fresh workspace |

### Input/Output Examples

**Current (Manual Steps):**
```
Agent executes:
1. ls -t docs/checkpoints/*.md | head -1
   Returns: docs/checkpoints/2026-01-22-04-SESSION-228-work-009-complete-coldstart-identity-injection-wired.md
2. Read tool on that file
3. Parse frontmatter manually
4. mcp__haios-memory__db_query for each ID in load_memory_refs: [82302, 82303, 82304, 82305, 82306, 82307]
5. More parsing...

Problem: 6+ tool calls, ~500 tokens consumed, easy to skip memory query step
```

**After (Single Command):**
```
just session-context
Returns:
=== SESSION CONTEXT ===
Prior Session: 228

Completed last session:
- WORK-009 Coldstart Orchestrator - Wire ContextLoader

=== DRIFT WARNINGS ===
(none)

Memory from prior session:
- 82302: Key insight: justfile recipes -> cli.py -> modules is the correct layer stack
- 82303: Content injection via recipe output eliminates Read calls for L0-L4 manifesto

Pending:
- Pick next work from queue (E2-072, INV-017, etc.)

Improvement: ~30 lines, single command, memory refs ALWAYS queried
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No checkpoint files | Return defaults with "(none)" values | Test 5 |
| Empty memory_refs | Skip query, return "(no memory refs)" | Test 3 |
| Malformed frontmatter | Return empty dict, log warning | Implicit in parse |
| Missing config file | Use hardcoded defaults | Constructor graceful |

### Open Questions

**Q: Should memory query use MCP tool directly or via MemoryBridge?**

A: For testability, inject query function via constructor. Production uses MCP tool, tests mock it. This matches IdentityLoader pattern where external dependencies are injectable.

---

## Open Decisions (MUST resolve before implementation)

<!-- No operator_decisions in work item - none blocked -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| (none) | - | - | Work item has no operator_decisions field |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_session_loader.py` with 5 tests from Tests First section
- [ ] Verify all tests fail (red) - SessionLoader doesn't exist yet

### Step 2: Create session.yaml config
- [ ] Create `.claude/haios/config/loaders/session.yaml` per design
- [ ] Test 1 passes (config loads)

### Step 3: Implement SessionLoader class
- [ ] Create `.claude/haios/lib/session_loader.py` per design
- [ ] Tests 2, 3, 4, 5 pass (green)

### Step 4: Add just session-context recipe
- [ ] Add recipe to justfile following `identity` pattern
- [ ] Verify `just session-context` outputs formatted content

### Step 5: Register SessionLoader in ContextLoader
- [ ] Add import in `context_loader.py` `_register_default_loaders()`
- [ ] Add "session" to haios.yaml context.roles (optional for future use)

### Step 6: Update coldstart.md Phase 2
- [ ] Modify coldstart.md Step 4-6 to use `just session-context`
- [ ] Remove manual checkpoint/memory steps

### Step 7: Integration Verification
- [ ] All new tests pass
- [ ] Run full test suite (no regressions): `pytest`
- [ ] Manual test: `just session-context` outputs expected format

### Step 8: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/lib/README.md` with session_loader.py
- [ ] **MUST:** Update `.claude/haios/config/loaders/README.md` if exists
- [ ] **MUST:** Verify README content matches actual file state

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment - misinterpreting CH-005 requirements | Medium | Verified: CH-005 spec read, R1-R4 mapped to deliverables |
| Integration - memory query without MCP available | Medium | Injectable query function allows graceful fallback |
| Regression - breaking existing coldstart | Low | Existing identity loading unchanged, additive change |
| Scope creep - adding semantic search | Medium | Explicit Non-Goal in CH-005: "Memory search (just ID lookup)" |
| Knowledge gap - checkpoint frontmatter variations | Low | Real checkpoint examined, fields confirmed in schema |

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

**MUST** read `docs/work/active/CH-005/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| R1: session.yaml config | [ ] | File exists at `.claude/haios/config/loaders/session.yaml` |
| R2: SessionLoader class | [ ] | File exists at `.claude/haios/lib/session_loader.py` |
| R3: Memory integration | [ ] | `_query_memory_ids()` method formats memory content |
| R4: Drift prominence | [ ] | Output contains `=== DRIFT WARNINGS ===` header |
| R5: just session-context recipe | [ ] | `just session-context` executes and outputs content |
| R6: Coldstart Phase 2 wiring | [ ] | coldstart.md updated to use `just session-context` |
| Tests | [ ] | `pytest tests/test_session_loader.py -v` passes |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/config/loaders/session.yaml` | Config with checkpoint_dir, extract, output | [ ] | |
| `.claude/haios/lib/session_loader.py` | SessionLoader class with load() method | [ ] | |
| `tests/test_session_loader.py` | 5 tests covering extract/format/load | [ ] | |
| `justfile` | session-context recipe added | [ ] | |
| `.claude/commands/coldstart.md` | Steps 4-6 use session-context | [ ] | |
| `.claude/haios/lib/README.md` | **MUST:** Lists session_loader.py | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_session_loader.py -v
# Expected: 5 tests passed

just session-context
# Expected: ~30 lines formatted session context
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

- @.claude/haios/epochs/E2_3/arcs/configuration/CH-005-session-loader.md (chapter spec)
- @.claude/haios/lib/identity_loader.py (sibling pattern)
- @.claude/haios/lib/loader.py (base class)
- @.claude/haios/config/loaders/identity.yaml (config pattern)
- @docs/checkpoints/2026-01-22-04-SESSION-228-work-009-complete-coldstart-identity-injection-wired.md (latest checkpoint)
- Memory concepts: 81257 (checkpoint as manifest), 81237 (memory_refs query), 82310 (identity wiring pattern)

---
