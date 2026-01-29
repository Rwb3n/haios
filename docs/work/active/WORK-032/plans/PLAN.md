---
template: implementation_plan
status: approved
date: 2026-01-29
backlog_id: WORK-032
title: PlannerAgent Module Implementation
author: Hephaestus
lifecycle_phase: plan
session: 247
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-29T20:22:02'
---
# Implementation Plan: PlannerAgent Module Implementation

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

PlannerAgent module will transform a RequirementSet into a WorkPlan with grouped work items, dependency graph, and execution order, completing the PLAN stage of the Pipeline.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `cli.py` (add plan commands) |
| Lines of code affected | ~30 | CLI dispatch additions |
| New files to create | 2 | `planner_agent.py`, `tests/test_planner_agent.py` |
| Tests to write | 8 | Based on CH-003 success criteria |
| Dependencies | 2 | RequirementExtractor (input), WorkEngine (future consumer) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | RequirementExtractor input, WorkEngine output |
| Risk of regression | Low | New module, no existing behavior to break |
| External dependencies | Low | Pure Python, no external APIs |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests First | 30 min | High |
| PlannerAgent Implementation | 60 min | High |
| CLI Integration | 20 min | High |
| Integration Testing | 20 min | High |
| **Total** | ~2.5 hr | High |

---

## Current State vs Desired State

### Current State

```python
# No PlannerAgent exists - manual workflow
# Agent reads requirements manually, creates work items one by one

# Current pipeline gap:
# CORPUS -> INGEST (RequirementExtractor) -> ??? -> BUILD -> VALIDATE
```

**Behavior:** No automated path from RequirementSet to work items. Agent must manually read requirements and create work items.

**Result:** Pipeline is incomplete. PLAN stage missing per S26.

### Desired State

```python
# .claude/haios/modules/planner_agent.py - NEW
from requirement_extractor import RequirementSet, Requirement

class PlannerAgent:
    def __init__(self, requirements: RequirementSet):
        self.requirements = requirements

    def plan(self) -> WorkPlan:
        """Generate work plan from requirements."""
        groupings = self.suggest_groupings()
        deps = self.estimate_dependencies()
        return self._build_plan(groupings, deps)

    def suggest_groupings(self) -> List[RequirementGroup]:
        """Suggest requirement groupings for operator review."""
        # Group by domain (REQ-TRACE-*, REQ-CONTEXT-*, etc.)

    def estimate_dependencies(self) -> DependencyGraph:
        """Estimate dependencies from derives_from links."""
```

**Behavior:** PlannerAgent takes RequirementSet, groups by domain, estimates dependencies, produces WorkPlan.

**Result:** Pipeline complete: INGEST -> PLAN -> BUILD -> VALIDATE. Operator approves groupings.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: WorkPlan Schema Validation
```python
def test_work_plan_schema():
    """WorkPlan has required fields per S26."""
    plan = WorkPlan(
        source_requirements=RequirementSet(...),
        created_at=datetime.now(),
        planner_version="1.0.0",
        work_items=[],
        execution_order=[]
    )
    assert hasattr(plan, 'source_requirements')
    assert hasattr(plan, 'work_items')
    assert hasattr(plan, 'execution_order')
```

### Test 2: PlannerAgent Accepts RequirementSet
```python
def test_planner_agent_init(sample_requirement_set):
    """PlannerAgent initializes with RequirementSet."""
    planner = PlannerAgent(sample_requirement_set)
    assert planner.requirements == sample_requirement_set
```

### Test 3: Suggest Groupings by Domain
```python
def test_suggest_groupings_by_domain():
    """suggest_groupings() groups requirements by domain prefix."""
    reqs = RequirementSet(
        source_corpus="test",
        extracted_at=datetime.now(),
        extractor_version="1.0",
        requirements=[
            Requirement(id="REQ-TRACE-001", description="...", source=...),
            Requirement(id="REQ-TRACE-002", description="...", source=...),
            Requirement(id="REQ-CONTEXT-001", description="...", source=...)
        ]
    )
    planner = PlannerAgent(reqs)
    groupings = planner.suggest_groupings()

    assert len(groupings) == 2  # TRACE and CONTEXT
    trace_group = next(g for g in groupings if g.domain == "TRACE")
    assert len(trace_group.requirements) == 2
```

### Test 4: Estimate Dependencies from derives_from
```python
def test_estimate_dependencies():
    """estimate_dependencies() uses derives_from links."""
    reqs = RequirementSet(
        source_corpus="test",
        extracted_at=datetime.now(),
        extractor_version="1.0",
        requirements=[
            Requirement(id="REQ-001", description="Base", derives_from=[], source=...),
            Requirement(id="REQ-002", description="Derived", derives_from=["REQ-001"], source=...)
        ]
    )
    planner = PlannerAgent(reqs)
    deps = planner.estimate_dependencies()

    assert ("REQ-002", "REQ-001") in deps.edges  # REQ-002 depends on REQ-001
```

### Test 5: Plan Produces WorkPlan
```python
def test_plan_produces_work_plan(sample_requirement_set):
    """plan() returns WorkPlan with work items."""
    planner = PlannerAgent(sample_requirement_set)
    plan = planner.plan()

    assert isinstance(plan, WorkPlan)
    assert len(plan.work_items) > 0
    assert plan.planner_version == PlannerAgent.VERSION
```

### Test 6: Work Items Have requirement_refs
```python
def test_work_items_have_requirement_refs():
    """Generated work items reference source requirements."""
    reqs = RequirementSet(...)
    planner = PlannerAgent(reqs)
    plan = planner.plan()

    for item in plan.work_items:
        assert len(item.requirement_refs) > 0
        assert all(ref.startswith("REQ-") for ref in item.requirement_refs)
```

### Test 7: Execution Order Respects Dependencies
```python
def test_execution_order_respects_dependencies():
    """execution_order has dependencies before dependents."""
    reqs = RequirementSet(
        requirements=[
            Requirement(id="REQ-001", derives_from=[], ...),
            Requirement(id="REQ-002", derives_from=["REQ-001"], ...)
        ]
    )
    planner = PlannerAgent(reqs)
    plan = planner.plan()

    # Work item containing REQ-001 should come before REQ-002 in order
    # (Implementation will verify via topological sort)
```

### Test 8: CLI Integration
```python
def test_cli_plan_command(tmp_path):
    """CLI plan command produces output."""
    # Setup: create test corpus with requirements
    result = subprocess.run(
        ["python", ".claude/haios/modules/cli.py", "plan", str(tmp_path)],
        capture_output=True, text=True
    )
    assert result.returncode == 0 or "WorkPlan" in result.stdout
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

### Exact Code Change

**File 1: NEW `.claude/haios/modules/planner_agent.py`**

Core data classes (CH-003 R1: WorkPlan Schema):

```python
@dataclass
class PlannedWorkItem:
    """A work item suggested by the planner."""
    id: str  # Suggested WORK-PXXX
    title: str
    type: str = "feature"
    requirement_refs: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    estimated_effort: str = "medium"
    priority: str = "medium"

@dataclass
class RequirementGroup:
    """A group of requirements to become a single work item."""
    domain: str  # e.g., "TRACE", "CONTEXT"
    requirements: List[Requirement] = field(default_factory=list)
    suggested_title: str = ""

@dataclass
class DependencyGraph:
    """Graph of dependencies between requirements/work items."""
    edges: List[Tuple[str, str]] = field(default_factory=list)
    nodes: Set[str] = field(default_factory=set)

    def topological_sort(self) -> List[str]:
        """Return nodes in dependency order (Kahn's algorithm)."""

@dataclass
class WorkPlan:
    """Output of the PLAN stage per S26."""
    source_requirements: RequirementSet
    created_at: datetime
    planner_version: str
    work_items: List[PlannedWorkItem] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    dependency_graph: DependencyGraph = field(default_factory=DependencyGraph)
```

**File 2: MODIFY `.claude/haios/modules/cli.py`**

Add to main() dispatch (around line 425):

```python
    elif cmd == "plan":
        if len(sys.argv) < 3:
            print("Usage: cli.py plan <requirements_path>")
            print("       cli.py plan --from-corpus <corpus_config>")
            return 1
        if sys.argv[2] == "--from-corpus":
            return cmd_plan_from_corpus(sys.argv[3])
        return cmd_plan(sys.argv[2])
```

### Call Chain Context

```
RequirementExtractor.extract()
    |
    +-> RequirementSet
            |
            +-> PlannerAgent(requirements)  # <-- NEW
                    |
                    +-> suggest_groupings()
                    |       Returns: List[RequirementGroup]
                    |
                    +-> estimate_dependencies()
                    |       Returns: DependencyGraph
                    |
                    +-> plan()
                            Returns: WorkPlan
                                |
                                +-> WorkEngine (future: create work items)
```

### Function/Component Signatures

```python
class PlannerAgent:
    """PLAN stage component per S26."""

    VERSION = "1.0.0"

    def __init__(self, requirements: RequirementSet):
        """Initialize with requirements to plan."""

    def suggest_groupings(self) -> List[RequirementGroup]:
        """Suggest how requirements could be grouped into work items.

        Groups by domain (REQ-TRACE-*, REQ-CONTEXT-*, etc.).

        Returns:
            List of RequirementGroup for operator review.
        """

    def estimate_dependencies(self) -> DependencyGraph:
        """Estimate dependencies from derives_from links.

        Returns:
            DependencyGraph with edges and topological sort.
        """

    def plan(self, approved_groupings: Optional[List[RequirementGroup]] = None) -> WorkPlan:
        """Generate work plan from requirements.

        Args:
            approved_groupings: Optional operator-approved groupings.

        Returns:
            WorkPlan with work items and execution order.
        """
```

### Behavior Logic

**Grouping Flow:**
```
RequirementSet
    |
    +-> Group by domain
    |       REQ-TRACE-001, REQ-TRACE-002 -> TRACE group
    |       REQ-CONTEXT-001 -> CONTEXT group
    |
    +-> Sort within group by strength (MUST first)
    |
    +-> Return List[RequirementGroup]
```

**Planning Flow:**
```
RequirementSet + (optional approved groupings)
    |
    +-> For each group:
    |       Create PlannedWorkItem
    |       Map requirement IDs to work item ID
    |
    +-> Convert requirement dependencies to work item dependencies
    |       REQ-002 derives_from REQ-001
    |       -> WORK-P002 depends on WORK-P001
    |
    +-> Topological sort for execution order
    |       Kahn's algorithm
    |
    +-> Return WorkPlan
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Suggest for approval | `suggest_groupings()` separate from `plan()` | Operator decision: reversibility principle, human-in-loop |
| Group by domain | Extract domain from REQ-{DOMAIN}-NNN | Operator decision: domains are natural work boundaries |
| Work ID prefix | WORK-P### (P for "planned") | Distinguish from actual WORK-XXX until operator approves |
| Topological sort | Kahn's algorithm | Standard, handles DAGs, warns on cycles |
| Import pattern | try/except conditional | Matches sibling modules (work_engine.py lines 49-54) |
| RequirementStrength sort | MUST before SHOULD | Higher priority requirements first within group |

### Input/Output Examples

**Input (RequirementSet from L4 manifesto):**
```yaml
requirements:
  - id: REQ-TRACE-001
    description: "Work items trace to chapters"
    strength: MUST
    derives_from: []

  - id: REQ-TRACE-002
    description: "Close validates requirement"
    strength: MUST
    derives_from: [REQ-TRACE-001]

  - id: REQ-CONTEXT-001
    description: "Coldstart injects context"
    strength: MUST
    derives_from: []
```

**Output (WorkPlan):**
```yaml
work_items:
  - id: WORK-P001
    title: "Implement TRACE requirements"
    requirement_refs: [REQ-TRACE-001, REQ-TRACE-002]
    dependencies: []
    estimated_effort: small
    priority: high

  - id: WORK-P002
    title: "Implement CONTEXT requirements"
    requirement_refs: [REQ-CONTEXT-001]
    dependencies: []
    estimated_effort: small
    priority: high

execution_order: [WORK-P001, WORK-P002]
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Empty RequirementSet | Return empty WorkPlan | Implicit |
| Circular dependencies | Log warning, return partial order | Test 7 |
| No domain in ID | Domain = "GENERAL" | Test 3 edge |
| Single requirement | One work item, one group | Test 5 |

### Open Questions

**Q: Should plan() automatically create work items via WorkEngine?**

No - per CH-003 Non-Goals: "Work item creation (that's WorkEngine's job)". PlannerAgent suggests, WorkEngine creates. This keeps concerns separated.

---

## Open Decisions (Resolved in AMBIGUITY Phase)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Auto-create vs suggest | [auto-create, suggest for approval] | suggest for approval | Reversibility principle - operator reviews groupings before creation |
| Grouping granularity | [per-requirement, group by domain, group by strength] | group by domain | Domains are natural work boundaries (TRACE, CONTEXT, etc.) |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_planner_agent.py`
- [ ] Add all 8 tests from Tests First section
- [ ] Verify all tests fail (red) - module doesn't exist yet

### Step 2: Implement Data Classes
- [ ] Create `.claude/haios/modules/planner_agent.py`
- [ ] Implement PlannedWorkItem, RequirementGroup, DependencyGraph, WorkPlan
- [ ] Tests 1-2 pass (green)

### Step 3: Implement suggest_groupings()
- [ ] Implement _extract_domain()
- [ ] Implement suggest_groupings() with domain grouping
- [ ] Test 3 passes (green)

### Step 4: Implement estimate_dependencies()
- [ ] Implement DependencyGraph.add_edge()
- [ ] Implement DependencyGraph.topological_sort()
- [ ] Implement estimate_dependencies()
- [ ] Test 4 passes (green)

### Step 5: Implement plan()
- [ ] Implement _next_work_id()
- [ ] Implement plan() combining groupings and dependencies
- [ ] Tests 5-7 pass (green)

### Step 6: Add CLI Commands
- [ ] Add cmd_plan() function
- [ ] Add cmd_plan_from_corpus() function
- [ ] Add dispatch to main()
- [ ] Test 8 passes (green)

### Step 7: Integration Verification
- [ ] All tests pass: `pytest tests/test_planner_agent.py -v`
- [ ] Run full test suite: `pytest tests/ -v` (no regressions)

### Step 8: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with planner_agent.py entry
- [ ] **MUST:** Verify README content matches actual module state

### Step 9: Runtime Consumer Verification
- [ ] Verify PlannerAgent has CLI as runtime consumer
- [ ] Document future consumer: Orchestrator (CH-006)

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment | Medium | Verified interface matches S26 and CH-003 exactly |
| RequirementSet schema change | Medium | Import from requirement_extractor, don't duplicate |
| Cycle in dependencies | Low | DependencyGraph handles cycles with warning |
| Domain extraction fails | Low | Fallback to "GENERAL" domain |
| No runtime consumer yet | Low | CLI provides immediate consumer, Orchestrator is future |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 259 | 2026-01-29 | SESSION-259 | Plan authored | - |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-032/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| `.claude/haios/modules/planner_agent.py` - PlannerAgent class | [ ] | File exists, class defined |
| WorkPlan schema definition (dataclass) | [ ] | WorkPlan dataclass in module |
| `plan()` method produces WorkPlan from RequirementSet | [ ] | Test 5 passes |
| `suggest_groupings()` method for operator review | [ ] | Test 3 passes |
| `estimate_dependencies()` method using derives_from links | [ ] | Test 4 passes |
| Grouping heuristics (by domain, strength, dependencies) | [ ] | Tests 3-4 pass |
| CLI command: `plan <requirements_file>` | [ ] | Test 8 passes |
| CLI command: `plan --from-corpus <corpus_config>` | [ ] | Manual test |
| Unit tests: `tests/test_planner_agent.py` | [ ] | 8 tests exist |
| Integration with WorkEngine for work item creation | [ ] | Future - document only |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/planner_agent.py` | PlannerAgent class with plan(), suggest_groupings(), estimate_dependencies() | [ ] | |
| `.claude/haios/modules/cli.py` | plan command added | [ ] | |
| `tests/test_planner_agent.py` | 8 tests covering all acceptance criteria | [ ] | |
| `.claude/haios/modules/README.md` | **MUST:** Lists planner_agent.py | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest [test_file] -v
# Expected: X tests passed
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

- @.claude/haios/epochs/E2_3/arcs/pipeline/CH-003-planner-agent.md (chapter spec)
- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md (pipeline architecture)
- @.claude/haios/modules/requirement_extractor.py (input module)
- @.claude/haios/modules/work_engine.py (sibling import pattern)
- @.claude/haios/modules/corpus_loader.py (sibling module reference)

---
