---
template: observations
work_id: 'WORK-115'
captured_session: '336'
generated: '2026-02-10'
last_updated: '2026-02-10T20:45:09'
---
# Observations: WORK-115

## What surprised you?

The critique agent's A7 finding was the most valuable catch this session: the plan's Goal statement claimed "provides structured inputs to CH-011 contracts" but the implementation didn't wire ceremony_context to enforce_ceremony_contract at all. This was a silent goal/implementation gap that would have gone unnoticed through testing alone - tests verify what IS built, not what's MISSING from scope. The critique agent earned its cost on this single finding. Also notable: all 9 assumptions were addressable with minimal plan revision - the plan's structure was sound, just specific implementation details (contextvars vs threading.local, ConfigLoader vs raw I/O, datetime import) needed correction.

## What's missing?

The ceremony_context is now infrastructure without consumers. No ceremony skill currently wraps its WorkEngine calls in `ceremony_context()`. In warn mode this is invisible - everything works as before. But the value proposition (governed state changes with audit trail) is unrealized until ceremony skills adopt it. This is explicitly deferred but represents a gap between capability and usage. Also missing: no mechanism to automatically inject structured inputs from ceremony_context into CH-011's enforce_ceremony_contract() - this would complete the CH-011/CH-012 integration and make contract validation meaningful (currently validates empty inputs, producing no-op warnings per memory 84329).

## What should we remember?

Pattern: `contextvars.ContextVar` is the correct choice for context propagation in Python, even in single-threaded code. The delta from `threading.local()` is literally one import change, and it future-proofs for async/subagent propagation. Pattern: public guard functions (`check_ceremony_required`) imported cross-module are cleaner than routing through GovernanceLayer instance methods when the check is stateless - follows the pure additive pattern from memory 84334. Pattern: naming toggles with their scope (`ceremony_context_enforcement` vs `ceremony_contract_enforcement`) prevents operator confusion when multiple toggles control related but distinct enforcement mechanisms.

## What drift did you notice?

CH-012 spec (`.claude/haios/epochs/E2_5/arcs/ceremonies/CH-012-SideEffectBoundaries.md`, line 132) lists `update_work()` as a protected operation, but WorkEngine has no such public method. The spec was written against the chapter design, not the actual API. The deliverable in WORK-115 WORK.md (line 76) also references "update_work". This is a spec/implementation naming drift - the actual guarded methods are close(), create_work(), transition(), set_queue_position(), archive(). The CH-012 chapter file should be updated to reflect actual method names.
