---
template: observations
work_id: WORK-074
captured_session: '282'
generated: '2026-02-02'
last_updated: '2026-02-02T00:41:58'
---
# Observations: WORK-074

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

**Explore agents found significant blind spots that two manual passes missed.** The assumption was that a verification pass (WORK-073) would catch anything the first pass (WORK-072) missed. In reality, both passes had similar blind spots because the same agent (main) with the same search patterns performed them. The Explore agents used different search strategies (import tracing, dead code detection, coverage analysis) that revealed: (1) tests importing from lib/ instead of modules/, (2) 3 skills never invoked anywhere, (3) 47+ undocumented components. This validates the operator's intuition that different agent types produce different discovery patterns.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

**A "component registry" pattern for SYSTEM-AUDIT.md.** The audit document tracks modules, skills, agents manually in prose tables. When 47+ components were discovered as undocumented, it revealed there's no structured registry that auto-discovers components. A pattern like: `just audit-components` that scans .claude/ directories and outputs a machine-readable inventory would prevent documentation drift. Currently the audit is manual and prone to staleness.

**Test coverage linking between modules and lib.** The E2-279 module decomposition created modules (cascade_engine, backfill_engine, spawn_tree) but tests still import from lib (cascade, backfill, spawn). There's no mechanism to flag when a module exists but tests reference a legacy lib path. A test hygiene check could detect `from X import` where X.py exists in both modules/ and lib/.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

**Parallel specialized Explore agents are more effective than serial manual passes.** For future audits, spawn 5-6 Explore agents with different focus areas (consumers, dead code, coverage, undocumented) rather than doing multiple passes with main agent. Each agent's different search heuristics catches different blind spots.

**"Tests pass" does not mean "modules are tested".** The test_lib_cascade.py tests pass because they test lib/cascade.py which works. But cascade_engine.py (the module) has different code paths that aren't exercised. When decomposing lib → modules, tests must be migrated to import from modules/, not just left pointing at lib/.

**Hook integration is solid - governance layer works.** The positive finding: all 21 activity matrix primitives mapped, all 4 hooks integrated, 0 governance gaps. This is evidence the E2.4 governed activities architecture is working as designed.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

**SYSTEM-AUDIT.md claims comprehensive coverage but misses 47+ components.** Section 7 (Module Status) says "All lib files have runtime consumers" but only details 8 of 24 lib files. The .claude/REFS/ directory (11 files), .claude/mcp/ (4 files), critique_frameworks/ (2 files), and output-styles/ (1 file) are not mentioned anywhere in the audit.

**Test files reference lib/ instead of modules/ after E2-279 decomposition.** The module decomposition created cascade_engine.py, backfill_engine.py, spawn_tree.py but tests still do `from cascade import`, `from backfill import`, `from spawn import`. The tests technically pass (lib still exists) but don't test the actual module code paths.

**Three skills defined but never invoked.** audit, schema-ref, extract-content exist as skill files but grep finds 0 invocations. Either these are aspirational (planned but not integrated) or they represent documentation drift where skills were created but workflows never wired to use them.
