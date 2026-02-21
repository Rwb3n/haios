# generated: 2025-09-23
# System Auto: last updated on: 2026-02-03T00:06:06
# Code Implementation & Engineering Guide

## Quick Links

| What | Where |
|------|-------|
| **Requirements** | `.claude/haios/manifesto/L4/functional_requirements.md` |
| **Architecture** | `.claude/haios/manifesto/L4/technical_requirements.md` |
| **Current Epoch** | `.claude/haios/epochs/E2_4/EPOCH.md` |
| **Config** | `.claude/haios/config/haios.yaml` |
| **Entry Point Tiers** | `docs/ADR/ADR-045-three-tier-entry-point-architecture.md` |

---

## CRITICAL Rules (MUST)

### 1. Module-First Principle
Commands/Skills → `cli.py` / `just` → modules → lib. **Never** instruct agents to read files manually.

### 2. Path Constants via ConfigLoader
```python
from config import ConfigLoader
config = ConfigLoader.get()
path = config.get_path("work_item", id="WORK-080")
```
**Never** hardcode paths.

### 3. Work Item ID Policy
Format: `WORK-XXX`. Type field determines routing, not ID prefix.

### 4. Memory Refs Rule
When reading documents with `memory_refs` in frontmatter, **MUST** query those IDs.

### 5. SQL Queries
**BLOCKED.** Use `schema-verifier` subagent.

### 6. Traceability Chain
```
L4 Requirement → Epoch → Arc → Chapter → Work Item
```
No chapter file → work item BLOCKED.

---

## Lifecycles (E2.5 - Session 294)

Lifecycles are pure functions, independently completable:

| Lifecycle | Signature | Phases |
|-----------|-----------|--------|
| Investigation | `Question → Findings` | EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE |
| Design | `Requirements → Specification` | EXPLORE → SPECIFY → CRITIQUE → COMPLETE |
| Implementation | `Specification → Artifact` | PLAN → DO → CHECK → DONE |
| Validation | `Artifact × Spec → Verdict` | VERIFY → JUDGE → REPORT |
| Triage | `[Items] → [PrioritizedItems]` | SCAN → ASSESS → RANK → COMMIT |

**Chaining is caller choice.** Lifecycles can complete without spawning next.

See `L4/functional_requirements.md` for full details (REQ-LIFECYCLE-*).

---

## Queue (Orthogonal to Lifecycle)

```
backlog → ready → active → done
```

Queue position is separate from lifecycle phase. Work item can be `queue: done` without spawning.

See `L4/functional_requirements.md` (REQ-QUEUE-*).

---

## Ceremonies

Side-effect boundaries. See `L4/functional_requirements.md` (REQ-CEREMONY-*).

| Category | Ceremonies |
|----------|------------|
| Queue | Intake, Prioritize, Commit, Release |
| Session | Start, End, Checkpoint |
| Closure | Close Work/Chapter/Arc/Epoch |
| Feedback | Chapter/Arc/Epoch/Requirements Review |
| Memory | Observation Capture, Triage, Memory Commit |

---

## Governance Quick Reference

### Hooks
| Hook | Purpose |
|------|---------|
| PreToolUse | Governance enforcement, state injection |
| PostToolUse | Timestamps, cascade triggers |
| UserPromptSubmit | Date/time, vitals |
| Stop | ReasoningBank extraction + session-end actions (WORK-161) |

### Commands
| Command | Purpose |
|---------|---------|
| `/coldstart` | Initialize session |
| `/new-checkpoint` | Create checkpoint |
| `/new-work` | Create work item |
| `/new-investigation` | Create investigation |
| `/new-plan` | Create plan |
| `/close` | Close work item |
| `/implement` | Start implementation |

### Governance Triggers (MUST)
- Discover bug/gap → `/new-investigation`
- SQL query → `schema-verifier` subagent
- Close work → `/close <id>`
- Create governed doc → `/new-*` command
- Proportional governance (L3.20): effort=small items MAY use lightweight phases per REQ-LIFECYCLE-005. Tiers: Trivial (none) → Small (checklist) → Standard (full) → Architectural (operator). See `L4/functional_requirements.md` for threshold predicates.

---

## Agents

| Agent | Model | Requirement | Category | Purpose |
|-------|-------|-------------|----------|---------|
| critique-agent | opus | recommended | verification | Assumption surfacing |
| investigation-agent | opus | **required** | utility | EXPLORE phase |
| validation-agent | sonnet | recommended | verification | CHECK phase |
| preflight-checker | haiku | **required** | gate | Plan readiness |
| schema-verifier | haiku | **required** | gate | SQL queries |
| test-runner | haiku | optional | utility | Test execution |
| anti-pattern-checker | sonnet | recommended | verification | L1 claim verification |
| why-capturer | haiku | recommended | utility | Learning extraction |
| implementation-cycle-agent | sonnet | optional | cycle-delegation | Full impl cycle delegation |
| investigation-cycle-agent | sonnet | optional | cycle-delegation | Full investigation delegation |
| close-work-cycle-agent | sonnet | optional | cycle-delegation | Full close cycle delegation |
| plan-authoring-agent | sonnet | optional | cycle-delegation | Plan authoring in isolated context |
| design-review-validation-agent | sonnet | optional | verification | DO phase exit gate (design alignment) |

---

## Work Item Completion (ADR-033)

| Criterion | Verify |
|-----------|--------|
| Tests pass | `pytest` - all green |
| Runtime consumer exists | Grep for imports outside tests |
| WHY captured | `ingester_ingest` |
| Docs current | CLAUDE.md, READMEs updated |

---

## Session Hygiene

1. `/coldstart` at session start
2. Checkpoint before compact
3. Store learnings to memory

---

*For full requirements, see `.claude/haios/manifesto/L4/`*
*Last Updated: 2026-02-18 | Version: Epoch 2.8 Agent UX (Session 398)*
