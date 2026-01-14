---
template: investigation
status: complete
date: 2025-12-22
backlog_id: INV-022
title: "Investigation: Work-Cycle-DAG Unified Architecture"
author: Hephaestus
session: 98
lifecycle_phase: conclude
spawned_by: Session-98
related: [INV-011, INV-012, E2-076, E2-111, ADR-038]
memory_refs: [77243, 77244, 77245, 77246, 77247, 77248, 77249, 77250, 77251, 77252, 77253]
milestone: Future
version: "1.1"
generated: 2025-12-22
last_updated: 2025-12-23T09:40:38
---
# Investigation: Work-Cycle-DAG Unified Architecture

@docs/README.md
@docs/epistemic_state.md
@docs/investigations/INVESTIGATION-INV-011-work-item-as-file-architecture.md
@docs/investigations/INVESTIGATION-INV-012-workflow-state-machine-architecture.md
@docs/plans/PLAN-E2-076-dag-governance-architecture-adr.md

---

## Context

**Trigger:** Session 98 discussion about template guidance patterns and cycle skills.

**Operator Insight:**
> "The way that agents work successfully in this system, an example being template guidance - how the template's content forms a core for the agent to generate successful content. Thinking about the cycle skills and how they should scaffold all cycle docs from the start to ensure that steps aren't skipped."

**The Unified Vision:**
> "Anything can be work if we have a cycle designed for it. The work file arrives at each node, spawns all of that node's cycle docs. The agent has flexibility to move WITHIN the constraints that all cycle files are available, they must all be completed in order, and the agent cannot exit and move to another node until the cycle is complete. Work files can spawn other work files that proceed async - hence the DAG - but both can be blocked or unblocked by each other mechanistically."

**Prior Work Synthesis:**

| Investigation | Contribution | Gap |
|---------------|--------------|-----|
| **INV-011** | Work-item-as-file schema, "blood cell" metaphor | Doesn't address cycle scaffolding |
| **INV-012** | Workflow state machine, command/skill exits | Doesn't tie to work files |
| **E2-076** | DAG edges, cascade mechanism | Graph exists but nodes don't contain cycles |

This investigation unifies these threads into a coherent architecture.

---

## Objective

Design the **Work-Cycle-DAG** architecture where:

1. **Work Files** are entities that traverse a lifecycle DAG
2. **Nodes** are lifecycle phases that contain **Cycles** (investigation-cycle, implementation-cycle, etc.)
3. **Cycles** scaffold ALL their docs at node entry, ensuring no steps are skipped
4. **Agent Movement** is constrained: free within a cycle, gated at node exit
5. **Spawning** creates parallel work files that can block/unblock each other

**Core Pattern:** Template guidance (channeling) at the **cycle level**, not just the document level.

---

## Scope

### In Scope
- Unified architecture design merging INV-011 + INV-012 + E2-076
- Node-Cycle mapping (which cycle at which node)
- Scaffold-on-entry mechanism design
- In-order completion gates
- Work file spawning and mechanical blocking
- Integration with existing implementation-cycle and investigation-cycle skills

### Out of Scope (for this investigation)
- Implementation of the architecture (future milestone work)
- Memory system changes
- Individual tool implementations

---

## Hypotheses

| # | Hypothesis | Test Method | Priority |
|---|------------|-------------|----------|
| **H1** | Template channeling scales from documents to cycles | Analyze implementation-cycle/investigation-cycle success patterns | 1st |
| **H2** | Scaffold-on-entry prevents step skipping more reliably than exit-criteria prompts | Compare failure modes of current vs proposed | 2nd |
| **H3** | Mechanical blocking (frontmatter-based) is more reliable than prompt-based blocking | Review E2-076e cascade implementation | 3rd |
| **H4** | Work files can carry context across nodes without scattering | Design context accumulation schema | 4th |
| **H5** | DAG cycle containment is implementable with current tooling | Audit hooks, commands, skills | 5th |

---

## Investigation Steps

### Phase 1: Vision Capture (Session 98) - COMPLETE

1. [x] Document operator insight and unified vision
2. [x] Synthesize prior work (INV-011, INV-012, E2-076)
3. [x] Create this investigation document

### Phase 2: Architecture Design (Session 101) - COMPLETE

4. [x] **Node-Cycle Mapping** - See "Node-Cycle Mapping (Full Design)" in Findings
   - DISCOVERY → investigation-cycle
   - DESIGN → adr-cycle (NEW)
   - PLAN → plan-cycle (NEW)
   - IMPLEMENT → implementation-cycle
   - CLOSE → closure-cycle (NEW)

5. [x] **Scaffold-on-Entry Mechanism** - See "Scaffold-on-Entry Mechanism Design" in Findings
   - Trigger: current_node field change in work file
   - Hook: PostToolUse detects change, scaffolds via /new-{type}
   - Active indicator: cycle_docs field populated

6. [x] **In-Order Completion Gate** - See "Node Exit Gate Design" in Findings
   - PreToolUse blocks node transition if criteria not met
   - Criteria defined per node in binding config
   - Validates: status fields, section content, test results

7. [x] **Work File Schema Extension** - See "Work File Schema v2" in Findings
   - current_node, node_history, cycle_docs fields added
   - Directory structure: docs/work/{active,blocked,archive}/

8. [x] **Async Spawning Design** - Reuses E2-076 blocked_by/blocks edges
   - Work file spawns via spawned_by field
   - Mechanical blocking via existing cascade hooks

### Phase 3: Integration Design (Session 101) - COMPLETE

9. [x] **Skill-Node Binding** - See "Node-Cycle Binding Configuration" in Findings
   - Binding in configuration file: `.claude/config/node-cycle-bindings.yaml`
   - Each node specifies: cycle skill, scaffold commands, exit criteria

10. [x] **Tooling Impact** - Documented in mechanism designs
    - Hooks: PostToolUse scaffold-on-entry, PreToolUse exit gate
    - Commands: /enter-node, /exit-node (or extend existing)
    - Status: Work file frontmatter IS the status

---

## Findings

### Session 101 EXPLORE Findings

#### META-FAILURE: Agent Did Not Invoke Subagent

**Critical observation:** During this investigation, the agent (Claude) failed to invoke the `investigation-agent` subagent as documented in `.claude/agents/investigation-agent.md`. This is a real-time demonstration of H2.

| Expected | Actual | Root Cause |
|----------|--------|------------|
| `Task(subagent_type='investigation-agent')` | Agent did work directly | investigation-cycle says "RECOMMENDED" (L2), not "MUST" |
| Detailed findings in file | Summaries only | No enforcement of output format |

**This failure IS evidence for the investigation.** L2 guidance was ignored.

---

#### H1: Template Channeling Scales to Cycles - PARTIALLY CONFIRMED

**Evidence Table:**

| Pattern | Source | Works? | Why |
|---------|--------|--------|-----|
| Clear phase names | `.claude/skills/implementation-cycle/SKILL.md:24-29` | YES | Structure visible in ASCII diagram |
| Exit criteria checklists | `.claude/skills/implementation-cycle/SKILL.md:53-57` | PARTIAL | Agent can self-assess but no verification |
| Tools per phase | `.claude/skills/implementation-cycle/SKILL.md:180-188` | YES | Composition Map guides tool selection |
| SHOULD guardrails | `.claude/skills/implementation-cycle/SKILL.md:67-70` | NO | ">3 files pause" routinely skipped |
| Subagent invocation | `.claude/agents/investigation-agent.md:17-18` | NO | "RECOMMENDED" = L2 = ignored |

**What WORKS:**
- Clear phase names (structure visible)
- Exit criteria checklists (self-assessment)
- Tools per phase (composition maps)

**What FAILS:**
- SHOULD guardrails are L2 (ignored ~20%)
- No scaffold-on-entry (agent can skip docs)
- No mechanical gates (self-declared completion)

**Conclusion:** Channeling works at L2 but needs L4 automation for reliability.

#### H2: Scaffold-on-Entry vs Exit-Criteria - CONFIRMED

**Evidence from Session 101 cleanup:**
- 5 investigations with file status ≠ archive status (exit-criteria ignored)
- 2 work items implemented but not closed (exit-criteria ignored)
- 4 ghost IDs (spawned items never created)

**Why scaffold-on-entry wins:**
- Exit-criteria: Checks AFTER the fact, can be skipped
- Scaffold-on-entry: Creates structure that channels, skipping impossible

#### H3: Mechanical Blocking Reliability - PARTIALLY CONFIRMED

**What IS mechanical (L4):**
- Timestamp injection (PostToolUse)
- Cascade event logging (status: complete triggers)
- Status file refresh

**What is NOT mechanical (L2):**
- File sync (investigation ↔ archive)
- Exit criteria verification
- Phase completion gates

**Gap:** We have mechanical PROPAGATION but not mechanical BLOCKING.

#### Node-Cycle Mapping (Full Design)

**Expanded Node-Cycle Table:**

| Node | Cycle Skill | Scaffolded Docs | Entry Trigger | Exit Gate |
|------|-------------|-----------------|---------------|-----------|
| **BACKLOG** | none | `WORK-{id}.md` only | Work item created in backlog | Decision to proceed (manual) |
| **DISCOVERY** | `investigation-cycle` | `INVESTIGATION-{id}-*.md` | backlog category = investigation OR operator decision | Findings documented, spawns created, memory_refs populated |
| **DESIGN** | `adr-cycle` (NEW) | `ADR-{nnn}-*.md` | Investigation spawns ADR OR architecture decision needed | ADR status = accepted |
| **PLAN** | `plan-cycle` (NEW) | `PLAN-{id}-*.md` | Work item ready for implementation | Plan status = approved, tests defined |
| **IMPLEMENT** | `implementation-cycle` | Tests: `tests/test_{id}.py`, Code: varies, Verification: inline | Plan approved | Tests pass, demo complete, all checklist items done |
| **CLOSE** | `closure-cycle` (NEW) | Closure section in work file | Implementation verified | DoD verified, archived, memory stored |

**Scaffold-on-Entry Mechanism Design:**

```
TRIGGER: Work file frontmatter `current_node` changes
         OR `/enter-node {node}` command invoked

HOOK: PreToolUse on Edit to work file's current_node field
      OR PostToolUse after current_node update

SCAFFOLD ACTION:
    1. Read work file frontmatter → get new node
    2. Look up node-cycle binding → get cycle skill
    3. For each scaffolded doc type in cycle:
       a. Check if doc exists (Glob pattern)
       b. If not exists: Create via /new-{type} command
       c. Update work file cycle_docs field with paths
    4. Update work file: node_history append entry

EXAMPLE:
    current_node: backlog → plan

    PostToolUse detects change:
    → Glob("docs/plans/PLAN-{id}-*.md") → not found
    → Execute: /new-plan {id} "{title}"
    → Update work file:
        cycle_docs:
          plan: docs/plans/PLAN-{id}-{title}.md
        node_history:
          - node: plan
            entered: 2025-12-22T23:15:00
            exited: null
```

**Node Exit Gate Design:**

```
TRIGGER: Agent attempts to change current_node
         OR Agent invokes `/close` or `/exit-node`

GATE CHECK (PreToolUse):
    1. Read current_node from work file
    2. Look up exit criteria for that node's cycle
    3. For each criterion:
       a. Verify condition met (read files, check frontmatter)
       b. If ANY criterion fails: BLOCK with message
    4. If all pass: ALLOW transition

EXIT CRITERIA BY NODE:

DISCOVERY Exit:
    - [ ] Investigation status = complete
    - [ ] Findings section has content (not placeholder)
    - [ ] Spawned items exist (not "None yet")
    - [ ] memory_refs populated

PLAN Exit:
    - [ ] Plan status = approved
    - [ ] Tests First section has actual tests
    - [ ] Detailed Design section filled

IMPLEMENT Exit:
    - [ ] All tests pass (`pytest` exit code 0)
    - [ ] Demo completed (manual verification)
    - [ ] Ground Truth Verification table all checked

CLOSE Exit:
    - [ ] DoD criteria met (ADR-033)
    - [ ] Memory stored (ingester_ingest called)
    - [ ] Work file status = complete
```

**Node-Cycle Binding Configuration:**

```yaml
# Proposed: .claude/config/node-cycle-bindings.yaml
nodes:
  backlog:
    cycle: null
    scaffold: []
    exit_criteria: []  # Manual decision

  discovery:
    cycle: investigation-cycle
    scaffold:
      - type: investigation
        command: "/new-investigation {id} \"{title}\""
        pattern: "docs/investigations/INVESTIGATION-{id}-*.md"
    exit_criteria:
      - field: status
        value: complete
        source: investigation_file
      - section: "## Findings"
        not_contains: "[Document findings here"
      - section: "## Spawned Work Items"
        not_contains: "None yet"

  plan:
    cycle: plan-cycle
    scaffold:
      - type: plan
        command: "/new-plan {id} \"{title}\""
        pattern: "docs/plans/PLAN-{id}-*.md"
    exit_criteria:
      - field: status
        value: approved
        source: plan_file
      - section: "## Tests First"
        min_length: 100

  implement:
    cycle: implementation-cycle
    scaffold:
      - type: test
        command: "touch tests/test_{id}.py"
        pattern: "tests/test_{id}*.py"
    exit_criteria:
      - command: "pytest tests/test_{id}*.py"
        exit_code: 0
      - section: "## Ground Truth Verification"
        all_checked: true

  close:
    cycle: closure-cycle
    scaffold: []  # Inline in work file
    exit_criteria:
      - dod_verified: true
      - memory_stored: true
```

#### Work File Schema v2 (Designed)

**Full Schema (absorbing INV-024):**

```yaml
---
template: work_item
id: E2-150
title: "Work Item Title"
status: active | blocked | complete | archived

# Ownership
owner: Hephaestus
created: 2025-12-22
closed: null

# Classification
milestone: M4-Research
priority: high | medium | low
effort: low | medium | high
category: implementation | investigation | adr | maintenance

# DAG Edges (from E2-076b)
spawned_by: Session-101
spawned_by_investigation: INV-022
blocked_by: []
blocks: []
enables: []
related: []

# NODE-CYCLE STATE (NEW)
current_node: implement  # BACKLOG | DISCOVERY | DESIGN | PLAN | IMPLEMENT | CLOSE
node_history:
  - node: backlog
    entered: 2025-12-22T10:00:00
    exited: 2025-12-22T10:30:00
  - node: plan
    entered: 2025-12-22T10:30:00
    exited: 2025-12-22T11:00:00
  - node: implement
    entered: 2025-12-22T11:00:00
    exited: null  # currently here

# Cycle docs for current node
cycle_docs:
  plan: docs/plans/PLAN-E2-150-*.md
  tests: tests/test_e2_150.py
  verification: inline

# Context accumulation
memory_refs: [77119, 77120, 77121]
documents:
  investigations: []
  adrs: []
  plans: [PLAN-E2-150-*.md]
  checkpoints: [SESSION-101]
---
```

**Directory Structure:**
```
docs/work/
├── active/      # status: active
├── blocked/     # status: blocked
└── archive/     # status: complete | archived
```

**Design Rationale:**

| Field | Purpose | Solves |
|-------|---------|--------|
| `current_node` | Tracks DAG position | Scattered context |
| `node_history` | Audit trail of flow | Session discontinuity |
| `cycle_docs` | References scaffolded docs | Finding related files |
| Directory by status | Files move on transition | Visual status grouping |

---

### Session 98 Recon Findings

#### Prior Work State

| Document | Status | Key Insight |
|----------|--------|-------------|
| INV-011 | Phase 1 done | Work-item-as-file FEASIBLE, schema drafted |
| INV-012 | Vision captured | Commands = transitions, Skills = states with exits |
| E2-076 | Plan complete | DAG structure exists, cascades work |
| E2-111 | COMPLETE | investigation-cycle skill created |
| implementation-cycle | COMPLETE | Skill guides PLAN-DO-CHECK-DONE |

#### The Missing Bridge

Current state:
```
Work Item (backlog.md entry)
    → triggers Plan creation (manual)
    → Plan guides implementation-cycle (via skill)
    → Cycle has exit criteria (prompt-based)
```

Proposed state:
```
Work File (WORK-E2-xxx.md)
    → enters NODE (e.g., IMPLEMENT)
    → NODE scaffolds ALL cycle docs (automatic)
    → Agent works within cycle (channeled)
    → Cycle completion GATES node exit (mechanical)
    → Work File moves to next node
```

#### Template Channeling Pattern

Why templates work:
1. **Structure is visible** - Empty sections are obvious omissions
2. **Agent fills blanks** - LLM energy channeled into productive paths
3. **Validation possible** - Can check if sections filled

Applied to cycles:
1. **All cycle docs scaffolded** - Missing phases are impossible
2. **Agent completes phases** - Energy channeled through phase sequence
3. **Completion gated** - Can't exit until all phases done

---

## Spawned Work Items

### Immediate (Fix L2→L3 Gaps Discovered)

These items address governance drift revealed during Session 101:

- [ ] **E2-140: Investigation Status Sync Hook**
  - PostToolUse on backlog-complete.md edit
  - Auto-update investigation file `status: complete`
  - Fixes: 5 investigations with file/archive status mismatch

- [ ] **E2-141: Backlog ID Uniqueness Gate**
  - PreToolUse on Write/Edit to governed files
  - Grep all files for `backlog_id: {new_id}`, block if duplicate
  - Fixes: INV-011 ID collision

- [ ] **E2-142: Investigation-Cycle Subagent Enforcement**
  - Change investigation-cycle skill from "RECOMMENDED" to "MUST invoke investigation-agent"
  - Add L3 gate in skill that blocks EXPLORE without subagent
  - Fixes: Agent bypassed subagent during this investigation

- [ ] **E2-143: Audit Recipe Suite**
  - `just audit-sync` - file status vs archive consistency
  - `just audit-gaps` - implementation evidence vs pending status
  - `just audit-stale` - investigations older than 10 sessions

- [x] **E2-144: Investigation Template Enhancement** - COMPLETE (Session 101)
  - Template enhanced from 125 → 340 lines
  - Added: Evidence Tables, Design Outputs, Ground Truth Verification
  - Added: Binary Verification questions, Session Progress Tracker
  - Added: MUST requirements with skip rationale
  - Follows oyster-nacre pattern: template forms core for agent output

### Architecture (Future Milestone)

- [ ] **ADR-039: Work-Cycle-DAG Unified Architecture**
  - Formalizes node-cycle mapping, work file schema, scaffold-on-entry
  - Requires operator approval before implementation

- [ ] **Mx-WorkCycle Milestone** (Epoch 3 scope)
  - E2-150: Work file template and type implementation
  - E2-151: Node-cycle binding configuration
  - E2-152: Scaffold-on-entry PreToolUse hook
  - E2-153: Node exit gate enforcement
  - E2-154: Work file spawning mechanism

---

## Expected Deliverables

- [x] Vision capture (this document)
- [x] Unified architecture design (Session 101)
- [x] Node-cycle mapping table (Session 101) - Full design with 6 nodes, triggers, gates
- [x] Work file schema v2 (Session 101) - Absorbing INV-024, with node_history tracking
- [x] Scaffold-on-entry mechanism design (Session 101) - Hook-based triggering
- [x] Node exit gate design (Session 101) - PreToolUse blocking with criteria
- [x] Node-cycle binding configuration (Session 101) - YAML schema for bindings
- [x] Integration design (Session 101) - Hooks, commands, status impacts
- [x] Memory storage (concepts 77243-77253)
- [ ] ADR-039 draft (when ready to implement)

---

## Key Concepts

### The Blood Cell Model (from INV-011)

```
Work File = Blood Cell
DAG Nodes = Organs
Cycles = Organ Function

Blood cell flows through circulatory system
    → Arrives at each organ
    → Organ activates (cycle runs)
    → Cell picks up/delivers cargo (context)
    → Moves to next organ
    → Completes circuit
```

### The Engine Piston Model (Operator)

```
Work File = Piston
DAG Nodes = Cylinder Positions
Cycles = Combustion Phases

Piston moves through engine cycle
    → Each position has defined phases (intake, compress, ignite, exhaust)
    → Cannot skip phases
    → Phase completion drives movement
    → Full cycle = work done
```

### Cycle as Channeling Container

```
NODE: IMPLEMENT
    │
    ├── [SCAFFOLD] implementation-cycle docs
    │   ├── Plan status section (PLAN phase)
    │   ├── Test file placeholder (DO phase - TDD)
    │   ├── Implementation file placeholder (DO phase)
    │   ├── Verification checklist (CHECK phase)
    │   └── Closure template (DONE phase)
    │
    ├── [CONSTRAIN] Agent works within these docs
    │   └── Can only edit cycle docs until complete
    │
    └── [GATE] All phases done → node exit allowed
```

---

## Future Milestone Scope

This investigation is scoped for **context capture only**. Implementation would be a future milestone (possibly Epoch 3 or M6+) that includes:

1. Work file type + tooling
2. Node-cycle binding configuration
3. Scaffold-on-entry hooks
4. Completion gate enforcement
5. Work file spawning mechanism
6. Integration with existing cycles

**Why Not Now:**
- E2-111 (investigation-cycle) just completed
- implementation-cycle still maturing
- Foundation must be solid before adding containment layer

---

## References

- **INV-011:** Work Item as File Architecture (blood cell metaphor, schema)
- **INV-012:** Workflow State Machine Architecture (command/skill exits)
- **E2-076:** DAG Governance Architecture (edges, cascades)
- **E2-076b:** Frontmatter Schema (spawned_by, blocked_by, etc.)
- **E2-076e:** Cascade Hooks (Python implementation)
- **E2-111:** Investigation Cycle Skill (three-phase cycle)
- **ADR-038:** M2-Governance Symphony Architecture
- **Memory:** Session 98 discussion, concepts TBD

---
