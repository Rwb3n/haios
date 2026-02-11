---
template: observations
work_id: 'WORK-126'
captured_session: '349'
generated: '2026-02-11'
last_updated: '2026-02-11T22:26:12'
---
# Observations: WORK-126

## What surprised you?

- **Critique-agent caught a real plan defect (A4).** The step-ordering claim said "Tests 3, 4 should start passing" at Step 2, but Test 4 required `create_work()` seeding from Step 3. This is a good signal that critique adds value even for small, well-understood changes — it caught a logic error in the plan narrative that wouldn't have caused a code bug but would have confused an implementer following the plan.
- **The close() dual-write pattern is safe but non-obvious.** Critique surfaced (A3) that `close()` calls `_write_work_file()` then `_set_closed_date()` which does a second YAML round-trip. The new `queue_history` field survives because `_set_closed_date` does `yaml.safe_load -> modify -> yaml.dump` which preserves all keys. Worth knowing for future field additions.

## What's missing?

- **close() doesn't close node_history last entry's exited timestamp (critique A7).** This creates an asymmetry: `queue_history` in close shows a clean "done" terminal entry, but `node_history` won't. Pre-existing gap, now more visible. Not WORK-126 scope but should be tracked.
- **cycle_phase metadata drift.** Items that skip plan-authoring (like bug fixes) close with `cycle_phase: backlog` which is semantically wrong. S348 drift note captured this but no work item exists yet.

## What should we remember?

- **Parallel tracking field pattern:** Touch points are always (1) dataclass field, (2) parser with `fm.get("field", [])` backward compat, (3) writer persistence, (4) all mutation sites (set_*, create_*, close). Pure additive changes to work_engine.py are low-risk because defaults handle backward compat naturally.
- **Critique value for small work.** Even a 40-minute task benefited from critique catching A4 (step ordering) and surfacing A3 (dual-write pattern) and A7 (node_history asymmetry). The overhead was ~2 minutes for genuine insight.

## What drift did you notice?

- **Coldstart orchestrator prior_session shows 345, not 348.** The SessionLoader reads from the latest checkpoint file, but the most recent checkpoint (S348) wasn't the one picked up — possible filename sorting issue or checkpoint not committed.
- **Work items at backlog can be selected for work** without going through the ready queue. WORK-126 was at `queue_position: backlog` when selected, requiring manual `backlog -> ready -> working` transitions. The survey-cycle doesn't enforce that items must be at `ready` before selection.
