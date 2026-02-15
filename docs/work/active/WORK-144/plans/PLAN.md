---
template: implementation_plan
status: complete
date: 2026-02-15
backlog_id: WORK-144
title: "Agent Capability Cards"
author: Hephaestus
lifecycle_phase: plan
session: 375
version: "1.5"
generated: 2026-02-15
last_updated: 2026-02-15T20:52:47
---
# Implementation Plan: Agent Capability Cards

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

All 11 HAIOS agents will have structured capability card frontmatter (trigger_conditions, input/output contracts, requirement_level, invoked_by, category, related_agents) enabling machine-discoverable agent selection without reading full system prompts.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 12 | 11 agent .md files + README.md in `.claude/agents/` |
| Lines of code affected | ~1542 | `wc -l .claude/agents/*.md` (frontmatter additions to each) |
| New files to create | 1 | `tests/test_agent_capability_cards.py` |
| Tests to write | 5 | Schema validation, completeness, backward compat, CLAUDE.md sync |
| Dependencies | 1 | CLAUDE.md agent table (consumer of agent metadata) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Frontmatter-only changes, no code imports |
| Risk of regression | Low | No existing tests for agent frontmatter; Claude Code reads name/description/tools/model |
| External dependencies | Low | No APIs; Claude Code plugin system auto-discovers agents |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Schema design + 11 agent updates | 30 min | High |
| README + CLAUDE.md update | 10 min | High |
| **Total** | **~55 min** | High |

---

## Current State vs Desired State

### Current State

```yaml
# .claude/agents/critique-agent.md:1-9 - Typical current frontmatter
---
name: critique-agent
description: Pre-implementation assumption surfacing. Framework loaded from haios.yaml config.
tools: Read, Glob
model: opus
color: yellow
generated: '2026-01-25'
last_updated: '2026-02-01T22:46:39'
---
```

**Behavior:** Claude Code auto-discovers agents by `name`, `description`, `tools`, and `model` fields. Additional metadata (requirement_level, trigger conditions, input/output contracts, invoked_by) is buried in markdown body — not machine-parseable.

**Result:** Agent selection requires reading full system prompt or relying on CLAUDE.md hardcoded table. No structured way to enumerate capabilities.

### Desired State

```yaml
# .claude/agents/critique-agent.md:1-18 - Target frontmatter with capability card
---
name: critique-agent
description: Pre-implementation assumption surfacing. Framework loaded from haios.yaml config.
tools: Read, Glob
model: opus
color: yellow
requirement_level: recommended
category: verification
trigger_conditions:
  - Before DO phase in implementation-cycle
  - When plan has significant architectural decisions
input_contract: "plan_path, work_id"
output_contract: "critique-report.md + assumptions.yaml with verdict (BLOCK/REVISE/PROCEED)"
invoked_by:
  - implementation-cycle (PLAN phase Gate 1)
related_agents:
  - anti-pattern-checker (post-hoc verification)
  - validation-agent (CHECK phase)
  - preflight-checker (plan readiness)
generated: '2026-01-25'
last_updated: '2026-02-15T21:00:00'
---
```

**Behavior:** All capability metadata is in frontmatter — machine-parseable, grep-able, enumerable without reading body.

**Result:** Agent selection can be done by querying frontmatter fields. CLAUDE.md agent table references these fields instead of hardcoding descriptions.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: All Agents Have Required Capability Card Fields
```python
def test_all_agents_have_capability_card_fields():
    """Every agent .md file must have the new capability card frontmatter fields."""
    import yaml
    from pathlib import Path

    agents_dir = Path(".claude/agents")
    required_fields = {"requirement_level", "category", "trigger_conditions",
                       "input_contract", "output_contract", "invoked_by", "related_agents"}

    for agent_file in sorted(agents_dir.glob("*.md")):
        if agent_file.name == "README.md":
            continue
        content = agent_file.read_text(encoding="utf-8")
        # Parse YAML frontmatter between --- delimiters
        parts = content.split("---", 2)
        assert len(parts) >= 3, f"{agent_file.name}: missing frontmatter"
        fm = yaml.safe_load(parts[1])
        for field in required_fields:
            assert field in fm, f"{agent_file.name}: missing field '{field}'"
```

### Test 2: Capability Card Field Values Are Valid
```python
def test_capability_card_field_values_valid():
    """Validate allowed values for enum-like fields."""
    import yaml
    from pathlib import Path

    agents_dir = Path(".claude/agents")
    valid_levels = {"required", "recommended", "optional"}
    valid_categories = {"gate", "verification", "utility", "cycle-delegation"}

    for agent_file in sorted(agents_dir.glob("*.md")):
        if agent_file.name == "README.md":
            continue
        content = agent_file.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        fm = yaml.safe_load(parts[1])
        assert fm["requirement_level"] in valid_levels, \
            f"{agent_file.name}: invalid requirement_level '{fm['requirement_level']}'"
        assert fm["category"] in valid_categories, \
            f"{agent_file.name}: invalid category '{fm['category']}'"
        assert isinstance(fm["trigger_conditions"], list), \
            f"{agent_file.name}: trigger_conditions must be a list"
        assert isinstance(fm["invoked_by"], list), \
            f"{agent_file.name}: invoked_by must be a list"
        assert isinstance(fm["related_agents"], list), \
            f"{agent_file.name}: related_agents must be a list"
```

### Test 3: Backward Compatibility - Existing Fields Preserved
```python
def test_existing_frontmatter_fields_preserved():
    """Existing fields (name, description, tools, model) must still be present."""
    import yaml
    from pathlib import Path

    agents_dir = Path(".claude/agents")
    core_fields = {"name", "description", "tools", "model"}

    for agent_file in sorted(agents_dir.glob("*.md")):
        if agent_file.name == "README.md":
            continue
        content = agent_file.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        fm = yaml.safe_load(parts[1])
        for field in core_fields:
            assert field in fm, f"{agent_file.name}: core field '{field}' missing after update"
```

### Test 4: Agent Count Is Exactly 11
```python
def test_agent_count():
    """Verify exactly 11 agent files exist (excluding README)."""
    from pathlib import Path

    agents_dir = Path(".claude/agents")
    agent_files = [f for f in agents_dir.glob("*.md") if f.name != "README.md"]
    assert len(agent_files) == 11, f"Expected 11 agents, found {len(agent_files)}: {[f.name for f in agent_files]}"
```

### Test 5: Input/Output Contracts Are Non-Empty Strings
```python
def test_contracts_are_nonempty():
    """input_contract and output_contract must be non-empty strings."""
    import yaml
    from pathlib import Path

    agents_dir = Path(".claude/agents")
    for agent_file in sorted(agents_dir.glob("*.md")):
        if agent_file.name == "README.md":
            continue
        content = agent_file.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        fm = yaml.safe_load(parts[1])
        assert isinstance(fm["input_contract"], str) and len(fm["input_contract"]) > 0, \
            f"{agent_file.name}: input_contract must be non-empty string"
        assert isinstance(fm["output_contract"], str) and len(fm["output_contract"]) > 0, \
            f"{agent_file.name}: output_contract must be non-empty string"
```

---

## Detailed Design

### Capability Card Schema

New YAML frontmatter fields to add to every agent `.md` file. These extend (not replace) the existing `name`, `description`, `tools`, `model` fields.

**Schema Definition:**

```yaml
# NEW fields (added after existing fields, before generated/last_updated)
requirement_level: required | recommended | optional
category: gate | verification | utility | cycle-delegation
trigger_conditions:            # list of strings - when to invoke
  - "description of trigger condition"
input_contract: "string describing what agent expects from parent"
output_contract: "string describing what agent returns to parent"
invoked_by:                    # list of strings - which skills/cycles invoke this
  - "skill-name (phase context)"
related_agents:                # list of strings - cross-references
  - "agent-name (relationship)"
```

### Agent-by-Agent Capability Card Data

Extracted from reading all 11 agent body sections:

| Agent | requirement_level | category | trigger_conditions | input_contract | output_contract | invoked_by | related_agents |
|-------|-------------------|----------|--------------------|----------------|-----------------|------------|----------------|
| anti-pattern-checker | recommended | verification | epoch/milestone/major completion claims | claim text + context file path | JSON: verified, lenses, verdict, gaps | manual invocation; checkpoint-cycle VERIFY | validation-agent, critique-agent |
| close-work-cycle-agent | optional | cycle-delegation | context limit approaching + work ready for closure | work_id | structured summary: cycle result, gates, DoD, artifacts | /close command; parent delegation | close-work-cycle skill, retro-cycle skill |
| critique-agent | recommended | verification | before DO phase; plan has architectural decisions | plan_path, work_id | critique-report.md + assumptions.yaml with verdict | implementation-cycle (PLAN Gate 1) | anti-pattern-checker, validation-agent, preflight-checker |
| implementation-cycle-agent | optional | cycle-delegation | context limit approaching + approved plan | work_id, plan_path | structured summary: cycle result, gates, artifacts | parent delegation | implementation-cycle skill, preflight-checker, validation-agent |
| investigation-agent | required | utility | EXPLORE phase of investigation-cycle | phase keyword + investigation context | phase-specific output (hypotheses/evidence/findings) | investigation-cycle (EXPLORE phase) | investigation-cycle-agent, memory-agent skill |
| investigation-cycle-agent | optional | cycle-delegation | context limit approaching + investigation work | work_id | structured summary: hypotheses, verdicts, spawned work | parent delegation | investigation-cycle skill, investigation-agent |
| preflight-checker | required | gate | PLAN-to-DO transition in implementation-cycle | plan_path, file_manifest (optional) | JSON: ready, phase, issues, warnings, blocked | implementation-cycle (PLAN exit gate) | critique-agent, validation-agent |
| schema-verifier | required | gate | any SQL query against haios_memory.db | table_name or query intent | schema info or SELECT query results | any agent needing DB access | none |
| test-runner | optional | utility | CHECK phase of implementation-cycle | test path or filter | structured summary: pass/fail, counts, failures | implementation-cycle (CHECK phase) | validation-agent |
| validation-agent | recommended | verification | CHECK phase of implementation-cycle | plan_path, implementation summary | structured summary: tests, demo, DoD checklist, verdict | implementation-cycle (CHECK phase) | test-runner, preflight-checker, critique-agent |
| why-capturer | recommended | utility | DONE phase of implementation-cycle | backlog_id, plan_path, context_summary | list of concept_ids stored to memory | implementation-cycle (DONE phase); close-work-cycle | ingester_ingest (tool) |

### Exact Code Change Pattern

Each agent file gets the same structural change: insert new fields into YAML frontmatter after existing fields, before `generated`/`last_updated`.

**Example — `critique-agent.md`:**

**Current frontmatter (lines 1-9):**
```yaml
---
name: critique-agent
description: Pre-implementation assumption surfacing. Framework loaded from haios.yaml
  config.
tools: Read, Glob
model: opus
color: yellow
generated: '2026-01-25'
last_updated: '2026-02-01T22:46:39'
---
```

**Target frontmatter:**
```yaml
---
name: critique-agent
description: Pre-implementation assumption surfacing. Framework loaded from haios.yaml
  config.
tools: Read, Glob
model: opus
color: yellow
requirement_level: recommended
category: verification
trigger_conditions:
  - Before DO phase in implementation-cycle
  - When plan has significant architectural decisions
input_contract: "plan_path, work_id"
output_contract: "critique-report.md + assumptions.yaml with verdict (BLOCK/REVISE/PROCEED)"
invoked_by:
  - implementation-cycle (PLAN phase Gate 1)
related_agents:
  - anti-pattern-checker (post-hoc verification)
  - validation-agent (CHECK phase)
  - preflight-checker (plan readiness)
generated: '2026-01-25'
last_updated: '2026-02-15T21:00:00'
---
```

**Diff pattern (same for all 11 agents):**
```diff
 model: opus
 color: yellow
+requirement_level: recommended
+category: verification
+trigger_conditions:
+  - Before DO phase in implementation-cycle
+  - When plan has significant architectural decisions
+input_contract: "plan_path, work_id"
+output_contract: "critique-report.md + assumptions.yaml with verdict (BLOCK/REVISE/PROCEED)"
+invoked_by:
+  - implementation-cycle (PLAN phase Gate 1)
+related_agents:
+  - anti-pattern-checker (post-hoc verification)
+  - validation-agent (CHECK phase)
+  - preflight-checker (plan readiness)
 generated: '2026-01-25'
```

### Call Chain Context

```
Claude Code Plugin System
    |
    +-> Auto-discovers .claude/agents/*.md
    |       Reads: name, description, tools, model (for Task tool)
    |
    +-> HAIOS agent invocations
    |       Task(subagent_type='agent-name', prompt='...')
    |       New fields: capability card metadata for selection
    |
    +-> CLAUDE.md agent table (consumer)
            References agent metadata for quick lookup
```

### README.md Update

Update `.claude/agents/README.md` to reflect new capability card fields in the Available Agents table and add a Schema section.

### CLAUDE.md Update

Update the Agents table in `CLAUDE.md` to add `Requirement` and `Category` columns sourced from frontmatter fields, replacing hardcoded descriptions.

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontmatter fields vs separate card file | Frontmatter fields | Keeps agent definition self-contained; Claude Code already parses frontmatter; no extra files to manage |
| String contracts vs structured schema | String descriptions | Contracts vary too much between agents for a rigid schema; strings are human+machine readable; sufficient for discovery |
| Category enum values | gate, verification, utility, cycle-delegation | Maps to existing README groupings; 4 values cover all 11 agents cleanly |
| requirement_level values | required, recommended, optional | Matches RFC 2119 convention already used in agent body text |
| Lists for trigger_conditions/invoked_by/related_agents | YAML lists | Multiple triggers/invokers per agent; lists are natural; grep-friendly |
| Insert position in frontmatter | After model/color, before generated | Groups capability metadata together; keeps timestamps at end |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Agent with no `color` field (10 of 11) | Insert after `model` field instead | Test 3 (backward compat) |
| Agent with `context: fork` field (2 agents) | Insert after `context` field | Test 3 (backward compat) |
| Empty related_agents (schema-verifier) | Use `related_agents: []` (empty list) | Test 2 (valid values) |
| Claude Code reads unknown frontmatter | Claude Code ignores unknown fields — safe to add | N/A (external behavior) |

### Open Questions

**Q: Does Claude Code break if unknown frontmatter fields are added?**

No — Claude Code reads `name`, `description`, `tools`, `model` and ignores other fields. Verified by the fact that `color`, `context`, `generated`, `last_updated` are already present and ignored by the Task tool dispatch. Adding more fields is safe.

---

## Open Decisions (MUST resolve before implementation)

No `operator_decisions` in WORK-144 frontmatter. No blocking decisions.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| (none) | — | — | No operator decisions required |

---

## Implementation Steps

### Step 1: Write Failing Tests (RED)
- [ ] Create `tests/test_agent_capability_cards.py` with all 5 tests
- [ ] Verify all 5 tests fail (agents don't have new fields yet)

### Step 2: Add Capability Card Fields to All 11 Agents
- [ ] Edit each agent .md file: insert capability card frontmatter using data from Detailed Design table
- [ ] Order: anti-pattern-checker, close-work-cycle-agent, critique-agent, implementation-cycle-agent, investigation-agent, investigation-cycle-agent, preflight-checker, schema-verifier, test-runner, validation-agent, why-capturer
- [ ] Tests 1-5 pass (GREEN)

### Step 3: Update README.md
- [ ] Update `.claude/agents/README.md` with capability card schema reference and updated table
- [ ] Add schema section documenting the new fields

### Step 4: Update CLAUDE.md Agent Table
- [ ] Update CLAUDE.md Agents table to include Requirement and Category columns from frontmatter

### Step 5: Integration Verification
- [ ] All 5 new tests pass
- [ ] Full test suite passes (no regressions)

### Step 6: Consumer Verification
- [ ] Grep for hardcoded agent descriptions in skills/hooks that could reference capability card fields
- [ ] Verify no stale references

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Claude Code breaks on unknown frontmatter fields | High | Already validated: `color`, `context`, `generated`, `last_updated` are unknown to Claude Code and work fine |
| Frontmatter YAML parsing errors from multi-line strings | Medium | Use quoted strings for contracts; test each file after edit |
| Capability card data extracted incorrectly from body | Medium | All 11 agent bodies read in AUTHOR phase; data table reviewed before implementation |
| Scope creep into building a discovery CLI tool | Low | Explicitly out of scope — deliverables are frontmatter + docs only |

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

**MUST** read `docs/work/active/WORK-144/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Agent Card schema defined as extended YAML frontmatter fields | [ ] | Schema documented in plan Detailed Design |
| Schema includes: trigger_conditions, input_contract, output_contract, invoked_by, requirement_level, related_agents | [ ] | All 7 fields present in frontmatter |
| All 11 agent .md files updated with capability card frontmatter | [ ] | Read each file, verify fields present |
| Cards backward-compatible (existing frontmatter fields preserved) | [ ] | Test 3 passes |
| CLAUDE.md agent table updated to reference capability card fields | [ ] | Read CLAUDE.md, verify table |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `tests/test_agent_capability_cards.py` | 5 tests, all passing | [ ] | |
| `.claude/agents/anti-pattern-checker.md` | Capability card fields in frontmatter | [ ] | |
| `.claude/agents/close-work-cycle-agent.md` | Capability card fields in frontmatter | [ ] | |
| `.claude/agents/critique-agent.md` | Capability card fields in frontmatter | [ ] | |
| `.claude/agents/implementation-cycle-agent.md` | Capability card fields in frontmatter | [ ] | |
| `.claude/agents/investigation-agent.md` | Capability card fields in frontmatter | [ ] | |
| `.claude/agents/investigation-cycle-agent.md` | Capability card fields in frontmatter | [ ] | |
| `.claude/agents/preflight-checker.md` | Capability card fields in frontmatter | [ ] | |
| `.claude/agents/schema-verifier.md` | Capability card fields in frontmatter | [ ] | |
| `.claude/agents/test-runner.md` | Capability card fields in frontmatter | [ ] | |
| `.claude/agents/validation-agent.md` | Capability card fields in frontmatter | [ ] | |
| `.claude/agents/why-capturer.md` | Capability card fields in frontmatter | [ ] | |
| `.claude/agents/README.md` | Updated with schema + new table | [ ] | |
| `CLAUDE.md` | Agent table updated with Requirement/Category | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_agent_capability_cards.py -v
# Expected: 5 tests passed
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

- @docs/work/active/WORK-144/WORK.md (work item)
- @.claude/agents/ (11 agent files — primary artifacts)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-DISCOVER-004)
- Memory 85155: Google A2A protocol Agent Cards pattern
- Memory 85211: Operator directive — create Agent Cards for all 11 agents

---
