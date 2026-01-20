# generated: 2026-01-20
# System Auto: last updated on: 2026-01-20T21:05:38
# Chapter: Loader Base

## Definition

**Chapter ID:** CH-003
**Arc:** configuration
**Status:** Planned

---

## Problem

Agent reads entire files when it needs specific content.

Current state:
```
Agent reads: L0-telos.md (101 lines)
Agent needs: Prime directive (1 sentence)
```

Waste: 100 lines of context tokens.

---

## Agent Need

> "I need specific content extracted from files. Tell me what I need, not everything."

---

## Requirements

### R1: Extraction DSL

Config defines what to extract:

```yaml
extract:
  mission:
    file: manifesto/L0-telos.md
    section: "## The Prime Directive"
    type: blockquote
```

### R2: Extraction Types

| Type | What it extracts |
|------|------------------|
| `blockquote` | First `> ` block in section |
| `first_paragraph` | Text until blank line |
| `all_h3` | All `### ` with first line |
| `numbered_list` | All `1. ` items |
| `bulleted_list` | All `- ` items |
| `frontmatter` | YAML field |
| `code_block` | First fenced block |
| `full_section` | Everything under heading |

### R3: Output Formatting

Loader outputs formatted text, not raw extraction:

```yaml
output:
  template: |
    Mission: {mission}
    Principles:
    {principles}
```

### R4: Injection Ready

Output is a string suitable for direct injection into agent context via Bash output.

---

## Interface

**Loader contract:**
```
Input: config_path (yaml file)
Output: formatted string

Methods:
  - extract() -> dict of extracted values
  - format(dict) -> string
  - load() -> string (extract + format)
```

---

## Success Criteria

- [ ] Extraction DSL documented
- [ ] All extraction types implemented
- [ ] Output is injection-ready (not file paths)
- [ ] Config-driven (no hardcoded extractions)

---

## Non-Goals

- Caching extracted content
- Incremental extraction
- Multi-file joins
