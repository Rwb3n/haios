# generated: 2026-01-30
# System Auto: last updated on: 2026-02-01T16:55:45
# Arc: Activities

## Arc Definition

**Arc ID:** activities
**Epoch:** E2.4 (The Activity Layer)
**Name:** Governed Activities
**Status:** Planned
**Pressure:** [volumous] - thematic exploration

---

## Theme

Define and implement governed activities per state.

**Core Pattern:**
```
Governed Activity = Primitive × State × Governance Rules
```

---

## Chapters

| Chapter | Name | Status | Purpose |
|---------|------|--------|---------|
| CH-001 | ActivityMatrix | Planned | Define full matrix of primitives × states × rules |
| CH-002 | StateDefinitions | Planned | Formalize EXPLORE, DESIGN, PLAN, DO, CHECK, DONE states |
| CH-003 | GovernanceRules | Planned | Implement rules per governed activity |
| CH-004 | PreToolUseIntegration | Planned | Wire governed activities to PreToolUse hook |

---

## Key Governed Activities (from Session 265)

| State | Blocked | Allowed |
|-------|---------|---------|
| EXPLORE | (none) | explore-read, explore-search, explore-memory, capture-notes |
| DESIGN | (none) | requirements-read, spec-write, critique-invoke |
| PLAN | (none) | scope-read, plan-write, critique-invoke |
| DO | AskUser, explore-*, spec-write | spec-read, artifact-write, artifact-edit, build-execute, **task-track** |
| CHECK | (none) | verify-read, test-execute, verdict-write |

### DO State: CC Task Integration (WORK-059, Session 274)

**Finding:** Agent SHOULD use CC Task System for DO phase micro-tracking.

| Activity | Tool | Purpose |
|----------|------|---------|
| `task-track` | TaskCreate, TaskUpdate | Break down implementation into sub-tasks |

**Rationale:**
- CC Tasks are ephemeral (no disk pollution)
- `activeForm` provides spinner UX for operator visibility
- Dependencies (blockedBy) track sub-task ordering
- Auto-cleanup at session end

**Level:** L2 (RECOMMENDED) - Agent discretion based on task complexity.

**Memory Refs:** 82904-82914

---

## Exit Criteria

- [ ] Activity matrix documented
- [ ] States formally defined
- [ ] Governance rules implemented
- [ ] PreToolUse enforces state-based restrictions

---

## Memory Refs

Session 265 governed activities decision: 82706-82710

---

## References

- @.claude/haios/epochs/E2_4/EPOCH.md
- @.claude/haios/epochs/E2/architecture/S20-pressure-dynamics.md
