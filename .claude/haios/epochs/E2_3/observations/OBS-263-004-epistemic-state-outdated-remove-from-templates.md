---
id: OBS-263-004
title: epistemic_state.md outdated - remove from templates
session: 263
date: 2026-01-30
work_id: null
dimension: infrastructure
priority: medium
status: pending
generated: 2026-01-30
last_updated: '2026-01-30T19:46:18'
---
# OBS-263-004: epistemic_state.md outdated - remove from templates

## What Happened

Operator flagged that `@docs/epistemic_state.md` is "super outdated" and "far from useful."

## Evidence

**File last updated:** 2026-01-14 (16 days stale)

**Content drift:**
- Says "Epoch 2.2" - we're in E2.3
- Says "Sessions: 190" - we're at 263
- Lists "Active Chapters: Chariot, Breath, Form, Ground" - these are E2.2 chapters
- References "9 modules" - architecture has evolved

**Template pollution:**
- Referenced in `@` link in work_item.md template (line 38)
- **716 files** contain `@docs/epistemic_state.md` as a result
- Every work item, investigation, plan links to this outdated file
- Agents instructed to read `@` references waste context on stale content

## Root Cause

1. `docs/epistemic_state.md` was a manual "current state" doc that requires human maintenance
2. It was added to templates as "always useful context"
3. No one maintains it, so it drifts
4. Templates propagate the stale link to every new document

## Recommendation

### Immediate Actions

1. **Remove from templates:**
   - `.claude/templates/work_item.md` - remove line 38 (`@docs/epistemic_state.md`)
   - `.claude/templates/investigation.md` - remove if present
   - `.claude/templates/plan.md` - remove if present

2. **Delete or archive the file:**
   - `docs/epistemic_state.md` → archive or delete
   - The EPOCH.md files are the authoritative "current state" now

### Do NOT

- Mass-edit 716 existing files to remove the reference (too disruptive)
- Existing files can keep the stale link; new files won't have it

## Alternative

If epistemic_state.md has value, it should be **generated** not manually maintained:
- `just epistemic-state` could generate from EPOCH.md + session count + active arcs
- But this adds maintenance burden for marginal value

**Operator verdict:** Remove it. EPOCH.md is the authoritative current state.

---

## Related

- `.claude/templates/work_item.md:38`
- `docs/epistemic_state.md` (the outdated file)
- `.claude/haios/epochs/E2_3/EPOCH.md` (the authoritative current state)
