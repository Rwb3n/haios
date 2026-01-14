# generated: 2026-01-03
# System Auto: last updated on: 2026-01-03T14:42:46

# HAIOS Configuration

E2-246: Unified configuration files for HAIOS modules.

## Files

| File | Purpose | Source |
|------|---------|--------|
| `haios.yaml` | System config: manifest, toggles, thresholds | Consolidated from `governance-toggles.yaml`, `routing-thresholds.yaml` |
| `cycles.yaml` | Cycle config: node bindings, cycle definitions | Consolidated from `node-cycle-bindings.yaml` |
| `components.yaml` | Component registry: skills, agents, hooks | Placeholder for E2-240 |

## Usage

```python
from config import ConfigLoader

config = ConfigLoader.get()

# Access sections
toggles = config.toggles           # governance toggles
thresholds = config.thresholds     # routing thresholds
node_bindings = config.node_bindings  # node-cycle bindings

# Or access full config files
haios = config.haios               # full haios.yaml
cycles = config.cycles             # full cycles.yaml
components = config.components     # full components.yaml
```

## Schema

### haios.yaml

```yaml
manifest:
  name: haios
  version: "2.2"
  description: "Hybrid AI Operating System - Trust Engine"

toggles:
  block_powershell: true  # Block PowerShell through bash

thresholds:
  observation_pending:
    enabled: true
    max_count: 10
    divert_to: observation-triage-cycle
    escape_priorities: [critical]
```

### cycles.yaml

```yaml
nodes:
  backlog:
    cycle: null
    scaffold: []
    exit_criteria: []
  discovery:
    cycle: investigation-cycle
    scaffold:
      - type: investigation
        command: '/new-investigation {id} "{title}"'
    exit_criteria:
      - type: file_status
        field: status
        value: complete
  # ... more nodes ...
```

### components.yaml

```yaml
skills: {}    # Populated by E2-240
agents: {}    # Populated by E2-240
hooks: {}     # Populated by E2-240
```

## Migration (E2-246)

Old config files in `.claude/config/` are deprecated:
- `governance-toggles.yaml` → `haios.yaml` (toggles section)
- `routing-thresholds.yaml` → `haios.yaml` (thresholds section)
- `node-cycle-bindings.yaml` → `cycles.yaml` (nodes section)

Consumers have been updated to use ConfigLoader.

## Related

- **ConfigLoader:** `.claude/lib/config.py`
- **Tests:** `tests/test_config.py`
- **INV-053:** Architecture decision (3-file consolidation)
- **E2-240:** GovernanceLayer will populate components.yaml
