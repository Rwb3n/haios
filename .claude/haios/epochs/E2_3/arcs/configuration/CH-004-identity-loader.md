# generated: 2026-01-20
# System Auto: last updated on: 2026-01-20T21:05:58
# Chapter: Identity Loader

## Definition

**Chapter ID:** CH-004
**Arc:** configuration
**Status:** Planned
**Depends:** CH-003 (Loader Base)

---

## Problem

Agent reads 5 manifesto files to establish identity.

Current state:
```
Coldstart reads:
  - L0-telos.md (101 lines)
  - L1-principal.md (147 lines)
  - L2-intent.md (114 lines)
  - L3-requirements.md (192 lines)
  - L4-implementation.md (583 lines)

Total: 1137 lines loaded as raw context
```

Agent needs ~50 lines of extracted essence.

---

## Agent Need

> "Who am I? What's my mission? What principles govern me? What constraints apply?"

---

## Requirements

### R1: Identity Extraction Config

```yaml
# config/loaders/identity.yaml
sources:
  L0:
    file: manifesto/L0-telos.md
    extract:
      mission:
        section: "## The Prime Directive"
        type: blockquote
      companion:
        section: "## The Companion Relationship"
        type: bulleted_list
        limit: 4

  L1:
    file: manifesto/L1-principal.md
    extract:
      constraints:
        section: "**Known Constraints:**"
        type: numbered_list

  L3:
    file: manifesto/L3-requirements.md
    extract:
      principles:
        section: "## Core Behavioral Principles"
        type: all_h3
```

### R2: Epoch Context

Identity includes current epoch:

```yaml
  epoch:
    source: "{discovery.epochs}/{epoch.current}/EPOCH.md"
    extract:
      name: frontmatter
      field: name
      arcs: section."## Arcs".table.column[0]
```

### R3: Output Format

```
=== IDENTITY ===
Mission: {mission}

Principles:
{principles}

Constraints:
{constraints}

Epoch: {epoch.name}
Arcs: {epoch.arcs}
```

### R4: Compact

Output < 100 lines. Essence, not documentation.

---

## Interface

```bash
just identity
# Outputs formatted identity context
```

---

## Success Criteria

- [ ] Identity loaded via config, not hardcoded reads
- [ ] Output < 100 lines
- [ ] Contains: mission, principles, constraints, epoch
- [ ] Coldstart Phase 1 uses this loader

---

## Non-Goals

- Full manifesto content
- L4 technical specs (that's session/work context)
- Historical epoch info
