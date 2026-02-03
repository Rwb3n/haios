# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T20:01:32
# Arc: Portability

## Definition

**Arc ID:** portability
**Epoch:** E2.5
**Theme:** HAIOS as distributable, portable plugin
**Status:** Planned

---

## Purpose

Ensure HAIOS can be distributed as a standalone Claude Code plugin with proper initialization, configuration, and upgrade paths.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-PORTABLE-001 | All paths configurable via haios.yaml (no hardcoded paths) |
| REQ-PORTABLE-002 | Init ceremony creates runtime structure from seed |
| REQ-PORTABLE-003 | Templates have seed (source) and runtime (customizable) locations |

**NOTE:** These requirements are PROPOSED. Investigation WORK-094 will determine if they should be added to L4.

---

## Origin Context (Session 297 Discussion)

### The Question

During E2.5 decomposition review, stakeholder asked:
> "Can we verify that the templates folder will be migrated to haios/ for portability? With all dependencies and consumers considered?"

### Key Findings (Pre-Investigation)

1. **Templates currently at `.claude/templates/`** - not inside `haios/` portable core
2. **Hardcoded paths found in:**
   - `scaffold.py:266` - templates path
   - `cascade.py:43-44` - status/events files
   - `dependencies.py:22-23` - skills/agents paths
   - `audit_decision_coverage.py:306-307` - **BUG: hardcoded E2_4 epoch**

3. **Proposed pattern: Seed + Runtime**
   ```
   .claude/haios/templates/    # SEED (source of truth, travels with plugin)
   .claude/templates/          # RUNTIME (copied on init, customizable)
   ```

4. **Init ceremony needed** to copy seed → runtime on first use

### Stakeholder Direction

> "work-xxx type investigation. explore > investigation > append to epoch2.5 > append to arcs > more chapters?"

This arc was created to contain portability-related chapters that emerge from investigation.

---

## Chapters

| CH-ID | Title | Requirements | Dependencies |
|-------|-------|--------------|--------------|
| TBD | TBD - pending WORK-094 investigation | TBD | TBD |

---

## Exit Criteria

- [ ] All hardcoded paths identified and made configurable
- [ ] Template seed/runtime pattern implemented
- [ ] Init ceremony functional
- [ ] Plugin can be installed in fresh project via init
- [ ] Upgrade path documented (seed changes → runtime sync)

---

## References

- @docs/work/active/WORK-094/WORK.md (investigation)
- @.claude/haios/config/haios.yaml (path configuration)
- @.claude/haios/lib/scaffold.py (primary consumer of templates)
