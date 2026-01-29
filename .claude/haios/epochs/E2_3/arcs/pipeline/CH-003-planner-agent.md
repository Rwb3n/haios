# generated: 2026-01-29
# System Auto: last updated on: 2026-01-29T18:35:32
# Chapter: PlannerAgent

## Definition

**Chapter ID:** CH-003
**Arc:** pipeline
**Status:** Planned
**Work Item:** WORK-032
**Implementation:** `.claude/haios/modules/planner_agent.py`

---

## Problem

RequirementExtractor produces `RequirementSet` with structured requirements. But there's no automated path from requirements to work items:

**Current state:**
```
Requirements (REQ-TRACE-001, REQ-CONTEXT-001, etc.)
    ↓
[MANUAL] Agent reads requirements, creates work items
    ↓
Work Items (WORK-XXX)
```

**Gap:** Pipeline PLAN stage needs to automatically decompose requirements into work items.

---

## Agent Need

> "Given a set of requirements, I need to produce a work plan that breaks them into implementable work items with dependencies."

---

## Requirements

### R1: WorkPlan Schema

```yaml
work_plan:
  source_requirements: RequirementSet
  created_at: datetime
  planner_version: string

work_items:
  - id: string                # Auto-generated WORK-XXX
    title: string
    type: enum[feature, investigation, bug, chore, spike]
    requirement_refs: list[string]  # REQ-IDs this implements
    acceptance_criteria: list[string]  # Derived from requirements
    dependencies: list[string]  # Other work item IDs
    estimated_effort: enum[small, medium, large]
    priority: enum[critical, high, medium, low]

dependency_graph:
  - from: WORK-001
    to: WORK-002
    type: blocks
```

### R2: PlannerAgent Interface

```python
class PlannerAgent:
    def __init__(self, requirements: RequirementSet):
        """Initialize with requirements to plan."""

    def plan(self) -> WorkPlan:
        """Generate work plan from requirements."""

    def suggest_groupings(self) -> List[RequirementGroup]:
        """Suggest how requirements could be grouped into work items."""

    def estimate_dependencies(self) -> DependencyGraph:
        """Estimate dependencies between potential work items."""
```

### R3: Grouping Heuristics

Requirements should be grouped by:
1. **Domain:** REQ-TRACE-*, REQ-CONTEXT-*, REQ-GOVERN-*
2. **Strength:** MUST requirements before SHOULD
3. **Dependencies:** Requirements that depend on each other

### R4: CLI Integration

```bash
python .claude/haios/modules/cli.py plan <requirements_file>
python .claude/haios/modules/cli.py plan --from-corpus <corpus_config>
```

---

## Success Criteria

- [ ] WorkPlan schema defined
- [ ] PlannerAgent class implements plan(), suggest_groupings()
- [ ] Requirements grouped by domain/strength
- [ ] Dependencies estimated from derives_from links
- [ ] CLI command works
- [ ] Tests verify planning with sample requirements

---

## Non-Goals

- Work item creation (that's WorkEngine's job)
- Execution (that's BUILD stage)
- Human-level design decisions (agent suggests, operator approves)

---

## Dependencies

- **CH-002 RequirementExtractor:** Provides RequirementSet input
- **WorkEngine:** Creates work items from WorkPlan
- **S26:** Pipeline architecture (stage interfaces)

---

## Design Questions

1. **Auto-create vs suggest?** Should PlannerAgent create work items or just suggest them for approval?
   - Recommendation: Suggest for approval (reversibility principle)

2. **Granularity?** One work item per requirement, or grouped?
   - Recommendation: Group by domain, user approves groupings

3. **Human-in-loop?** At what point does operator review?
   - Recommendation: After suggest_groupings(), before plan() finalizes

---

## References

- @.claude/haios/modules/requirement_extractor.py (input source)
- @.claude/haios/modules/work_engine.py (work item creation)
- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md (stage interface)
- @.claude/haios/manifesto/L4/agent_user_requirements.md (Project Foreman role)
