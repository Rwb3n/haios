---
template: observations
work_id: WORK-087
captured_session: '303'
generated: '2026-02-03'
last_updated: '2026-02-03T23:06:46'
---
# Observations: WORK-087

## What surprised you?

The scope was narrower than initially anticipated. The plan called for potentially modifying CycleRunner.run() but it was already complete from WORK-084. The actual work was purely skill markdown refactoring - no Python code changes needed. This made TDD unusual: tests verify markdown content patterns rather than runtime behavior. The test fixture extraction logic needed adjustment because the CHAIN phase header includes "(Post-MEMORY)" suffix that wasn't in the test patterns.

## What's missing?

**README drift:** The critique-agent surfaced that `.claude/skills/close-work-cycle/README.md` shows phases as "VALIDATE-ARCHIVE-CAPTURE" but SKILL.md has "VALIDATE-ARCHIVE-MEMORY-CHAIN". This pre-existing drift should be addressed. The README.md was not updated in this work because fixing pre-existing drift is out of scope, but it's now documented.

**Skill content tests pattern:** There's no standard pattern for testing skill markdown content. I created `extract_section()` helper but this could be a shared utility for other skill tests.

## What should we remember?

**Skills are instruction documents, not executable code.** Testing skill changes means verifying the markdown content has the right patterns (AskUserQuestion, choice language, etc.) that Claude will interpret correctly. This is fundamentally different from testing Python modules where you invoke functions.

**"Caller choice" in skills means AskUserQuestion.** The implementation of REQ-LIFECYCLE-004 for skills is to use AskUserQuestion tool to present options rather than auto-invoking Skill() calls. The routing logic still determines *suggestions* but execution requires explicit user selection.

## What drift did you notice?

**README.md vs SKILL.md phases:** close-work-cycle README.md line 16-18 shows "VALIDATE-ARCHIVE-CAPTURE" but SKILL.md has four phases: VALIDATE, ARCHIVE, MEMORY, CHAIN. This is pre-existing drift, not caused by this work.

**Carried forward from Session 302:** CYCLE_PHASES in cycle_runner.py has investigation-cycle phases in order "HYPOTHESIZE, EXPLORE, CONCLUDE, CHAIN" but L4 REQ-FLOW-002 may expect different ordering. Also observation-triage-cycle phases don't match L4 Triage lifecycle phases.
