---
template: observations
work_id: WORK-085
captured_session: '302'
generated: '2026-02-03'
last_updated: '2026-02-03T22:24:30'
---
# Observations: WORK-085

## What surprised you?

The implementation was simpler than anticipated. The plan predicted ~50 minutes, and it took approximately that. The surprise was how cleanly the PAUSE_PHASES constant maps to the existing CYCLE_PHASES pattern - adding it was truly additive with no refactoring required.

The critique-agent identified A7 (consumer integration) as blocking, but upon analysis, close-work-cycle is a markdown skill, not Python code. The "consumer" is the agent reading the skill guidance, not a code-to-code call. This revealed an assumption gap in how we think about skill-to-module integration: skills don't "call" Python methods directly, they guide agent behavior which then uses Python modules.

## What's missing?

**Runtime integration with close-work-cycle:** While `is_at_pause_point()` exists and works (work_engine.py:356), there's no `just` recipe or skill guidance that explicitly calls it. The close-work-cycle skill could be enhanced to say "query WorkEngine.is_at_pause_point() before accepting closure at pause." This is future work, not blocking.

**Validation lifecycle phases:** CYCLE_PHASES doesn't define a validation-cycle, yet PAUSE_PHASES includes validation lifecycle with pause phase REPORT. This is correct (PAUSE_PHASES is keyed by lifecycle name, not cycle name), but the asymmetry could confuse future developers. Consider documenting this distinction.

## What should we remember?

**Pattern: Lifecycle vs Cycle naming distinction.** Lifecycles (investigation, design, implementation, validation, triage) are abstract workflows defined in L4 functional_requirements.md. Cycles (implementation-cycle, investigation-cycle) are skill implementations in .claude/skills/. PAUSE_PHASES uses lifecycle names; CYCLE_PHASES uses cycle names. This distinction matters for any future work touching phase definitions.

**Pattern: Type-to-lifecycle mapping.** Work items have a `type` field (feature, investigation, bug, chore, spike) from the work_item template. Lifecycles have different names (implementation, investigation, etc.). The `type_to_lifecycle` mapping in `is_at_pause_point()` (work_engine.py:380-390) bridges this gap. If new work types are added to the template, this mapping needs updating.

## What drift did you notice?

**CYCLE_PHASES vs L4 functional_requirements.md:** The investigation-cycle phases in CYCLE_PHASES (cycle_runner.py:135) are `["HYPOTHESIZE", "EXPLORE", "CONCLUDE", "CHAIN"]` but L4 REQ-FLOW-002 says `EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE`. The order differs (HYPOTHESIZE before EXPLORE in code) and VALIDATE phase is missing from code. This is existing drift pre-dating WORK-085, not caused by this work.

**observation-triage-cycle vs L4 Triage lifecycle:** CYCLE_PHASES (cycle_runner.py:140) has `["SCAN", "TRIAGE", "PROMOTE"]` but L4 defines Triage lifecycle phases as `SCAN → ASSESS → RANK → COMMIT` (functional_requirements.md). Different phase names. PAUSE_PHASES uses L4-authoritative name (COMMIT), not the cycle's terminal phase name (PROMOTE). This drift should be addressed in a future work item to align CYCLE_PHASES with L4.
