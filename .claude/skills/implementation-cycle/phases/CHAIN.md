---
phase: CHAIN
skill: implementation-cycle
---
# CHAIN Phase (Post-DONE)

**On Entry:**
```bash
just set-cycle implementation-cycle CHAIN {work_id}
```

**Goal:** Close work item and route to next work item.

**Actions:**
1. Close work item: `/close {backlog_id}`
2. Query next work: `just ready`
3. If items returned, read first work file to check `documents.plans`
4. Read work item `type` field from WORK.md
5. **Apply routing decision table** (see `routing-gate` skill):
   - If `next_work_id` is None → `await_operator`
   - If `type` == "investigation" OR ID starts with `INV-` → `invoke_investigation`
   - If `has_plan` is True → `invoke_implementation`
   - Else → `invoke_work_creation`
5. Execute the action:
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
```bash
just clear-cycle
```

**Tools:** /close, Bash(just ready), Read, Skill(routing-gate)
