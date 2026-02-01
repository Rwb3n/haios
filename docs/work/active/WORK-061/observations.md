---
template: observations
work_id: WORK-061
captured_session: '272'
generated: '2026-02-01'
last_updated: '2026-02-01T16:08:27'
---
# Observations: WORK-061

## What surprised you?

**The fractured templates already existed.** WORK-043 (Session 271) had already created the `.claude/templates/investigation/` directory with all four phase templates (EXPLORE.md, HYPOTHESIZE.md, VALIDATE.md, CONCLUDE.md). The plan indicated these were deliverables, but they were pre-created by a parallel work item in the same session. This reduced implementation effort from ~1 hour to ~30 minutes. The work item spawning from WORK-037 was well-coordinated - the prior session anticipated the implementation needs.

**The skill description auto-updates.** When I wrote the new SKILL.md file, the system automatically updated the skill description in the registry (visible in the system-reminder listing). This is invisible infrastructure that "just works" - the skill discovery mechanism reads frontmatter at runtime. No manual registration needed.

## What's missing?

**No automated test for skill flow changes.** Skills are markdown, so there's no pytest coverage for their structure. A future enhancement could be a skill-linting tool that validates: (1) phase names match activity_matrix.yaml mappings, (2) "On Entry" bash commands reference valid just recipes, (3) exit criteria checklists are well-formed. Currently skill correctness is manual review only.

**No migration tooling for in-flight investigations.** The critique (Session 272) noted that the "grandfather clause" for in-flight investigations is documentation-only. If an investigation is mid-HYPOTHESIZE when the skill updates, there's no detection mechanism or guidance. This was accepted as low risk due to the atomic nature of skill updates, but worth noting for systems with more concurrent work.

## What should we remember?

**EXPLORE-FIRST rationale:** Session 262 demonstrated that unconstrained exploration (via built-in Explore agent) produced deeper analysis than the template-constrained investigation-cycle. The HYPOTHESIZE-first pattern forced premature closure - agents had to commit to hypotheses before seeing evidence. The inversion (EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE) lets hypotheses form FROM evidence rather than constraining what evidence is gathered. This is a significant L4 decision (Session 265) that inverts 100+ sessions of prior practice.

**Consumer verification catches drift.** After implementing the skill rewrite, the plan's "Consumer Verification" step (Step 5) prompted a grep for old flow references. This found two README files (`investigation-cycle/README.md` and `skills/README.md`) still showing HYPOTHESIZE-EXPLORE-CONCLUDE. Without this step, the skill would have updated but documentation would have drifted. Include consumer verification in future skill refactors.

## What drift did you notice?

**Checkpoint drift flag predicted the change.** The prior session (271) checkpoint flagged "investigation-cycle skill line 89 MUST invoke investigation-agent will be invalid after WORK-061" in drift_observed. This was accurate - WORK-061 removed that MUST requirement (investigation-agent invocation is now optional in EXPLORE phase). The drift flagging system correctly predicted the work needed.

**Flow arc CH-003 status needs update.** The flow arc ARC.md (`.claude/haios/epochs/E2_4/arcs/flow/ARC.md`) lists CH-003 (InvestigationFlow) as "Planned". WORK-061 implements this chapter's functionality. The arc status should be updated to reflect completion. This is minor housekeeping, not architectural drift.
