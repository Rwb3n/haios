# generated: 2026-01-03
# System Auto: last updated on: 2026-01-05T20:05:11

# HAIOS Core

Modular core of the HAIOS system. Contains configuration and future module implementations.

## Directory Structure

```
.claude/haios/
├── manifest.yaml        # E2-269: Plugin manifest (component declarations)
├── config/              # E2-246: Unified configuration files
│   ├── haios.yaml      # System config: manifest, toggles, thresholds
│   ├── cycles.yaml     # Cycle config: node bindings
│   └── components.yaml # Component registry (placeholder)
├── manifesto/          # L0-L7 Manifesto Corpus (immutable foundation)
└── modules/            # Future: Black box modules (E2-240+)
```

## Plugin Manifest (E2-269)

The `manifest.yaml` declares all HAIOS plugin components per SECTION-18-PORTABLE-PLUGIN-SPEC.md:

| Section | Contents |
|---------|----------|
| `plugin` | Metadata (name, version, description, author) |
| `targets` | LLM target declarations (Claude CLI) |
| `components` | Commands (18), Skills (15), Agents (7), Hooks (4) |
| `dependencies` | MCP servers, Python requirements |
| `versioning` | Semantic versioning strategy |

**Usage:** Future installer will read `manifest.yaml` to generate target-specific outputs.

**Tests:** `pytest tests/test_manifest.py -v`

## Configuration (E2-246)

The `config/` directory contains unified configuration files accessed via `ConfigLoader`:

```python
from config import ConfigLoader
config = ConfigLoader.get()
toggles = config.toggles
```

See `config/README.md` for details.

## Manifesto Corpus

The `manifesto/` directory contains the immutable foundation:
- **L0-telos.md:** WHY HAIOS exists (Agency Engine)
- **L1-principal.md:** WHO the operator is
- **L2-intent.md:** WHAT serving means
- **L3-requirements.md:** HOW to behave (7 principles)

These are read during `/coldstart`.

## Modules

The `modules/` directory contains black box module implementations:

| Module | Status | Purpose |
|--------|--------|---------|
| **GovernanceLayer** (E2-240) | Implemented | Policy enforcement, gate checks, transition validation |
| **MemoryBridge** (E2-241) | Planned | MCP wrapper, query modes, auto-link |
| **WorkEngine** (E2-242) | Planned | WORK.md owner, lifecycle management |

Each module is a swap point - implementations can be replaced without touching other modules.

See `modules/README.md` for usage details.
