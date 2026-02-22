---
phase: CHECK
skill: implementation-cycle
---
# CHECK Phase

**On Entry:**
```bash
just set-cycle implementation-cycle CHECK {work_id}
```

**Goal:** Verify implementation meets quality bar.

**Actions:**
1. Run test suite: `pytest tests/ -v`
2. Verify all tests pass (no regressions)
3. **DEMO the feature** - Exercise the new code path to surface bugs (Session 90)
4. Run plan's Ground Truth Verification
5. Check DoD criteria (ADR-033)
6. **MUST: Delegate deliverables verification to haiku subagent** (Session 192 - E2-290 Learning)
7. **If creating discoverable artifact:** Verify runtime discovery (see below)
8. **(Optional) Invoke validation-agent** for unbiased review: `Task(subagent_type='validation-agent')`

**MUST Gate: Deliverables Verification (Session 192 / WORK-178)**
Before declaring CHECK complete, delegate to haiku subagent:
```
Task(subagent_type='preflight-checker', model='haiku', prompt='Verify deliverables for {backlog_id}. Work item: docs/work/active/{backlog_id}/WORK.md. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. For EACH deliverable in the Deliverables section: confirm the work is done (file exists, content matches, grep confirms). For each plan Implementation Step: confirm it is complete. Report PASS (all done) or BLOCK (list incomplete items). If BLOCK: list each incomplete deliverable with reason.')
```

- **PASS:** All deliverables verified. Proceed to remaining CHECK steps.
- **BLOCK:** Incomplete deliverables reported. Return to DO phase, address gaps, then re-run CHECK.

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290 Session 192). Agent declared victory after tests passed but skipped 2 of 7 deliverables. Tests verify code works, deliverables verify scope is complete. Both are required.

> **Rationale (WORK-178):** Deliverables verification is structural (read file, scan checklist, report pass/fail) — no judgment required. Haiku model appropriate. Saves main-agent context for value-add work.

**Demo Step (Session 90 - TDD Gap Discovery):**
- Demo **MUST** exercise the happy path at minimum
- For hooks/commands: Run them and verify output
- For new functions: Call them with real data
- Document any bugs found during demo
- If bugs found: Fix and re-run CHECK phase

**For non-code tasks** (docs, ADRs, configs):
- Skip pytest if no code changes
- Focus on Ground Truth Verification (files exist, content correct)
- Use `/validate` command for template compliance
- Manual review replaces automated tests

**For discoverable artifacts** (skills, agents, commands):
- Run `just update-status-slim`
- Verify artifact appears in haios-status-slim.json
- File existence is NOT sufficient - must verify runtime discovery
- See INV-012 for anti-pattern details

**FORESIGHT Calibration (Optional - E2-106):**
Compare prediction to actual outcome, update foresight_prep in frontmatter:
```yaml
foresight_prep:
  # ... PLAN phase fields preserved ...
  actual_outcome: "What actually happened"
  prediction_error: 0.2  # How wrong was I? (0-1 scale)
  competence_estimate: 0.7  # How good am I at this domain now? (0-1)
  failure_modes_discovered: ["What I didn't anticipate"]
```
> This prepares data for Epoch 3 FORESIGHT layer. Enables UPDATE operation calibration.

**Exit Criteria:**
- [ ] All tests pass (or N/A for non-code)
- [ ] Ground Truth Verification complete
- [ ] No regressions in full test suite (or N/A)
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] **MUST:** All plan Implementation Steps checked off
- [ ] Discoverable artifacts appear in runtime status (or N/A)
- [ ] (Optional) foresight_prep calibration fields updated

**Tools:** Bash(pytest), Read, Task(test-runner), Task(validation-agent), Task(preflight-checker, model=haiku), /validate, just update-status
