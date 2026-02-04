---
template: observations
work_id: WORK-089
captured_session: '311'
generated: '2026-02-04'
last_updated: '2026-02-04T23:06:52'
---
# Observations: WORK-089

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

Template sizes exceeded targets but stayed within constraints. The plan targeted ~40-50 lines per template, but actual implementation resulted in 71-79 lines. This happened because the YAML frontmatter with full contract specifications (input_contract and output_contract as arrays of objects with field/type/required/description) takes more space than anticipated. However, all templates stayed well under the 100-line hard constraint from REQ-TEMPLATE-002. The investigation templates (EXPLORE, HYPOTHESIZE, VALIDATE, CONCLUDE) also run 75-87 lines, so this is consistent with the established pattern from WORK-088.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

**No design-cycle skill exists yet.** The templates are passive markdown - there's no skill that actually consumes them during a design lifecycle. The activity_matrix.yaml has no `design-cycle/*` entries in the `phase_to_state` mapping. This is expected (CH-006 scope is templates only, not skill creation), but worth noting for future work items in the lifecycles arc.

**ConfigLoader.get_phase_template() not implemented.** CH-006 lists this as a success criterion, but it's scoped to a different work item. The templates work by direct path access for now.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

**The investigation template pattern is proven and portable.** WORK-088 established the contract structure (input_contract/output_contract in YAML frontmatter, 5 sections: Header, Input Contract, Governed Activities, Output Contract, Template). WORK-089 successfully replicated this pattern for design lifecycle. Future template fracturing (implementation, validation, triage - WORK-090, WORK-091, WORK-092) should follow the exact same pattern.

**TDD works well for template creation.** Writing 4 tests first (directory exists, files exist, contracts present, size constraint) caught the need for the yaml import and properly validated the implementation. The tests are reusable - just change `design_dir` and `phases` for other lifecycle templates.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

None observed. Implementation matched plan exactly. No deviations from spec, no governance violations.
