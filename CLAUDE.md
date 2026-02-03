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
| Stop | ReasoningBank extraction |

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

---

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| critique-agent | opus | Assumption surfacing |
| investigation-agent | opus | EXPLORE phase |
| validation-agent | sonnet | CHECK phase |
| preflight-checker | haiku | **REQUIRED** - Plan readiness |
| schema-verifier | haiku | **REQUIRED** - SQL queries |
| test-runner | haiku | Test execution |

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
*Last Updated: 2026-02-03 | Version: Epoch 2.5 Design (Session 294)*
