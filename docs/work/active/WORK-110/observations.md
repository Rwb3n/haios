---
template: observations
work_id: 'WORK-110'
captured_session: '329'
generated: '2026-02-09'
last_updated: '2026-01-18T22:09:58'
---
# Observations: WORK-110

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- Implementation was significantly faster than plan estimated (~30 min vs ~2.5 hours). The plan's approved design was complete enough that DO phase was nearly mechanical: write tests, write module, write skills. The prior-session gate overhead (plan-authoring, plan-validation, preflight, critique) was disproportionate to the actual implementation effort, but the result was zero ambiguity during implementation. This validates the "front-load thinking" pattern — even if gates feel heavy, they produce clean DO phases.
- The `portal_manager` import failure was the only friction point. Test file needed `sys.path.insert(0, str(_root / ".claude" / "haios" / "modules"))` to let WorkEngine.create_work() lazy-load portal_manager.py at runtime. This is a known pattern from test_work_engine.py:27 but easy to miss when creating new test files.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- No consumer wiring yet. The 4 ceremony skills exist with contracts and the Python module exists with functions, but nothing in the system automatically invokes ceremonies when queue transitions happen. Direct `set_queue_position()` calls remain the runtime path. Future work should wire survey-cycle to use queue-commit, work-creation-cycle to use queue-intake, etc. This is documented in the plan (Step 6) as intentionally out of scope.
- No test fixture sharing between test_work_engine.py and test_queue_ceremonies.py. Both files duplicate the `_load_module()` helper, governance/engine fixtures, and sys.path setup. A shared conftest.py or test helper module would reduce duplication. Not blocking but worth addressing if more test files are created for queue/ceremony features.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- **Ceremony-as-wrapper pattern:** queue_ceremonies.py demonstrates a clean pattern for adding ceremony logging on top of existing engine methods without modifying them. `execute_queue_transition()` wraps `set_queue_position()` — validation stays in the engine, audit trail in the ceremony layer. This pattern should be reused for other ceremony implementations (CH-011 through CH-017 in the ceremonies arc).
- **Skill-as-contract pattern:** Ceremony skills (queue-unpark, queue-intake, etc.) are documentation-first artifacts that define input/output contracts. They don't contain executable code — the Python module provides runtime. This separation means skills can evolve contracts independently from implementation. Good pattern for all 19 ceremonies.
- **Test sys.path recipe:** When creating test files for modules that depend on WorkEngine, always add both paths: `sys.path.insert(0, str(_root / ".claude" / "haios" / "modules"))` and `sys.path.insert(0, str(_root / ".claude" / "haios" / "lib"))`. The modules path is needed for lazy-loaded dependencies like portal_manager.py.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- CH-010 spec (line 61) lists 5 ceremonies with "Unpark" as parked->backlog only. But the plan (and now implementation) treats Unpark as bidirectional (parked<->backlog), with Park as the reverse direction using the same skill. The spec's ceremony table doesn't explicitly list Park. The WORK.md AC4 says "Unpark moves parked->backlog (and Park moves backlog->parked)" which is correct but the CH-010 spec table should be updated to reflect bidirectional Unpark/Park.
- Scaffold observations template has `last_updated: '2026-01-18T22:09:58'` which is the hardcoded session 247 bug noted in prior session pending items. Confirmed still present — `just scaffold-observations` uses stale timestamp. Not a blocker but validates the pending bug report from Session 328.
