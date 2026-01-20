# generated: 2026-01-20
# System Auto: last updated on: 2026-01-20T21:05:01
# Chapter: Discovery Root

## Definition

**Chapter ID:** CH-001
**Arc:** configuration
**Status:** Planned

---

## Problem

Agent cannot discover where things are configured.

Current state:
- haios.yaml has some config
- haios-status.json has computed state
- Paths hardcoded in Python modules
- Paths hardcoded in skills/commands
- Agent must "know" where to look

---

## Agent Need

> "From one file, I can find any configuration in the system."

---

## Requirements

### R1: Single Entry Point

```
Agent reads: haios.yaml
Agent finds: path to any other config
```

### R2: Discovery Section

```yaml
# In haios.yaml
discovery:
  coldstart: config/coldstart.yaml
  loaders: config/loaders/
  session: ../.claude/session
  manifesto: manifesto/
  epochs: epochs/
```

### R3: No Dead Ends

Every path in discovery must exist. Missing file = system error.

### R4: Relative Paths

All paths relative to haios.yaml location. Agent resolves from known root.

---

## Interface

**Input:** Agent needs to find config for X

**Process:**
```
1. Read haios.yaml
2. Look in discovery section
3. Resolve relative path
4. Read target config
```

**Output:** Path to config file or directory

---

## Success Criteria

- [ ] Agent can find coldstart config from haios.yaml
- [ ] Agent can find loader configs from haios.yaml
- [ ] Agent can find session file from haios.yaml
- [ ] No hardcoded paths outside haios.yaml

---

## Non-Goals

- Config validation (separate chapter)
- Config hot-reload
- Config versioning
