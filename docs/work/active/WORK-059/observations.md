---
template: observations
work_id: WORK-059
captured_session: '274'
generated: '2026-02-01'
last_updated: '2026-02-01T16:51:27'
---
# Observations: WORK-059

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- **CC Task System is meta-useful for investigation work itself.** I created TaskCreate items to track the investigation sub-tasks (Document, Compare, Analyze, Recommend) and the dependency chain worked exactly as designed. This was NOT planned - I was investigating the tool and ended up using it to structure the investigation. The activeForm spinner provided real-time visibility into which sub-task was active. This demonstrated the "tactical tracking" value proposition in real-time.

- **Memory search found prior decision about "Update Todos" that predates current TaskCreate system.** Concept 38334 said "We will not build our own Todo list system. We will use Claude Code's built-in Update Todos feature." This was about a DIFFERENT tool (the old Update Todos feature), but the decision principle is the same: leverage CC's ephemeral tracking rather than building custom. The system evolved but the principle persisted.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- **No CC Task persistence option.** If an agent wants to carry sub-tasks across sessions (e.g., multi-session implementation), CC Tasks can't do it. WorkEngine handles this, but there's no "promote ephemeral task to persistent work item" pattern. For now, not needed - the separation is clean. But if future use cases require hybrid persistence, we'd need to design a promotion mechanism.

- **CLAUDE.md lacks CC Task guidance.** The investigation found CC Tasks SHOULD be used for DO phase micro-tracking, but CLAUDE.md doesn't document this pattern yet. This is the spawned work item (WORK-062) to address.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- **Two-Layer Work Tracking Pattern:** Strategic (WorkEngine, persistent, governed) + Tactical (CC Tasks, ephemeral, UX-focused). This separation of concerns should be documented as a pattern. Systems that try to do both end up bloated - better to have clean handoff between layers.

- **"Eat your own dogfood" as investigation methodology.** Using CC Tasks TO investigate CC Tasks provided direct evidence impossible to get from documentation alone. When investigating a tool, USE the tool in the investigation process. The investigation itself becomes a test case.

- **L2 (RECOMMENDED) vs L3 (REQUIRED) matters for adoption patterns.** CC Task adoption is L2 because forcing every DO phase to use TaskCreate would add friction for simple tasks. Agent discretion is appropriate when the tool is helpful but not critical.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- **Investigation template still references HYPOTHESIZE-FIRST.** The investigation doc at `docs/work/active/WORK-059/investigations/001-claude-code-task-system-comparison.md` still has the old HYPOTHESIZE-FIRST framing in comments and structure. WORK-061 changed to EXPLORE-FIRST but fractured templates haven't fully propagated. This was noted in coldstart drift warnings but is worth re-flagging: the monolithic investigation template needs updating or deprecation.

- [x] None observed (for other drift areas - the template drift is the main observation)
