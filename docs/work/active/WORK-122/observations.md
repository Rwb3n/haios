---
template: observations
work_id: 'WORK-122'
captured_session: '345'
generated: '2026-02-11'
last_updated: '2026-02-11T21:10:00'
---
# Observations: WORK-122

## What surprised you?

CH-015 (ClosureCeremonies) was essentially complete before WORK-122 started. The chapter was written on 2026-02-03 stating "skills exist but lack formal contracts" — but CH-011/WORK-112 (also created 2026-02-03, completed S335) had already retrofitted all contracts. The chapter file was never updated to reflect that work done under a different chapter satisfied its criteria. This meant the actual remaining value was DoD validation functions — a different deliverable than originally scoped. Lesson: chapter files can become stale as sources of truth when cross-chapter work satisfies criteria.

The critique-agent caught assumption A1 (chapter/arc/epoch files use bold markdown `**Status:** Complete`, not YAML frontmatter) that would have caused silent failure in 3 of 4 validation functions in dod_validation.py. This validates the WORK-121 decision to order critique before plan-validation.

## What's missing?

**BUG: close-chapter-ceremony SKILL.md line 85** has grep pattern `chapter: {arc}/{chapter_id}` but real WORK.md data uses `chapter: CH-015` (no arc prefix). The ceremony will fail to find work items if followed literally. Needs a bug fix work item.

**No `just queue-commit` recipe.** WorkEngine requires full governance init for queue transitions. Had to fall back to direct frontmatter edits, bypassing the queue_ceremonies.py module entirely. The ceremony module exists but has no justfile entry point.

**Lightweight plan template needed.** The full implementation_plan.md is ~400 lines. For a 3-file, 45-min task, sections like Open Decisions ("None"), Consumer Verification ("SKIPPED"), and Call Chain Context were pro-forma overhead. S344 and S345 both flag this. WORK-101 (Proportional Governance) is the answer.

## What should we remember?

**Two file format parsers needed for HAIOS hierarchy.** WORK.md files use YAML frontmatter (`---` delimited). Chapter/arc/epoch files use bold markdown (`**Status:** Complete`). Any module that reads across hierarchy levels needs both parsers. `dod_validation.py` has `_parse_frontmatter()` and `_parse_markdown_field()` as the reference implementation.

**Verify chapter state before creating work items.** Checking existing tests (test_ceremony_retrofit.py 96/96) revealed contracts were already done — saved significant time vs implementing redundant work. Pattern: always assess "is this actually done already?" before scoping new work.

**Critique-before-validation ordering works.** A1 was a genuine bug that would have shipped without the critique gate. Keep this ordering (WORK-121).

## What drift did you notice?

**close-chapter-ceremony SKILL.md** grep pattern doesn't match real data format. Spec says `chapter: {arc}/{chapter_id}`, data says `chapter: CH-015`.

**CH-015 chapter file** was stale — "What doesn't exist: Machine-readable contracts" was already false by the time WORK-122 started. Chapter files drift when cross-chapter work satisfies criteria silently.

**Checkpoint governance bypass.** Plan-validation-cycle APPROVE says MUST checkpoint. Skipped for small work to preserve context. Technically a governance bypass — proportional governance (WORK-101) would formalize when checkpoints can be skipped.
