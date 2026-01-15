---
allowed-tools: Read, Glob, Bash, mcp__haios-memory__memory_search_with_experience,
  mcp__haios-memory__db_query
description: Initialize session by loading essential context files
generated: '2025-12-25'
last_updated: '2026-01-15T19:53:08'
---

# Cold Start Initialization

**MUST** run at the start of every session.

---

## Step 1: Load Config

Read `.claude/haios/config/haios.yaml` first - this drives everything else.

Extract:
- `epoch.epoch_file` - path to current epoch
- `epoch.active_arcs` - list of active arcs (ADR-042: arcs > chapters)
- `epoch.arcs_dir` - path to arcs directory

---

## Step 2: Load Manifesto (MUST)

**MUST** read the foundational context - immutable philosophy:

1. `.claude/haios/manifesto/L0-telos.md` - Why HAIOS exists (IMMUTABLE)
2. `.claude/haios/manifesto/L1-principal.md` - Who the operator is
3. `.claude/haios/manifesto/L2-intent.md` - What serving the operator means
4. `.claude/haios/manifesto/L3-requirements.md` - Behavioral principles (IMMUTABLE)
5. `.claude/haios/manifesto/L4-implementation.md` - Technical specifications (dynamic)

---

## Step 3: Load Epoch Context (MUST)

**MUST** read from paths in haios.yaml:

1. Read `epoch.epoch_file` - current epoch definition
2. For each arc in `epoch.active_arcs`:
   - Read `{epoch.arcs_dir}/{arc}/ARC.md`

---

## Step 4: Load Checkpoint Manifest

Find the most recent checkpoint in `docs/checkpoints/` and read its frontmatter.

```bash
ls -t docs/checkpoints/*.md | head -1
```

The checkpoint is a **loading manifest** with these fields:

| Field | Action |
|-------|--------|
| `load_principles` | **MUST** read each file listed |
| `load_memory_refs` | **MUST** query each concept ID |
| `pending` | Surface as work options |
| `drift_observed` | **MUST** surface as warnings before work selection |

**If `drift_observed` is non-empty:** Display warnings prominently before proceeding.

---

## Step 5: Load Principles (from manifest)

For each file in `load_principles`:
- Read the file
- Note key principles that govern this session's work

---

## Step 6: Load Memory (from manifest)

For each concept ID in `load_memory_refs`:

```sql
SELECT id, type, content FROM concepts WHERE id IN ({load_memory_refs})
```

These are the learnings from the prior session. Inject into context.

---

## Step 7: Load Agent Instructions

Read `CLAUDE.md` - agent bootstrap and quick reference.

---

## Step 8: Session Start

```bash
just session-start {N}
```

Where N = last_session + 1 from `.claude/haios-status.json`.

---

## Step 9: Summary Output

Provide brief summary:
- **Manifesto loaded:** L0-L4 (confirm read)
- **Epoch context:** Which epoch + which arcs loaded
- **Principles loaded:** Which files from `load_principles`
- **Memory loaded:** Count of concepts from `load_memory_refs`
- **Drift warnings:** Any `drift_observed` items

---

## Step 10: Invoke Survey Cycle

**MUST** chain to survey-cycle for work selection:

```
Skill(skill="survey-cycle")
```

Survey-cycle owns routing:
- Checks checkpoint `pending` for prior work
- Presents options from `just ready`
- Routes to correct cycle based on work type

---

## Key Principle

**Ground yourself first. Config → Manifesto → Epoch → Checkpoint → Survey.**

Coldstart loads context. Survey-cycle selects work. Agent doesn't skip the chain.
