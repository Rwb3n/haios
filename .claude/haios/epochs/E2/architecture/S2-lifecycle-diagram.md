# generated: 2025-12-30
# System Auto: last updated on: 2026-01-18T13:00:45
# Section 2: Lifecycle Architecture Diagram

Generated: 2025-12-30 (Session 150)
Purpose: Visual summary of lifecycle architecture from Sections 2A-2F

---

## 1. NODE-LEVEL DAG (Work Item Lifecycle)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WORK ITEM NODE DAG                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌───────────┐    ┌─────┐
│    │ BACKLOG  │───▶│ DISCOVERY │───▶│   PLAN   │───▶│ IMPLEMENT │───▶│CLOSE│
│    └──────────┘    └───────────┘    └──────────┘    └───────────┘    └─────┘
│         │               │                │                │              │
│         │               │                │                │              │
│         ▼               ▼                ▼                ▼              ▼
│    ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌───────────┐    ┌─────┐
│    │  work-   │    │investiga- │    │  plan-   │    │  implem-  │    │close│
│    │ creation │    │   tion-   │    │authoring-│    │ entation- │    │work-│
│    │  -cycle  │    │   cycle   │    │  cycle   │    │   cycle   │    │cycle│
│    └──────────┘    └───────────┘    └──────────┘    └───────────┘    └─────┘
│                                                                             │
│    Note: `design` node REMOVED (Session 150) - vestigial, no cycle          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. PHASE-LEVEL DAG (Within Each Cycle)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CYCLE PHASE PATTERNS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SEMANTIC STRUCTURE (all cycles follow):                                    │
│                                                                             │
│  ┌────────────┐   ┌───────────┐   ┌────────────┐   ┌───────────┐   ┌──────┐│
│  │PREPARATION │──▶│ EXECUTION │──▶│ VALIDATION │──▶│PERSISTENCE│──▶│CHAIN ││
│  └────────────┘   └───────────┘   └────────────┘   └───────────┘   └──────┘│
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SPECIFIC CYCLES:                                                           │
│                                                                             │
│  investigation:   HYPOTHESIZE ──▶ EXPLORE ──▶ CONCLUDE ──▶ CHAIN            │
│                                                                             │
│  implementation:  PLAN ──▶ DO ──▶ CHECK ──▶ DONE ──▶ CHAIN                  │
│                                                                             │
│  close-work:      VALIDATE ──▶ OBSERVE ──▶ ARCHIVE ──▶ MEMORY ──▶ CHAIN     │
│                                                                             │
│  work-creation:   VERIFY ──▶ POPULATE ──▶ READY ──▶ CHAIN                   │
│                                                                             │
│  plan-authoring:  ANALYZE ──▶ AUTHOR ──▶ VALIDATE ──▶ CHAIN                 │
│                                                                             │
│  checkpoint:      SCAFFOLD ──▶ FILL ──▶ VERIFY ──▶ CAPTURE ──▶ COMMIT       │
│                   (TERMINAL - no CHAIN)                                     │
│                                                                             │
│  obs-triage:      SCAN ──▶ TRIAGE ──▶ PROMOTE                               │
│                   (TERMINAL - no CHAIN)                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. CYCLE ORCHESTRATOR FLOW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CYCLE ORCHESTRATOR                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  execute_cycle(cycle_id, work_id)                                           │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────┐                                                    │
│  │ Load cycle_def from │                                                    │
│  │ cycle-definitions   │                                                    │
│  │      .yaml          │                                                    │
│  └──────────┬──────────┘                                                    │
│             │                                                               │
│             ▼                                                               │
│  ┌─────────────────────┐     ┌───────────────────────────────┐              │
│  │ current_phase !=    │ NO  │                               │              │
│  │     CHAIN?          │────▶│  check_gate('objective_       │              │
│  └──────────┬──────────┘     │       complete')              │              │
│             │ YES            └───────────────┬───────────────┘              │
│             ▼                                │                              │
│  ┌─────────────────────┐                     │                              │
│  │  execute_phase()    │                     ▼                              │
│  │  (exit gates,       │          ┌─────────────────────┐                   │
│  │   memory, skill)    │          │   Gate PASSED?      │                   │
│  └──────────┬──────────┘          └──────────┬──────────┘                   │
│             │                                │                              │
│             ▼                         YES    │    NO                        │
│  ┌─────────────────────┐              ┌──────┴──────┐                       │
│  │ phase_exit_criteria │              │             │                       │
│  │      met?           │              ▼             ▼                       │
│  └──────────┬──────────┘     ┌─────────────┐ ┌─────────────┐                │
│      YES    │    NO          │execute_chain│ │   BLOCKED   │                │
│       ┌─────┴─────┐          │  (routing)  │ │ "objective  │                │
│       │           │          └──────┬──────┘ │ not met"    │                │
│       ▼           ▼                 │        └─────────────┘                │
│  ┌─────────┐ ┌─────────┐            ▼                                       │
│  │ advance │ │ return  │     ┌─────────────────────────────┐                │
│  │to next  │ │"continue│     │     ROUTING GATE            │                │
│  │ phase   │ │working" │     ├─────────────────────────────┤                │
│  └────┬────┘ └─────────┘     │ INV-* ──▶ investigation     │                │
│       │                      │ has_plan ──▶ implementation │                │
│       └──────────────────┐   │ else ──▶ work-creation      │                │
│                          │   │ fallback ──▶ await_operator │                │
│                          │   └─────────────────────────────┘                │
│                          │                                                  │
│                    (loop back to phase check)                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. OBJECTIVE_COMPLETE GATE (Defense in Depth)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     OBJECTIVE_COMPLETE GATE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  check_gate('objective_complete', work_id)                                  │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    COMPOSITE GATE (all must pass)                    │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  1. deliverables_checked                                     │   │    │
│  │  │     ─────────────────────────────────────────────────────── │   │    │
│  │  │     Read WORK.md → Extract ## Deliverables                   │   │    │
│  │  │     Count unchecked: - [ ]                                   │   │    │
│  │  │     PASS if count == 0                                       │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                              │                                      │    │
│  │                              ▼                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  2. no_remaining_work                                        │   │    │
│  │  │     ─────────────────────────────────────────────────────── │   │    │
│  │  │     Glob docs/work/active/{id}/*.md                          │   │    │
│  │  │     For each: check for ## Remaining Work section            │   │    │
│  │  │     PASS if empty or contains only "None"                    │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                              │                                      │    │
│  │                              ▼                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  3. anti_pattern_check (subagent)                            │   │    │
│  │  │     ─────────────────────────────────────────────────────── │   │    │
│  │  │     Invoke anti-pattern-checker subagent                     │   │    │
│  │  │     Validates no ceremonial completion                       │   │    │
│  │  │     PASS if subagent returns passed=true                     │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                              │
│                              ▼                                              │
│                    ┌───────────────────┐                                    │
│                    │  ALL 3 PASSED?    │                                    │
│                    └─────────┬─────────┘                                    │
│                       YES    │    NO                                        │
│                        ┌─────┴─────┐                                        │
│                        ▼           ▼                                        │
│                   ┌────────┐  ┌─────────────────────────────┐               │
│                   │  PASS  │  │  BLOCK: "Cycle objective    │               │
│                   │        │  │  not met - review remaining │               │
│                   │        │  │  work"                      │               │
│                   └────────┘  └─────────────────────────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. STATE STORAGE (Work-Centric)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STATE OWNERSHIP                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SESSION (ephemeral)              WORK ITEM (durable)                       │
│  ──────────────────               ───────────────────                       │
│                                                                             │
│  ┌─────────────────┐              ┌─────────────────────────────────────┐   │
│  │ haios-events    │              │ docs/work/active/{id}/WORK.md       │   │
│  │   .jsonl        │              ├─────────────────────────────────────┤   │
│  │                 │              │ YAML Frontmatter:                   │   │
│  │ • session_start │              │   current_node: implement           │   │
│  │ • session_end   │              │   node_history:                     │   │
│  │ • (ceremony)    │              │     - node: backlog                 │   │
│  └─────────────────┘              │       entered: 2025-12-30T10:00:00  │   │
│          │                        │       exited: 2025-12-30T10:05:00   │   │
│          │                        │     - node: discovery               │   │
│          ▼                        │       entered: 2025-12-30T10:05:00  │   │
│  ┌─────────────────┐              │       exited: null  ◄── CRASH FLAG  │   │
│  │ Session crashes │              │   memory_refs: [80325, 80326]       │   │
│  │ → No data loss  │              │   cycle_docs: {}                    │   │
│  │ → Work continues│              └─────────────────────────────────────┘   │
│  │   from WORK.md  │                           │                            │
│  └─────────────────┘                           │                            │
│                                                ▼                            │
│                               ┌─────────────────────────────────────┐       │
│                               │ Single Writer: PostToolUse hook     │       │
│                               │ Only writer to node_history         │       │
│                               └─────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. WORK ITEM DIRECTORY (Self-Contained Universe)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WORK ITEM DIRECTORY STRUCTURE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  docs/work/active/{id}/                                                     │
│  ├── WORK.md              ◄── Source of truth (frontmatter + content)       │
│  ├── observations.md      ◄── Captured before close (OBSERVE phase)         │
│  ├── plans/                                                                 │
│  │   └── PLAN.md          ◄── Implementation plan                           │
│  ├── SECTION-*.md         ◄── Investigation artifacts                       │
│  └── *.md                 ◄── Other work artifacts                          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                           PORTALS                                    │    │
│  │  ─────────────────────────────────────────────────────────────────  │    │
│  │  Work items reference external docs via portals (not copies):       │    │
│  │                                                                     │    │
│  │  WORK.md:                                                           │    │
│  │    spawned_by: INV-052        ──▶ [[INV-052]] portal                │    │
│  │    blocked_by: [E2-230]       ──▶ [[E2-230]] portal                 │    │
│  │    documents:                                                       │    │
│  │      checkpoints: [S149, S150] ──▶ Checkpoint portals               │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         ARCHIVE FLOW                                 │    │
│  │  ─────────────────────────────────────────────────────────────────  │    │
│  │                                                                     │    │
│  │  docs/work/active/{id}/  ──(just close-work)──▶  docs/work/archive/ │    │
│  │                                     │               {id}/           │    │
│  │                                     │                               │    │
│  │                              ┌──────┴──────┐                        │    │
│  │                              │ Atomic:     │                        │    │
│  │                              │ • status→   │                        │    │
│  │                              │   complete  │                        │    │
│  │                              │ • closed→   │                        │    │
│  │                              │   date      │                        │    │
│  │                              │ • mv dir    │                        │    │
│  │                              └─────────────┘                        │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. CONFIG FILES (Extensibility Layer)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CONFIGURATION ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  .claude/haios/config/                                                      │
│  ├── cycle-definitions.yaml    ◄── Cycle phases, gates, memory, routing     │
│  ├── gates.yaml                ◄── Gate check definitions (incl objective_  │
│  │                                  complete)                               │
│  ├── hook-handlers.yaml        ◄── Handler dispatch config                  │
│  └── thresholds.yaml           ◄── Context %, stale days, observation count │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        EXECUTION LAYER                               │    │
│  │  ─────────────────────────────────────────────────────────────────  │    │
│  │                                                                     │    │
│  │  cycle-definitions.yaml                                             │    │
│  │         │                                                           │    │
│  │         ▼                                                           │    │
│  │  ┌─────────────────────┐                                            │    │
│  │  │  cycle_executor.py  │  ◄── Thin orchestrator                     │    │
│  │  │  (future impl)      │                                            │    │
│  │  └──────────┬──────────┘                                            │    │
│  │             │                                                       │    │
│  │             ▼                                                       │    │
│  │  ┌─────────────────────┐                                            │    │
│  │  │     SKILL.md        │  ◄── Phase-specific logic                  │    │
│  │  │  (guardrails, exit  │                                            │    │
│  │  │   criteria, tools)  │                                            │    │
│  │  └─────────────────────┘                                            │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Pattern: YAML defines WHAT, Code executes HOW                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. KEY DECISIONS SUMMARY

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SESSION 149-150 DECISIONS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ DECISION                          │ CHOICE                            │  │
│  ├───────────────────────────────────┼───────────────────────────────────┤  │
│  │ State ownership                   │ WORK.md, not session events       │  │
│  │ Crash recovery                    │ exited: null in node_history      │  │
│  │ Extensibility                     │ YAML config + thin executor       │  │
│  │ Single writer                     │ PostToolUse → node_history        │  │
│  │ `design` node                     │ REMOVED (vestigial)               │  │
│  │ Routing rules                     │ Embedded in ChainConfig           │  │
│  │ objective_complete                │ Composite: 3 checks               │  │
│  │ Cycle orchestrator                │ check objective before CHAIN      │  │
│  └───────────────────────────────────┴───────────────────────────────────┘  │
│                                                                             │
│  REMAINING WORK:                                                            │
│  ───────────────                                                            │
│  None - superseded by Epoch 2.2 config consolidation.                       │
│  See .claude/haios/config/ for current config architecture.                 │
│  See .claude/haios/modules/cycle_runner.py for cycle execution.             │
│                                                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*Diagram generated Session 150 - consolidates Sections 2A through 2F*
