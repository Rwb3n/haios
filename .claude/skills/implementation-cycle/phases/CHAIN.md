---
phase: CHAIN
skill: implementation-cycle
---
# CHAIN Phase (Post-DONE)

**On Entry:**
```
mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="CHAIN", work_id="{work_id}")
```

**Goal:** Close work item and route to next work item.

**Actions:**
1. Close work item: `/close {backlog_id}`
2. **Delegate git commit to haiku subagent** (S436 / Memory 88078):
   ```
   Task(subagent_type='Bash', model='haiku', prompt='Stage and commit all changes for {backlog_id}. Command: git add -A && git commit -m "Session {session}: {backlog_id} {title}". Report exit code and commit hash.')
   ```
3. Query next work: `mcp__haios-operations__queue_ready()`
4. If items returned, read first work file to check `documents.plans`
5. Read work item `type` field from WORK.md
6. **Apply routing decision table** (see `routing-gate` skill):
   - If `next_work_id` is None → `await_operator`
   - If `type` == "investigation" OR ID starts with `INV-` → `invoke_investigation`
   - If `has_plan` is True → `invoke_implementation`
   - Else → `invoke_work_creation`
7. Execute the action:
   - `invoke_investigation` -> `Skill(skill="investigation-cycle")`
   - `invoke_implementation` -> `Skill(skill="implementation-cycle")`
   - `invoke_work_creation` -> `Skill(skill="work-creation-cycle")`
   - `await_operator` -> Report "No unblocked work. Awaiting operator direction."

**MUST:** Do not pause for acknowledgment - execute routing immediately.

**Exit Criteria:**
- [ ] Work item closed via /close
- [ ] Next work item identified (or none available)
- [ ] Appropriate cycle skill invoked (or awaiting operator)

**On Complete:**
```
mcp__haios-operations__cycle_clear()
```

**Tools:** /close, Task(Bash, model=haiku), mcp__haios-operations__queue_ready, Read, Skill(routing-gate)
