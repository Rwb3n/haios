---
template: observations
work_id: WORK-068
captured_session: '278'
generated: '2026-02-01'
last_updated: '2026-02-01T22:49:48'
---
# Observations: WORK-068

## What surprised you?

**Preflight-checker on haiku was too rigid.** When testing the haiku model assignment, the preflight-checker demanded a formal PLAN.md file even for trivial 8-line frontmatter changes. It didn't recognize that the WORK.md Context section contained an inline plan. This is a good test case showing haiku's limitations - it was too literal/mechanical and didn't apply judgment about when formal ceremony is overkill. This validates the model selection principle: haiku for truly mechanical tasks, but structured judgment tasks may need sonnet.

**Model field just works.** Adding `model: haiku/sonnet/opus` to agent frontmatter required zero configuration beyond the field itself. Claude Code respected the setting immediately - the schema-verifier confirmed haiku, critique-agent confirmed opus. No restarts, no environment variables needed.

## What's missing?

**Preflight-checker needs trivial-work awareness.** The preflight-checker should recognize when work items have inline plans in Context section (trivial effort, explicit design table) and not demand formal PLAN.md files. Currently it's binary: PLAN.md exists or FAIL. A smarter check would be: "Does design exist? (in PLAN.md OR in WORK.md Context with effort: trivial)".

## What should we remember?

**Model selection by cognitive tier:**
- **opus**: Unrestricted reasoning, assumption surfacing, deep exploration
- **sonnet**: Structured reasoning with judgment (validation, anti-patterns)
- **haiku**: Mechanical/fast (schema lookup, test execution, structured extraction)

This is now documented in CLAUDE.md under Agents section with the principle: "Match model to cognitive requirements."

**The haiku limitation observed here validates the categorization.** Preflight-checker on haiku failed to apply judgment about inline plans vs formal plans. This is acceptable because preflight-checking IS meant to be mechanical (check boxes), but the agent definition may need refinement to handle edge cases.

## What drift did you notice?

- [x] None observed - implementation matched design
