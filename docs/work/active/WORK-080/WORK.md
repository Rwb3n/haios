---
template: work_item
id: WORK-080
title: Single Source Path Constants Implementation
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-02
spawned_by: INV-041
chapter: CH-004
arc: chariot
closed: '2026-02-02'
priority: medium
effort: medium
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/config/haios.yaml
- .claude/haios/lib/config.py
acceptance_criteria:
- All Python modules use ConfigLoader.paths instead of hardcoded path constants
- haios.yaml contains paths section with all path definitions
- Tests verify path resolution works correctly
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-02 17:23:20
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 83179
- 83180
- 83181
- 83182
- 83198
- 83199
- 83200
- 83201
- 83202
- 83203
- 83204
- 83205
- 83206
- 83207
- 65046
- 83208
- 83209
- 83210
- 82309
- 83211
- 83212
extensions: {}
version: '2.0'
generated: 2026-02-02
last_updated: '2026-02-02T17:43:47'
---
# WORK-080: Single Source Path Constants Implementation

---

## Context

**Problem:** Path patterns are defined in multiple places across the codebase (70+ files), leading to drift when conventions change. INV-041 investigated this and recommended extending haios.yaml with a `paths:` section.

**Root cause:** Each layer defines its own path strings. When a pattern changes, all consumers must be manually updated.

**Solution (from INV-041):** Centralize path definitions in haios.yaml, consumed via ConfigLoader.paths property.

---

## Deliverables

- [ ] Add `paths:` section to `.claude/haios/config/haios.yaml` with all path definitions
- [ ] Add `ConfigLoader.paths` property to `.claude/haios/lib/config.py`
- [ ] Add `ConfigLoader.get_path(key, **kwargs)` method for interpolated paths
- [ ] Migrate `work_engine.py`: Replace WORK_DIR, ACTIVE_DIR, ARCHIVE_DIR constants
- [ ] Migrate `context_loader.py`: Replace MANIFESTO_PATH, STATUS_PATH, CONFIG_PATH constants
- [ ] Add tests for ConfigLoader.paths and get_path()
- [ ] Update CLAUDE.md with ConfigLoader.paths usage pattern

> **Scope Note:** Remaining 8 Python files with hardcoded paths deferred to follow-up work item. This work establishes the pattern; incremental migration follows.

---

## Design (from INV-041)

### Schema Addition (haios.yaml)

```yaml
paths:
  # Work item paths
  work_dir: "docs/work"
  work_active: "docs/work/active"
  work_archive: "docs/work/archive"
  work_item: "docs/work/active/{id}/WORK.md"
  work_plan: "docs/work/active/{id}/plans/PLAN.md"

  # Document paths
  checkpoints: "docs/checkpoints"
  reports: "docs/reports"
  adr: "docs/ADR"
  specs: "docs/specs"

  # Plugin paths
  templates: ".claude/templates"
  skills: ".claude/skills"
  commands: ".claude/commands"
  agents: ".claude/agents"
  hooks: ".claude/hooks"

  # Config paths
  haios_config: ".claude/haios/config"
  manifesto: ".claude/haios/manifesto"
```

### ConfigLoader Extension

```python
@property
def paths(self) -> Dict[str, str]:
    """Path constants (single source of truth)."""
    return self._haios.get("paths", {})

def get_path(self, key: str, **kwargs) -> Path:
    """Get path with placeholder substitution, returns Path object."""
    template = self.paths.get(key, "")
    resolved = template.format(**kwargs) if kwargs else template
    return Path(resolved)
```

---

## Migration Scope (11 Python files)

| File | Constants to Replace |
|------|---------------------|
| `work_engine.py` | WORK_DIR, ACTIVE_DIR, ARCHIVE_DIR |
| `context_loader.py` | MANIFESTO_PATH, STATUS_PATH, CONFIG_PATH |
| `scaffold.py` | TEMPLATE_CONFIG dirs (partial) |
| `status.py` | Various path references |
| `work_item.py` | Path patterns |
| `audit.py` | Glob patterns |
| `node_cycle.py` | Path references |
| `work_loader.py` | Path references |
| `session_loader.py` | Path references |
| `pre_tool_use.py` | Path patterns |
| `post_tool_use.py` | Path patterns |

---

## History

### 2026-02-02 - Created (Session 290)
- Spawned from INV-041 investigation findings
- Architecture decision: extend haios.yaml + ConfigLoader

---

## References

- Spawned by: INV-041 (Single Source Path Constants Architecture)
- Chapter: Chariot CH-004 (PathAuthority)
- Memory refs: 83179-83182 (INV-041 findings)
