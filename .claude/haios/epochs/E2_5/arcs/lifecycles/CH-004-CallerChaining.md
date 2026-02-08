# generated: 2026-02-03
# System Auto: last updated on: 2026-02-05T22:33:44
# Chapter: Caller Chaining

## Definition

**Chapter ID:** CH-004
**Arc:** lifecycles
**Status:** Complete
**Completed:** 2026-02-03 (Session 302)
**Implementation Type:** REFACTOR
**Depends:** CH-001, CH-002
**Work Items:** WORK-087

---

## Current State (Verified)

**Source:** `.claude/skills/close-work-cycle/SKILL.md` (lines 164-214)

CHAIN phase exists and prompts for next action, but uses routing logic:

```markdown
# From SKILL.md:191-200
6. **Apply routing decision table** (WORK-030: type field is authoritative):
   - If `next_work_id` is None → `await_operator`
   - If `type` == "investigation" → `invoke_investigation`
   - If `has_plan` is True → `invoke_implementation`
   - Else → `invoke_work_creation`
7. Execute the action:
   - `invoke_investigation` -> `Skill(skill="investigation-cycle")`
   - `invoke_implementation` -> `Skill(skill="implementation-cycle")`
   ...
```

**What exists:**
- CHAIN phase prompts and routes based on work type
- `await_operator` path exists (no auto-spawn)
- Routing decision table in skill markdown

**What doesn't exist:**
- `CycleRunner.chain()` explicit method
- Return of typed output to caller
- True "caller decides" pattern (skill decides via routing table)

**Caller identity:** The "caller" is Claude interpreting the skill markdown. No programmatic caller in current design.

---

## Problem

CHAIN phase has routing logic embedded in skill, not returned to caller. The skill decides next action based on work type, not the operator/caller.

Gap to address:
- Skill-embedded routing vs caller-controlled routing
- Need explicit `spawn_next=None` acceptance (currently implicit via `await_operator`)

---

## Agent Need

> "I need lifecycle completion to return control to me so I can decide whether to chain to next lifecycle, store the output, or do something else entirely."

---

## Requirements

### R1: Caller Decides Next Action (REQ-LIFECYCLE-004)

Lifecycle completion returns output to caller. Caller decides:
1. Pipe output to next lifecycle
2. Store output and stop
3. Discard output (rare but valid)

```python
# Lifecycle returns, caller chains
spec = cycle_runner.run(work_id, lifecycle="design")
# Decision point: operator/agent decides
if should_implement:
    artifact = cycle_runner.run(work_id, lifecycle="implementation", input=spec)
else:
    store_spec(spec)  # Design-only workflow
```

### R2: No Auto-Spawn

close-work-cycle must NOT auto-spawn next lifecycle. Prompt "spawn next?" but don't execute without explicit choice.

### R3: Explicit Chaining via Asset.pipe() (Deferred to CH-025)

When chaining is desired, use asset piping (see CH-025):

```python
# Explicit chaining via asset.pipe()
spec = cycle_runner.run(work_id, lifecycle="design")
artifact = spec.pipe("implementation")  # Asset owns piping
```

**NOTE:** `cycle_runner.chain()` was removed in favor of `asset.pipe()` per CH-025 decision. Assets carry data; chaining is about data flow.

---

## Interface

### CycleRunner Changes

```python
def run(work_id: str, lifecycle: str, input: Any = None) -> LifecycleOutput:
    """Run lifecycle, return output. NO auto-chain."""

def chain(work_id: str, from_lifecycle: str, to_lifecycle: str) -> LifecycleOutput:
    """Explicit chain: get output of from_lifecycle, pipe to to_lifecycle."""
```

### close-work-cycle Changes

Remove auto-spawn logic. Instead:

```
Work complete. Options:
1. Store output (no spawn)
2. Chain to {next_lifecycle}
3. Spawn new work item

Choice: _
```

### Spawn Ceremony

Spawning next work is a ceremony (Arc 3: Ceremonies), not lifecycle behavior.

---

## Success Criteria

- [ ] CycleRunner.run() returns without auto-chaining
- [ ] close-work-cycle prompts for next action, doesn't auto-spawn
- [ ] Explicit CycleRunner.chain() method for desired chaining
- [ ] "Complete without spawn" is valid and doesn't warn
- [ ] Unit tests: design completes → no implementation started
- [ ] Integration test: Design → prompt → choose "store only" → verify no spawn

---

## Non-Goals

- Removing ability to chain (chaining is still supported, just explicit)
- Automatic workflow orchestration (that's operator responsibility)
- Defining spawn ceremony details (see Arc 3)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-004)
- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-017-SpawnCeremony.md (spawn ceremony)
