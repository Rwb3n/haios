---
template: observations
work_id: WORK-043
captured_session: '271'
generated: '2026-02-01'
last_updated: '2026-02-01T15:30:36'
---
# Observations: WORK-043

## What surprised you?

The critique agent (A4) flagged a phase count mismatch: plan proposed 4 phases (EXPLORE, HYPOTHESIZE, VALIDATE, CONCLUDE) but activity_matrix.yaml only maps 3 investigation-cycle phases. This was actually a feature, not a bug - the plan correctly targets E2.4's EXPLORE-FIRST redesign (EPOCH.md Decision 5), while the current investigation-cycle skill (WORK-037) hasn't been updated yet. The critique agent correctly identified a gap but misinterpreted it as plan error vs intentional forward-looking design.

Line counts exceeded the 30-50 target (52-60 lines actual). The governed activities tables added essential clarity that justifies the overage. The target was always "soft" per plan guidance - focus on "minimal but complete" rather than strict line counts. REQ-TEMPLATE-002 says "~30-50 lines" not "exactly 30-50".

## What's missing?

**Template Loading Mechanism:** The critique agent (A1) correctly noted that scaffold.py's `load_template()` only supports flat names, not subdirectory templates like `investigation/EXPLORE`. Currently, these templates are guidance documents read by agents during phases, not scaffolded artifacts. However, if we want to scaffold from phase templates in the future, scaffold.py will need updates. This should be tracked for CH-004 TemplateRouter.

**activity_matrix.yaml VALIDATE phase mapping:** The phase_to_state section maps `investigation-cycle/HYPOTHESIZE`, `investigation-cycle/EXPLORE`, `investigation-cycle/CONCLUDE` but not `investigation-cycle/VALIDATE`. When WORK-037 adds the VALIDATE phase to investigation-cycle, it must also add the activity_matrix.yaml mapping.

## What should we remember?

**Contract Pattern is reusable:** The Input Contract / Governed Activities / Output Contract / Template structure works well. Each section serves a distinct purpose: prerequisites, governance, requirements, structure. This pattern should be applied to implementation-cycle templates (CH-002 ImplementationFracture).

**Phase templates are guidance, not scaffolding:** Unlike implementation_plan.md which gets scaffolded with placeholders, these phase templates are read-only references. The skill reads the template during each phase for guidance. This distinction matters for future template work.

**Critique agent needs context about future-facing design:** The critique flagged the 4-phase structure as a spec mismatch because it compared against current investigation-cycle. When designing for a future state (E2.4 EXPLORE-FIRST), the plan should explicitly note "targets E2.4 design, not current state" to help critique agents understand the intentional gap.

## What drift did you notice?

**Investigation-cycle vs E2.4 design:** The current investigation-cycle skill has 3 phases (HYPOTHESIZE → EXPLORE → CONCLUDE) but E2.4 EPOCH.md Decision 5 specifies 4 phases (EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE). The phase templates are built for the target design. WORK-037 needs to update the skill to match. This is intentional drift (design leads implementation) but should be resolved before epoch exit.
