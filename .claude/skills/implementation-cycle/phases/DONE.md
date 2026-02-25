---
phase: DONE
skill: implementation-cycle
---
# DONE Phase

**On Entry:**
```bash
just set-cycle implementation-cycle DONE {work_id}
```

**Goal:** Complete implementation and prepare for closure.

**Actions:**
1. Capture WHY: Store learnings to memory
2. Update plan status: `status: complete`
3. Update documentation if behavior changed — **delegate to haiku subagent** (S436 / Memory 88078):
   - Before delegating: enumerate the specific behavioral changes made in this session (e.g., "Added Task(test-runner, model=haiku) delegation to DO.md TDD section"). Substitute into the prompt below.
   ```
   Task(subagent_type='Bash', model='haiku', prompt='Update CLAUDE.md and relevant READMEs to reflect changes from {backlog_id}. Specific changes: [enumerate changes from this session]. Verify grep confirms updates.')
   ```
4. **Delegate git commit to haiku subagent** (S436 / Memory 88078):
   ```
   Task(subagent_type='Bash', model='haiku', prompt='Stage and commit all changes for {backlog_id}. Command: git add -A && git commit -m "Session {session}: {backlog_id} {title}". Report exit code and commit hash.')
   ```

**Exit Criteria:**
- [ ] WHY captured (memory_refs in checkpoint)
- [ ] Plan marked complete
- [ ] Docs updated (CLAUDE.md, READMEs) — delegated to haiku subagent
- [ ] Git commit executed — delegated to haiku subagent

**Tools:** ingester_ingest, Edit, Task(Bash, model=haiku)
