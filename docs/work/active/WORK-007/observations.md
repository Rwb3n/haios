---
template: observations
work_id: WORK-007
captured_session: '225'
generated: '2026-01-21'
last_updated: '2026-01-21T23:22:38'
---
# Observations: WORK-007

## What surprised you?

- **Epoch extraction divergence:** CH-004 spec assumed EPOCH.md has YAML frontmatter. Reality: uses markdown structure. Adapted with `first_paragraph` extraction instead of `frontmatter`. Documented deviation (mem 82287).
- **Output compactness exceeded expectations:** Target <100 lines, actual 36 lines. 97% reduction from 1137 raw manifesto lines.

## What's missing?

- **ContextLoader integration not wired:** `just identity` exists as runtime consumer, but not wired into automated coldstart flow. Deferred to follow-on work.
- **No extraction validation:** If manifesto section structure changes, extraction silently returns empty/partial. Could warn on missing expected content.

## What should we remember?

- **Wrapper pattern validated:** IdentityLoader wraps base Loader via composition. Domain-specific loaders should follow: YAML config + thin wrapper + just recipe.
- **Path resolution:** Loader's `base_path` resolves relative to PROJECT_ROOT. Sibling modules use `Path(__file__).parent.parent` for config discovery.
- **First runtime consumer pattern:** Proves WORK-005 loader.py is usable. Future loaders (session, work) follow same pattern.

## What drift did you notice?

- **Node state not transitioned:** Session 224 implemented feature but left `current_node: backlog`. Checkpoint correctly stated "CHECK phase" but WORK.md wasn't updated.
- **Acceptance criteria ambiguity:** "can use" vs "does use" - capability exists, integration not complete.
