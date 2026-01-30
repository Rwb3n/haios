# generated: 2026-01-30
# System Auto: last updated on: 2026-01-30T22:05:46
# Chapter: EpochTransition

## Definition

**Chapter ID:** CH-008
**Arc:** flow
**Status:** Planned
**Depends:** CH-007 (BatchOperations)

---

## Problem

Epoch transitions require updating multiple config files. Currently manual and error-prone.

Session 265 discovered these updates were needed:
- haios.yaml (epoch config)
- identity.yaml (epoch path)
- CLAUDE.md (version footer)
- epistemic_state.md (removed - was dead file)

---

## Epoch Transition Ceremony

### Files to Update

| File | Section | Update |
|------|---------|--------|
| `.claude/haios/config/haios.yaml` | `epoch.*` | current, epoch_file, arcs_dir, observations_dir, prior_epoch, active_arcs |
| `.claude/haios/config/loaders/identity.yaml` | `epoch_name.file` | Path to new EPOCH.md |
| `CLAUDE.md` | Footer | Version line |

### Files to Create

| File | Purpose |
|------|---------|
| `.claude/haios/epochs/E{X}_{Y}/EPOCH.md` | Epoch definition |
| `.claude/haios/epochs/E{X}_{Y}/arcs/` | Arc directories |
| `.claude/haios/epochs/E{X}_{Y}/architecture/` | Architecture docs |
| `.claude/haios/epochs/E{X}_{Y}/observations/` | Session observations |

### Files to Remove/Archive

| File | Action |
|------|--------|
| `docs/epistemic_state.md` | Removed (dead file - epoch context in EPOCH.md) |
| Prior epoch work items | Triage: carry, backlog, or archive |

---

## Proposed Interface

### Option A: Command

```bash
/new-epoch E2.5 "The Name"
```

Creates structure, updates configs, prompts for arc definitions.

### Option B: Just Recipe

```bash
just new-epoch E2.5 "The Name"
```

### Option C: Scaffold + Manual

```bash
just scaffold epoch E2.5 "The Name"
# Then manually update configs
```

---

## Ceremony Steps

1. **SCAFFOLD** - Create epoch directory structure
2. **DEFINE** - Write EPOCH.md with purpose, exit criteria
3. **MIGRATE** - Triage prior epoch arcs/work
4. **CONFIG** - Update haios.yaml, identity.yaml, CLAUDE.md
5. **COMMIT** - Single commit for epoch transition

---

## Session 265 Discovery

Epoch transition from E2.3 → E2.4 required:

```bash
# 1. Create structure
mkdir -p .claude/haios/epochs/E2_4/{architecture,arcs,observations}

# 2. Write EPOCH.md
# (manual)

# 3. Update haios.yaml
# epoch.current, epoch_file, arcs_dir, etc.

# 4. Update identity.yaml
# epoch_name.file path

# 5. Update CLAUDE.md footer
# Version line

# 6. Remove dead files
git rm docs/epistemic_state.md
```

This should be automated via `/new-epoch` command.

---

## Success Criteria

- [ ] `/new-epoch` command exists
- [ ] Creates epoch directory structure
- [ ] Updates all config files
- [ ] Prompts for epoch definition
- [ ] Single commit for transition

---

## References

- @.claude/haios/epochs/E2_4/EPOCH.md (created manually this session)
- @.claude/haios/config/haios.yaml
- @.claude/haios/config/loaders/identity.yaml
- Session 265 epoch transition
