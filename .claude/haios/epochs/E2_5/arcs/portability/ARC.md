# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T20:14:09
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

**Status:** VALIDATED by WORK-094 (Session 298). Ready for L4 addition.

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

## Investigation Findings (WORK-094, Session 298)

### Validated Findings

1. **Portability test FAILS** - Components (templates, skills, agents, hooks, commands) live outside `.claude/haios/`
2. **17 hardcoded paths across 7 files** violate REQ-CONFIG-001:
   - `scaffold.py` (4), `status.py` (4), `cascade.py` (3), `dependencies.py` (2), `audit_decision_coverage.py` (2), `work_loader.py` (1), `audit.py` (1)
3. **ConfigLoader underutilized** - Only 8 usages across 3 files vs 17 hardcoded
4. **No init ceremony exists** - No mechanism to bootstrap fresh installations
5. **BUG confirmed**: `audit_decision_coverage.py:306-307` has hardcoded E2_4 epoch path

### Architecture Decision: Seed + Runtime Pattern

```
.claude/haios/                  ← SEED (portable, canonical)
├── templates/, skills/, agents/, hooks/, commands/

.claude/                        ← RUNTIME (project-specific, customizable)
├── templates/, skills/, agents/, hooks/, commands/
```

Init ceremony copies seed → runtime on fresh install. Upgrades diff seed vs runtime.

---

## Chapters

| CH-ID | Title | Requirements | Dependencies |
|-------|-------|--------------|--------------|
| CH-028 | PathConfigMigration | REQ-PORTABLE-001, REQ-CONFIG-001 | None |
| CH-029 | SeedStructure | REQ-PORTABLE-003 | CH-028 |
| CH-030 | InitCeremony | REQ-PORTABLE-002 | CH-029 |
| CH-031 | UpgradePath | REQ-PORTABLE-002 | CH-030 |

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
