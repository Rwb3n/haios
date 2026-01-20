# generated: 2026-01-20
# System Auto: last updated on: 2026-01-20T21:07:45
# Arc: Configuration

## Definition

**Arc ID:** configuration
**Epoch:** E2.3
**Status:** Active
**Pressure:** [volumous]

---

## Mission

Object-oriented, discoverable configuration system for HAIOS.

---

## Core Principle

**Discoverability:** From one root file, find anything.

```
haios.yaml
    │
    ├──► coldstart.yaml
    ├──► loaders/*.yaml
    ├──► epochs/*.yaml
    └──► (all other config)
```

---

## Architecture

### Discovery Tree

```
.claude/haios/
├── config/
│   ├── haios.yaml              # ROOT - discovery index
│   ├── coldstart.yaml          # Orchestration phases
│   ├── loaders/
│   │   ├── identity.yaml       # Manifesto + epoch extraction
│   │   ├── session.yaml        # Checkpoint + memory extraction
│   │   └── work.yaml           # Queue + pending extraction
│   └── epochs/
│       └── E2_3.yaml           # Epoch-specific config
├── manifesto/                  # Source files (unchanged)
└── epochs/                     # Epoch definitions (unchanged)
```

### Coldstart Flow

```
┌─────────────────────────────────────────────────────────┐
│                      COLDSTART                          │
│                   (just coldstart)                      │
└─────────────────────────┬───────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ PHASE 1  │    │ PHASE 2  │    │ PHASE 3  │
    │ identity │───►│ session  │───►│   work   │
    └──────────┘    └──────────┘    └──────────┘
          │               │               │
      [BREATHE]       [BREATHE]       [SELECT]
```

### Loader Pattern

```python
class Loader:
    """Base loader interface."""

    def __init__(self, config_path: Path):
        self.config = yaml.load(config_path)

    def extract(self) -> dict:
        """Extract data from sources per config."""
        raise NotImplementedError

    def format(self, data: dict) -> str:
        """Format extracted data for injection."""
        raise NotImplementedError

    def load(self) -> str:
        """Extract and format. Single entry point."""
        return self.format(self.extract())
```

### Extraction DSL

```yaml
# How to extract from structured markdown
extract:
  mission:
    section: "## The Prime Directive"
    type: blockquote

  principles:
    section: "## Core Behavioral Principles"
    type: all_h3

  constraints:
    section: "**Known Constraints:**"
    type: numbered_list
    limit: 5
```

**Extraction Types:**
| Type | Description |
|------|-------------|
| `blockquote` | First `> ` prefixed block |
| `first_paragraph` | Text until blank line |
| `all_h3` | All `### ` headings with first line |
| `numbered_list` | All `1. ` items |
| `bulleted_list` | All `- ` items |
| `frontmatter` | YAML frontmatter field |
| `code_block` | First fenced code block |

---

## Files to Create

| File | Purpose | Priority |
|------|---------|----------|
| `config/haios.yaml` | Discovery root (migrate existing) | 1 |
| `config/coldstart.yaml` | Phase orchestration | 1 |
| `config/loaders/identity.yaml` | Manifesto extraction rules | 2 |
| `config/loaders/session.yaml` | Session context rules | 2 |
| `config/loaders/work.yaml` | Work queue rules | 2 |
| `.claude/lib/loader.py` | Base loader + extraction | 2 |
| `.claude/session` | Single integer file | 1 |

---

## Chapters

| Chapter | File | Status |
|---------|------|--------|
| CH-001 | [Discovery Root](CH-001-discovery-root.md) | Planned |
| CH-002 | [Session Simplify](CH-002-session-simplify.md) | Planned |
| CH-003 | [Loader Base](CH-003-loader-base.md) | Planned |
| CH-004 | [Identity Loader](CH-004-identity-loader.md) | Planned |
| CH-005 | [Session Loader](CH-005-session-loader.md) | Planned |
| CH-006 | [Work Loader](CH-006-work-loader.md) | Planned |
| CH-007 | [Coldstart Orchestrator](CH-007-coldstart-orchestrator.md) | Planned |
| CH-008 | [Status Prune](CH-008-status-prune.md) | Planned |

---

## Exit Criteria

- [ ] Single discovery root (haios.yaml points to all config)
- [ ] Session number from `.claude/session` (not 258KB JSON)
- [ ] Coldstart via injection (no manual file reads)
- [ ] All loaders config-driven
- [ ] haios-status.json < 10KB

---

## References

- Session 215 discussion (this session)
- @.claude/haios/config/haios.yaml (current, to migrate)
