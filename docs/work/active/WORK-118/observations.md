---
template: observations
work_id: 'WORK-118'
captured_session: '342'
generated: '2026-02-11'
last_updated: '2026-02-11T19:31:50'
---
# Observations: WORK-118

## What surprised you?

- [x] Rename blast radius: 391 references across 107 files for `-cycle` to `-ceremony` rename. Naming decisions made early become expensive to change. Forced scope split into WORK-118 (classification) + WORK-119 (rename).
- [x] HTML comments before YAML `---` delimiter broke all frontmatter parsing. `_parse_frontmatter()` regex uses `^---` requiring `---` at position 0. Caught immediately by TDD — test_ceremony_retrofit.py flagged 96 failures. Fixed by moving type to YAML field inside frontmatter.

## What's missing?

- [x] ceremony_registry.yaml has no `type:` field. Registry lists ceremonies by category/skill but doesn't track lifecycle vs ceremony distinction. Future work should add type to registry schema.
- [x] No `just set-ceremony` recipe exists as complement to `just set-cycle`. CeremonyRunner exists in code but justfile doesn't distinguish invocation types.

## What should we remember?

- [x] **Pattern: Thin wrapper over proven infrastructure.** CeremonyRunner wraps ceremony_context() rather than building a parallel system. CH-012 proved the runtime model; CH-013 added classification on top. "Evolve, don't replace" should be default when prior chapters established working infrastructure.
- [x] **Pattern: Backward-compat fallback import.** When extracting entries from a shared dict (CYCLE_PHASES → CEREMONY_PHASES), add a lazy import fallback in the getter. Allows gradual migration without breaking consumers.
- [x] **Anti-pattern: Content before YAML frontmatter.** Never add lines before `---` in files parsed for YAML frontmatter. Use fields inside the block.

## What drift did you notice?

- [x] CH-013 spec was written before CH-012 implementation and assumed a full CeremonyRunner parallel to CycleRunner. CH-012's ceremony_context() proved a different runtime model. Operator decision resolved the divergence (S342: evolve spec). Chapter specs should be treated as proposals when earlier chapters in the same arc change the landscape.
