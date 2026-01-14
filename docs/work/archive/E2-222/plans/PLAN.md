---
template: implementation_plan
id: E2-222
title: Routing Threshold Configuration
status: complete
author: Hephaestus
created: 2025-12-28
milestone: M7c-Governance
priority: medium
effort: small
backlog_id: E2-222
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T20:44:19'
---
# Implementation Plan: E2-222 - Routing Threshold Configuration

## Objective

Create configurable threshold system for routing-gate, starting with observation triage threshold (currently hardcoded at 10).

---

## Current State

- `observations.py` has `DEFAULT_OBSERVATION_THRESHOLD = 10` hardcoded at line 373
- `should_trigger_triage()` accepts threshold parameter but defaults to hardcoded value
- INV-048 designed the configuration schema
- No `.claude/config/routing-thresholds.yaml` exists

---

## Desired State

1. `.claude/config/routing-thresholds.yaml` exists with schema from INV-048
2. `observations.py` reads threshold from config file
3. Fallback to hardcoded default if config missing
4. CLAUDE.md references threshold configuration

---

## Detailed Design

### Config File Schema (from INV-048)

```yaml
# .claude/config/routing-thresholds.yaml
thresholds:
  observation_pending:
    enabled: true
    max_count: 10
    divert_to: observation-triage-cycle
    escape_priorities: [critical]  # Skip threshold for these priorities
```

### Implementation Approach

1. Create config file with schema
2. Add `load_threshold_config()` function to observations.py
3. Modify `get_observation_threshold()` to read from config with fallback
4. Update `should_trigger_triage()` to use config-aware threshold getter

### Code Changes

**observations.py additions:**

```python
def load_threshold_config() -> dict:
    """Load threshold config from routing-thresholds.yaml."""
    config_path = Path(__file__).parent.parent / "config" / "routing-thresholds.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    return {}

def get_observation_threshold() -> int:
    """Get observation pending threshold from config or default."""
    config = load_threshold_config()
    try:
        return config.get("thresholds", {}).get("observation_pending", {}).get("max_count", DEFAULT_OBSERVATION_THRESHOLD)
    except (KeyError, TypeError):
        return DEFAULT_OBSERVATION_THRESHOLD
```

---

## Tests First

1. `test_load_threshold_config_missing_file()` - Returns empty dict when file missing
2. `test_load_threshold_config_valid()` - Returns parsed config
3. `test_get_observation_threshold_default()` - Returns 10 when no config
4. `test_get_observation_threshold_from_config()` - Returns config value

---

## Implementation Steps

1. [ ] Write failing tests for config loading
2. [ ] Create `.claude/config/routing-thresholds.yaml` with schema
3. [ ] Add `load_threshold_config()` and `get_observation_threshold()` to observations.py
4. [ ] Update existing threshold usage to call `get_observation_threshold()`
5. [ ] Run tests - verify pass
6. [ ] Add reference to CLAUDE.md governance section

---

## Ground Truth Verification

| Criterion | Verification |
|-----------|--------------|
| Config file exists | `ls .claude/config/routing-thresholds.yaml` |
| Config loads correctly | `python -c "from observations import load_threshold_config; print(load_threshold_config())"` |
| Threshold reads from config | Change max_count in YAML, verify `get_observation_threshold()` returns new value |
| Tests pass | `pytest tests/test_observations.py -v` |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Config file missing | Low | Low | Fallback to hardcoded default |
| YAML parse error | Low | Med | Try/except with default fallback |
| Path resolution cross-platform | Low | Med | Use Path for cross-platform paths |

---

## Rollback Plan

Delete config file - system falls back to hardcoded default (no breaking change).

---

## Related

- **E2-221:** Routing-gate skill (consumer)
- **E2-223:** Integration into cycle skills (completed)
- **E2-224:** OBSERVE phase threshold check (consumer)
- **INV-048:** Source investigation with schema design
