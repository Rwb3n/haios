---
template: observations
work_id: 'WORK-114'
captured_session: '335'
generated: '2026-02-10'
last_updated: '2026-02-10T00:42:08'
---
# Observations: WORK-114

## What surprised you?

The critique agent's A2 finding (relative path `Path(".claude/skills")` vs `Path(__file__)` anchored navigation) was a genuine consistency issue that would have caused silent failures if cwd ever changed. The existing hook code at `pre_tool_use.py` lines 42, 151, 672 all use `Path(__file__)` — the plan's initial design deviated from this pattern without noticing. This validates the critique gate's value: it catches pattern inconsistencies that are invisible during focused design. Memory 84304-84310 from S334 already established this, and S335 reinforced it.

## What's missing?

Structured ceremony inputs at PreToolUse time. The Skill tool_input is `{"skill": "name", "args": "free-text string"}` — there's no way to map positional args to named contract fields. This means warn-mode enforcement is effectively a no-op (every ceremony warns identically about missing required fields). The real value requires CH-012's `ceremony_context()` which provides Python-level structured inputs. Until then, WORK-114 establishes the wiring but not meaningful validation. This was documented as a known limitation (critique A1) in the plan's Risks table.

## What should we remember?

**Pattern: Pure additive hook extension.** Adding `_check_ceremony_contract()` as a standalone function + single call-site insertion (6 lines at line 179) is the cleanest hook extension pattern. No existing lines modified except the insertion point. All new code in separate functions with independent try/except fail-permissive handling. This pattern should be reused for future hook extensions to `pre_tool_use.py`.

**Pattern: Registry-as-gate.** The ceremony registry (`ceremony_registry.yaml`) serves as a gate (is this skill a ceremony?) while the actual contract comes from the skill's YAML frontmatter. This separation means the registry doesn't need to be kept in sync with contract details — it just needs to list which skills are ceremonies. The contract source of truth is the skill file, not the registry.

## What drift did you notice?

- [ ] None observed — implementation matched plan exactly after critique revisions. Hook architecture accommodated the new check cleanly.
