---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-21
backlog_id: WORK-180
title: "Implement ADR-047 Tiered Coldstart"
author: Hephaestus
lifecycle_phase: plan
session: 413
generated: 2026-02-21
last_updated: 2026-02-21T00:17:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-180/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true
  - field: adr_047
    path: "docs/ADR/ADR-047-tiered-coldstart-context-injection.md"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete code blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Implement ADR-047 Tiered Coldstart

---

## Goal

After this plan is complete, `ColdstartOrchestrator` supports three tiers (Full/Light/Minimal) with auto-detection, two new loaders (EpochLoader, OperationsLoader) inject all operational context, and `/coldstart` requires zero manual Read calls.

---

## Open Decisions

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Tier auto-detection | ADR-047 heuristic | ADR-047 | Spec is accepted; no design ambiguity |
| Loader architecture | Config-driven (Loader base) vs standalone | Standalone | EpochLoader and OperationsLoader read multiple files with custom logic (not single-file extraction DSL). Follow SessionLoader/WorkLoader pattern (standalone class with extract/format/load), not IdentityLoader pattern (Loader base + YAML config). |
| --extend implementation | Full vs deferred | Deferred to WORK-181 | --extend requires mid-session re-entry logic (skip orphan detection, skip session-start). Separate work item keeps WORK-180 focused on the core tier pipeline. CLI accepts the flag but prints "not yet implemented". |
| Light tier phases | ADR-047 `work_active_only` vs full `work` | Full `work` loader | ADR-047 specifies `work_active_only` phase ID. Implementing a filtered WorkLoader variant is additional scope. Using the full WorkLoader is a deliberate simplification — Light tier still saves tokens by skipping identity, epoch, operations. Filtered loaders can be added in follow-on work if needed. (Critique A2) |
| Minimal tier phases | ADR-047 `session_number_only` vs full `session` | Full `session` loader | Same rationale. Full SessionLoader adds drift warnings and pending items which are useful even in minimal sessions. Filtered variant deferred. (Critique A2) |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/lib/epoch_loader.py` | CREATE | 1 |
| `.claude/haios/lib/operations_loader.py` | CREATE | 1 |
| `.claude/haios/lib/coldstart_orchestrator.py` | MODIFY | 1 |
| `.claude/haios/config/coldstart.yaml` | MODIFY | 1 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/haios/modules/cli.py` | calls cmd_coldstart() | 280-298 | UPDATE (forward args) |
| `.claude/commands/coldstart.md` | agent instructions | all | UPDATE (remove manual Read steps) |
| `justfile` | recipe coldstart-orchestrator | 213-214 | UPDATE (forward args) |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_epoch_loader.py` | CREATE | Unit tests for EpochLoader |
| `tests/test_operations_loader.py` | CREATE | Unit tests for OperationsLoader |
| `tests/test_coldstart_orchestrator.py` | UPDATE | Tier selection + integration tests |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 4 | 2 loaders + 2 test files |
| Files to modify | 4 | orchestrator + config + cli + justfile |
| Tests to write | ~18 | 6 epoch + 6 operations + 6 orchestrator tier |
| Total blast radius | 8 | Primary + Consumer + Test |

---

## Layer 1: Specification

### Current State

```python
# coldstart_orchestrator.py:34-55 — current loader registry
class ColdstartOrchestrator:
    def __init__(self, config_path=None):
        self.config_path = config_path or DEFAULT_CONFIG
        self._loaders = {
            "identity": IdentityLoader,
            "session": SessionLoader,
            "work": WorkLoader,
        }
        self._load_config()
```

```yaml
# coldstart.yaml — current phases
phases:
  - id: identity
    breathe: true
  - id: session
    breathe: true
  - id: work
    breathe: false
```

**Behavior:** Orchestrator runs 3 loaders (identity, session, work) + epoch validator. Agent then manually Reads EPOCH.md, 4x ARC.md, CLAUDE.md, queries memory refs. 88% of coldstart tokens come from manual Reads.

**Problem:** Agent is informed (WHO + WHAT) but not operational (no HOW). S393/S394: 200k agent failed because it had no knowledge of recipes/tier model.

### Desired State

```python
# coldstart_orchestrator.py — target: 5 loaders, tier selection, CLI args
class ColdstartOrchestrator:
    def __init__(self, config_path=None):
        self.config_path = config_path or DEFAULT_CONFIG
        self._loaders = {
            "identity": IdentityLoader,
            "session": SessionLoader,
            "work": WorkLoader,
            "epoch": EpochLoader,
            "operations": OperationsLoader,
        }
        self._load_config()

    def run(self, tier: str = "auto") -> str:
        # Resolve tier: auto -> detect from checkpoint + staleness
        resolved_tier = self._resolve_tier(tier)
        phases = self._get_phases_for_tier(resolved_tier)
        # Run phases in order with breathe markers
        ...
```

```yaml
# coldstart.yaml — target: tier config + new phases
tier_detection:
  max_age_hours: 24

tiers:
  full:
    phases: [identity, session, work, epoch, operations]
  light:
    phases: [session, work]
  minimal:
    phases: [session]

phases:
  - id: identity
    breathe: true
  - id: session
    breathe: true
  - id: work
    breathe: false
  - id: epoch
    breathe: true
  - id: operations
    breathe: false
```

**Behavior:** Orchestrator auto-detects tier from checkpoint state and staleness, runs only the phases for that tier. EpochLoader injects EPOCH.md + ARC.md context. OperationsLoader injects tier model, recipe catalogue, module paths.

**Result:** Zero manual Reads after coldstart. Agent is operational immediately.

### Tests

#### Test 1: EpochLoader extracts epoch context
- **file:** `tests/test_epoch_loader.py`
- **function:** `test_epoch_loader_extracts_status_and_arcs()`
- **setup:** tmp_path with mock EPOCH.md + 2 ARC.md files, mock haios.yaml pointing to them
- **assertion:** `loader.load()` output contains epoch name, status, arc names, chapter statuses

#### Test 2: EpochLoader handles missing EPOCH.md gracefully
- **file:** `tests/test_epoch_loader.py`
- **function:** `test_epoch_loader_missing_epoch_file()`
- **setup:** tmp_path with haios.yaml pointing to nonexistent EPOCH.md
- **assertion:** `loader.load()` returns warning string, does not raise

#### Test 3: EpochLoader handles missing ARC.md gracefully
- **file:** `tests/test_epoch_loader.py`
- **function:** `test_epoch_loader_missing_arc_file()`
- **setup:** tmp_path with EPOCH.md but one ARC.md missing
- **assertion:** `loader.load()` includes available arc, warns about missing one

#### Test 4: EpochLoader extracts exit criteria
- **file:** `tests/test_epoch_loader.py`
- **function:** `test_epoch_loader_extracts_exit_criteria()`
- **setup:** tmp_path with EPOCH.md containing exit criteria checkboxes
- **assertion:** Output contains checked/unchecked exit criteria

#### Test 5: OperationsLoader injects tier model
- **file:** `tests/test_operations_loader.py`
- **function:** `test_operations_loader_injects_tier_model()`
- **setup:** tmp_path with mock CLAUDE.md containing agent table
- **assertion:** `loader.load()` output contains tier descriptions

#### Test 6: OperationsLoader injects recipe catalogue
- **file:** `tests/test_operations_loader.py`
- **function:** `test_operations_loader_injects_recipe_catalogue()`
- **setup:** tmp_path with mock justfile containing recipes
- **assertion:** Output contains recipe names grouped by category

#### Test 7: OperationsLoader handles missing files gracefully
- **file:** `tests/test_operations_loader.py`
- **function:** `test_operations_loader_missing_files()`
- **setup:** tmp_path with no source files
- **assertion:** `loader.load()` returns warning, does not raise

#### Test 8: OperationsLoader injects common patterns
- **file:** `tests/test_operations_loader.py`
- **function:** `test_operations_loader_injects_patterns()`
- **setup:** tmp_path with mock CLAUDE.md
- **assertion:** Output contains WorkEngine + GovernanceLayer pattern, ConfigLoader pattern

#### Test 9: Tier auto-detection — fresh checkpoint with in-progress work
- **file:** `tests/test_coldstart_orchestrator.py`
- **function:** `test_tier_autodetect_fresh_checkpoint_light()`
- **setup:** Mock checkpoint with pending=[WORK-180], timestamp < 24h old
- **assertion:** `_resolve_tier("auto")` returns "light"

#### Test 10: Tier auto-detection — no checkpoint
- **file:** `tests/test_coldstart_orchestrator.py`
- **function:** `test_tier_autodetect_no_checkpoint_full()`
- **setup:** No checkpoint file
- **assertion:** `_resolve_tier("auto")` returns "full"

#### Test 11: Tier auto-detection — stale checkpoint
- **file:** `tests/test_coldstart_orchestrator.py`
- **function:** `test_tier_autodetect_stale_checkpoint_full()`
- **setup:** Mock checkpoint with timestamp > 24h old
- **assertion:** `_resolve_tier("auto")` returns "full"

#### Test 12: Tier auto-detection — explicit override
- **file:** `tests/test_coldstart_orchestrator.py`
- **function:** `test_tier_explicit_override()`
- **setup:** Any checkpoint state
- **assertion:** `_resolve_tier("minimal")` returns "minimal" regardless of checkpoint

#### Test 13: Orchestrator runs correct phases for each tier
- **file:** `tests/test_coldstart_orchestrator.py`
- **function:** `test_orchestrator_runs_tier_phases()`
- **setup:** Config with tier definitions, mock loaders
- **assertion:** Full runs 5 loaders, Light runs 2, Minimal runs 1

#### Test 14: CLI argument parsing
- **file:** `tests/test_coldstart_orchestrator.py`
- **function:** `test_cli_argparse_tier_argument()`
- **setup:** Mock sys.argv with `--tier full`
- **assertion:** Parsed args have tier="full"

#### Test 15: CLI --extend prints not-yet-implemented
- **file:** `tests/test_coldstart_orchestrator.py`
- **function:** `test_cli_extend_deferred()`
- **setup:** Mock sys.argv with `--extend epoch`
- **assertion:** Output contains "not yet implemented"

#### Test 16: Full tier output contains all phase markers
- **file:** `tests/test_coldstart_orchestrator.py`
- **function:** `test_full_tier_all_phase_markers()`
- **setup:** Config with full tier, mock loaders for all 5
- **assertion:** Output contains [PHASE: IDENTITY], [PHASE: SESSION], [PHASE: WORK], [PHASE: EPOCH], [PHASE: OPERATIONS]

#### Test 17: Light tier skips identity and epoch
- **file:** `tests/test_coldstart_orchestrator.py`
- **function:** `test_light_tier_skips_phases()`
- **setup:** Config with light tier, mock loaders
- **assertion:** Output does NOT contain [PHASE: IDENTITY] or [PHASE: EPOCH]

#### Test 18: Minimal tier runs session only
- **file:** `tests/test_coldstart_orchestrator.py`
- **function:** `test_minimal_tier_session_only()`
- **setup:** Config with minimal tier, mock loaders
- **assertion:** Output contains [PHASE: SESSION], does NOT contain [PHASE: IDENTITY], [PHASE: WORK], [PHASE: EPOCH], [PHASE: OPERATIONS]

### Design

#### File 1 (NEW): `.claude/haios/lib/epoch_loader.py`

```python
"""
Epoch Loader for Coldstart Arc.

WORK-180: Implements EpochLoader per ADR-047.
Reads EPOCH.md + active ARC.md files live at runtime,
extracts/compresses status, chapters, exit criteria.

Follows SessionLoader/WorkLoader pattern (standalone class).

Usage:
    from epoch_loader import EpochLoader
    loader = EpochLoader()
    output = loader.load()  # Returns ~60-80 lines of epoch context
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import re
import yaml
import logging

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
# A6 guard: fail fast if path assumption is wrong (Critique A6)
assert (PROJECT_ROOT / ".claude").exists(), f"PROJECT_ROOT miscalculated: {PROJECT_ROOT}"


class EpochLoader:
    """
    Extract epoch context from EPOCH.md and active ARC.md files.

    Reads source files live every invocation (no caching).
    Epoch content changes frequently — stale context is a silent failure.
    """

    def __init__(
        self,
        haios_config_path: Optional[Path] = None,
        base_path: Optional[Path] = None,
    ):
        self._base_path = base_path or PROJECT_ROOT
        self._haios_config_path = haios_config_path or (
            self._base_path / ".claude" / "haios" / "config" / "haios.yaml"
        )
        self._haios_config = self._load_haios_config()

    def _load_haios_config(self) -> Dict:
        try:
            with open(self._haios_config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Failed to load haios.yaml: {e}")
            return {}

    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        if not content.strip().startswith("---"):
            return {}
        match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError:
                return {}
        return {}

    def _extract_exit_criteria(self, content: str) -> List[str]:
        """Extract exit criteria checkboxes from markdown."""
        criteria = []
        in_exit = False
        for line in content.split("\n"):
            if line.strip().startswith("## Exit Criteria"):
                in_exit = True
                continue
            if in_exit and line.strip().startswith("## "):
                break
            if in_exit and line.strip().startswith("- ["):
                criteria.append(line.strip())
        return criteria

    def _extract_chapter_table(self, content: str) -> List[Dict]:
        """Extract chapter status rows from arc markdown tables."""
        chapters = []
        for line in content.split("\n"):
            line_s = line.strip()
            if not line_s.startswith("|"):
                continue
            if "CH-ID" in line_s or "---" in line_s:
                continue
            cells = [c.strip() for c in line_s.split("|") if c.strip()]
            if len(cells) >= 4 and cells[0].startswith("CH-"):
                chapters.append({
                    "id": cells[0],
                    "title": cells[1],
                    "status": cells[-1],
                })
        return chapters

    def extract(self) -> Dict[str, Any]:
        epoch_cfg = self._haios_config.get("epoch", {})
        result = {
            "epoch_id": epoch_cfg.get("current", "unknown"),
            "epoch_name": "",
            "epoch_status": "",
            "arcs": [],
            "exit_criteria": [],
            "error": None,
        }

        # Read EPOCH.md
        epoch_file = epoch_cfg.get("epoch_file", "")
        if not epoch_file:
            result["error"] = "No epoch_file in haios.yaml"
            return result

        epoch_path = self._base_path / epoch_file
        if not epoch_path.exists():
            result["error"] = f"EPOCH.md not found: {epoch_path}"
            return result

        epoch_content = epoch_path.read_text(encoding="utf-8")
        fm = self._parse_frontmatter(epoch_content)

        # Extract from EPOCH.md content — try bold-prefix pattern first,
        # fall back to frontmatter fields (Critique A5: validation for empty values)
        for line in epoch_content.split("\n"):
            if line.startswith("**Name:**"):
                result["epoch_name"] = line.split("**Name:**")[1].strip()
            if line.startswith("**Status:**"):
                result["epoch_status"] = line.split("**Status:**")[1].strip()

        # A5 fix: fallback to frontmatter if bold-prefix extraction failed
        if not result["epoch_name"]:
            result["epoch_name"] = fm.get("name", "")
        if not result["epoch_status"]:
            result["epoch_status"] = fm.get("status", "")

        # A5 fix: warn if still empty after fallback
        if not result["epoch_name"]:
            logger.warning("Could not extract epoch name from EPOCH.md")
            result["epoch_name"] = "(unknown — check EPOCH.md format)"
        if not result["epoch_status"]:
            logger.warning("Could not extract epoch status from EPOCH.md")
            result["epoch_status"] = "(unknown)"

        result["exit_criteria"] = self._extract_exit_criteria(epoch_content)

        # Read active ARC.md files
        arcs_dir = epoch_cfg.get("arcs_dir", "")
        active_arcs = epoch_cfg.get("active_arcs", [])

        for arc_name in active_arcs:
            arc_path = self._base_path / arcs_dir / arc_name / "ARC.md"
            arc_data = {"name": arc_name, "chapters": [], "error": None}

            if not arc_path.exists():
                arc_data["error"] = f"ARC.md not found: {arc_path}"
                result["arcs"].append(arc_data)
                continue

            arc_content = arc_path.read_text(encoding="utf-8")
            arc_data["chapters"] = self._extract_chapter_table(arc_content)
            result["arcs"].append(arc_data)

        return result

    def format(self, extracted: Dict[str, Any]) -> str:
        lines = ["=== EPOCH CONTEXT ==="]

        if extracted.get("error"):
            lines.append(f"(Epoch loading error: {extracted['error']})")
            return "\n".join(lines)

        lines.append(
            f"Epoch: {extracted['epoch_id']} — {extracted['epoch_name']} "
            f"({extracted['epoch_status']})"
        )

        # Arcs + chapters
        for arc in extracted["arcs"]:
            lines.append(f"\nArc: {arc['name']}")
            if arc.get("error"):
                lines.append(f"  (Warning: {arc['error']})")
                continue
            for ch in arc["chapters"]:
                lines.append(f"  {ch['id']} {ch['title']}: {ch['status']}")

        # Exit criteria
        if extracted["exit_criteria"]:
            lines.append("\nEpoch Exit Criteria:")
            for c in extracted["exit_criteria"]:
                lines.append(f"  {c}")

        return "\n".join(lines)

    def load(self) -> str:
        return self.format(self.extract())


if __name__ == "__main__":
    loader = EpochLoader()
    print(loader.load())
```

#### File 2 (NEW): `.claude/haios/lib/operations_loader.py`

```python
"""
Operations Loader for Coldstart Arc.

WORK-180: Implements OperationsLoader per ADR-047.
Injects operational HOW: tier model, recipe catalogue, module paths,
common patterns. Reads source files live (no caching).

Follows SessionLoader/WorkLoader pattern (standalone class).

Usage:
    from operations_loader import OperationsLoader
    loader = OperationsLoader()
    output = loader.load()  # Returns ~40-60 lines of operational context
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
# A6 guard: fail fast if path assumption is wrong (Critique A6)
assert (PROJECT_ROOT / ".claude").exists(), f"PROJECT_ROOT miscalculated: {PROJECT_ROOT}"

# Key recipes the agent needs to know about, grouped by category
RECIPE_CATEGORIES = {
    "Governance": [
        "scaffold", "validate", "node", "close-work",
        "set-cycle", "clear-cycle",
    ],
    "Rhythm": [
        "session-start", "session-end", "coldstart-orchestrator",
    ],
    "Plan Tree": [
        "ready", "queue", "queue-prioritize", "queue-commit",
    ],
}

# Common patterns every agent should know
COMMON_PATTERNS = [
    "WorkEngine requires GovernanceLayer: WorkEngine(governance=GovernanceLayer())",
    "Path resolution: ConfigLoader.get().get_path('work_item', id='WORK-XXX')",
    "Scaffold: scaffold_template('work_item', output_path=..., backlog_id=..., title=...)",
    "Agent MUST NOT run `just X` directly — use Skill() or Task() wrappers (ADR-045 Tier model)",
]


class OperationsLoader:
    """
    Inject operational context for agent execution.

    Reads source files live at runtime. Stale operational context
    is a silent failure (S393/S394 evidence).
    """

    def __init__(
        self,
        base_path: Optional[Path] = None,
        claude_md_path: Optional[Path] = None,
        justfile_path: Optional[Path] = None,
    ):
        self._base_path = base_path or PROJECT_ROOT
        self._claude_md_path = claude_md_path or (self._base_path / "CLAUDE.md")
        self._justfile_path = justfile_path or (self._base_path / "justfile")

    def _extract_agent_table(self) -> List[str]:
        """Extract agent table from CLAUDE.md."""
        if not self._claude_md_path.exists():
            return ["(CLAUDE.md not found)"]
        content = self._claude_md_path.read_text(encoding="utf-8")

        lines = []
        in_agents = False
        for line in content.split("\n"):
            if "| Agent |" in line and "Model" in line:
                in_agents = True
                lines.append(line.strip())
                continue
            if in_agents:
                if line.strip().startswith("|"):
                    lines.append(line.strip())
                else:
                    break
        return lines if lines else ["(No agent table found)"]

    def _extract_governance_triggers(self) -> List[str]:
        """Extract governance trigger rules from CLAUDE.md."""
        if not self._claude_md_path.exists():
            return []
        content = self._claude_md_path.read_text(encoding="utf-8")

        triggers = []
        in_triggers = False
        for line in content.split("\n"):
            if "### Governance Triggers" in line:
                in_triggers = True
                continue
            if in_triggers and line.strip().startswith("#"):
                break
            if in_triggers and line.strip().startswith("- "):
                triggers.append(line.strip())
        return triggers

    def _extract_recipe_availability(self) -> Dict[str, List[str]]:
        """Check which key recipes exist in justfile."""
        if not self._justfile_path.exists():
            return {}
        content = self._justfile_path.read_text(encoding="utf-8")

        available = {}
        for category, recipes in RECIPE_CATEGORIES.items():
            found = []
            for recipe in recipes:
                # Match recipe definition: recipe_name: or recipe_name arg:
                pattern = rf"^{re.escape(recipe)}(?:\s|\:)"
                if re.search(pattern, content, re.MULTILINE):
                    found.append(recipe)
            if found:
                available[category] = found
        return available

    def extract(self) -> Dict[str, Any]:
        return {
            "tier_model": [
                "Tier 1 (Commands): Operator types /command in chat",
                "Tier 2 (Skills+Agents): Agent uses Skill() or Task()",
                "Tier 3 (Recipes): Internal — called by Tier 1/2 only",
                "Rule: Agent MUST NOT run `just X` directly",
            ],
            "recipes": self._extract_recipe_availability(),
            "agent_table": self._extract_agent_table(),
            "governance_triggers": self._extract_governance_triggers(),
            "common_patterns": COMMON_PATTERNS,
        }

    def format(self, extracted: Dict[str, Any]) -> str:
        lines = ["=== OPERATIONS ==="]

        # Tier model
        lines.append("\nEntry Point Tiers (ADR-045):")
        for t in extracted["tier_model"]:
            lines.append(f"  {t}")

        # Recipe catalogue
        lines.append("\nAvailable Recipes (Tier 3 — call via skills, not directly):")
        for category, recipes in extracted["recipes"].items():
            lines.append(f"  {category}: {', '.join(recipes)}")

        # Agent table
        lines.append("\nAgents:")
        for line in extracted["agent_table"]:
            lines.append(f"  {line}")

        # Governance triggers
        if extracted["governance_triggers"]:
            lines.append("\nGovernance Triggers (MUST):")
            for t in extracted["governance_triggers"]:
                lines.append(f"  {t}")

        # Common patterns
        lines.append("\nCommon Patterns:")
        for p in extracted["common_patterns"]:
            lines.append(f"  {p}")

        return "\n".join(lines)

    def load(self) -> str:
        return self.format(self.extract())


if __name__ == "__main__":
    loader = OperationsLoader()
    print(loader.load())
```

#### File 3 (MODIFY): `.claude/haios/lib/coldstart_orchestrator.py`

**Changes:**
1. Import EpochLoader and OperationsLoader
2. Add them to `_loaders` registry
3. Add `run(tier="auto")` parameter
4. Add `_resolve_tier()` and `_get_phases_for_tier()` methods
5. Add `_get_checkpoint_age_hours()` helper
6. Update `__main__` with argparse

**Key additions:**

```python
import sys
import re
import time
from epoch_loader import EpochLoader
from operations_loader import OperationsLoader

# In __init__:
self._loaders = {
    "identity": IdentityLoader,
    "session": SessionLoader,
    "work": WorkLoader,
    "epoch": EpochLoader,
    "operations": OperationsLoader,
}

def _find_latest_checkpoint(self) -> Optional[Path]:
    """Find most recent checkpoint file (reuses SessionLoader pattern)."""
    from config import ConfigLoader
    checkpoint_dir = Path(__file__).parent.parent.parent.parent / ConfigLoader.get().get_path("checkpoints")
    if not checkpoint_dir.exists():
        return None
    checkpoints = [cp for cp in checkpoint_dir.glob("*.md") if cp.name != "README.md"]
    if not checkpoints:
        return None
    import re as _re
    def _session_number(path: Path) -> tuple:
        session_match = _re.search(r"SESSION-(\d+)", path.name, _re.IGNORECASE)
        session_num = int(session_match.group(1)) if session_match else 0
        date_match = _re.match(r"(\d{4}-\d{2}-\d{2}-\d{2})", path.name)
        date_prefix = date_match.group(1) if date_match else ""
        return (session_num, date_prefix, path.name)
    return max(checkpoints, key=_session_number)

def _get_checkpoint_age_hours(self) -> Optional[float]:
    """Get age of latest checkpoint in hours from file mtime."""
    cp = self._find_latest_checkpoint()
    if cp is None:
        return None
    mtime = cp.stat().st_mtime
    age_seconds = time.time() - mtime
    return age_seconds / 3600.0

def _has_pending_work(self) -> bool:
    """Check if latest checkpoint has pending work items. (Critique A1 fix)"""
    cp = self._find_latest_checkpoint()
    if cp is None:
        return False
    content = cp.read_text(encoding="utf-8")
    if not content.strip().startswith("---"):
        return False
    match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False
    try:
        fm = yaml.safe_load(match.group(1)) or {}
        return bool(fm.get("pending", []))
    except yaml.YAMLError:
        return False

def _resolve_tier(self, tier: str) -> str:
    """Resolve tier from explicit or auto-detection."""
    if tier != "auto":
        return tier
    # Auto-detection heuristic (ADR-047):
    # 1. Stale checkpoint (>max_age_hours) -> full
    # 2. Fresh checkpoint with pending work -> light
    # 3. Default -> full
    age = self._get_checkpoint_age_hours()
    max_age = self.config.get("tier_detection", {}).get("max_age_hours", 24)
    if age is None or age > max_age:
        return "full"
    if self._has_pending_work():
        return "light"
    return "full"

def _get_phases_for_tier(self, tier: str) -> list:
    """Get phase list for resolved tier."""
    tiers = self.config.get("tiers", {})
    tier_def = tiers.get(tier, {})
    phase_ids = tier_def.get("phases", [])
    if not phase_ids:
        # Fallback to all phases in config
        return self.config.get("phases", [])
    # Build phase entries from phase_ids
    all_phases = {p["id"]: p for p in self.config.get("phases", [])}
    return [all_phases[pid] for pid in phase_ids if pid in all_phases]

# Updated run():
def run(self, tier: str = "auto") -> str:
    output = []
    # PHASE 0: Orphan detection (E2-236)
    recovery_result = self._check_for_orphans()
    if recovery_result:
        output.append("[PHASE: RECOVERY]")
        output.append(recovery_result)
        output.append("\n[BREATHE]\n")

    # Tier resolution (ADR-047)
    resolved_tier = self._resolve_tier(tier)
    phases = self._get_phases_for_tier(resolved_tier)

    for phase in phases:
        # ... same phase loop as current, using resolved phases ...
        pass

    # Epoch validation (WORK-154) — only for full tier
    if resolved_tier == "full":
        validation_output = self._run_epoch_validation()
        if validation_output:
            output.append("[PHASE: VALIDATION]")
            output.append(validation_output)
            output.append("\n[BREATHE]\n")

    output.append("[READY FOR SELECTION]")
    return "\n".join(output)

# Updated __main__ (with argparse):
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Coldstart Orchestrator")
    parser.add_argument("--tier", default="auto",
                        choices=["auto", "full", "light", "minimal"])
    parser.add_argument("--extend", nargs="*", default=None,
                        help="Extend with additional phases (not yet implemented)")
    args = parser.parse_args()
    if args.extend is not None:
        print("[EXTEND] --extend is not yet implemented. Use --tier instead.")
        sys.exit(0)
    orch = ColdstartOrchestrator()
    print(orch.run(tier=args.tier))
```

#### File 3b (MODIFY): `.claude/haios/modules/cli.py` — cmd_coldstart arg forwarding (Critique A4 fix)

**Current Code (cli.py:280-298):**
```python
def cmd_coldstart() -> int:
    ...
    orch = ColdstartOrchestrator()
    ...
    print(orch.run())
    return 0
```

**Target Code:**
```python
def cmd_coldstart(tier: str = "auto") -> int:
    """Run coldstart orchestrator with tier selection."""
    import sys
    import io
    from coldstart_orchestrator import ColdstartOrchestrator

    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    orch = ColdstartOrchestrator()
    print(orch.run(tier=tier))
    return 0
```

**Dispatch block (cli.py:~720):**
```python
elif cmd == "coldstart":
    tier = "auto"
    if "--tier" in sys.argv:
        idx = sys.argv.index("--tier")
        if idx + 1 < len(sys.argv):
            tier = sys.argv[idx + 1]
    return cmd_coldstart(tier=tier)
```

#### File 4 (MODIFY): `.claude/haios/config/coldstart.yaml`

**Target content:**
```yaml
# Coldstart phase orchestration config per CH-007 spec
# WORK-180: Tiered coldstart per ADR-047

tier_detection:
  max_age_hours: 24

tiers:
  full:
    phases: [identity, session, work, epoch, operations]
  light:
    phases: [session, work]
  minimal:
    phases: [session]

phases:
  - id: identity
    breathe: true
  - id: session
    breathe: true
  - id: work
    breathe: false
  - id: epoch
    breathe: true
  - id: operations
    breathe: false
```

### Call Chain

```
/coldstart (command, Tier 1)
    |
    +-> coldstart.md (skill instructions)
    |       Calls: just coldstart-orchestrator [--tier X]
    |
    +-> justfile: coldstart-orchestrator recipe
    |       Calls: python cli.py coldstart [--tier X]
    |
    +-> cli.py: cmd_coldstart()
    |       Calls: ColdstartOrchestrator().run(tier=X)
    |
    +-> ColdstartOrchestrator.run(tier)
            |
            +-> _resolve_tier(tier)     # auto-detect or passthrough
            +-> _get_phases_for_tier()  # config lookup
            +-> Phase loop:
                +-> IdentityLoader.load()      # [PHASE: IDENTITY]
                +-> SessionLoader.load()       # [PHASE: SESSION]
                +-> WorkLoader.load()          # [PHASE: WORK]
                +-> EpochLoader.load()         # [PHASE: EPOCH]      <-- NEW
                +-> OperationsLoader.load()    # [PHASE: OPERATIONS] <-- NEW
            +-> EpochValidator.validate()      # [PHASE: VALIDATION]
            +-> "[READY FOR SELECTION]"
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Standalone loaders (not Loader base) | SessionLoader pattern | EpochLoader reads multiple files with custom extraction logic (chapter tables, exit criteria). The Loader base is designed for single-file section extraction via YAML DSL. Same reasoning as SessionLoader. |
| No caching | Read files every invocation | Epoch content changes frequently (arc status, chapter progress). Stale context replicates S393/S394 failure silently (ADR-047 critique finding A3). Coldstart runs once per session — cost is acceptable. |
| --extend deferred | Stub in CLI, not implemented | Requires skip-orphan-detection logic and mid-session re-entry. Separate work item keeps scope manageable. |
| Light tier = session + work | Not session only | Agent continuing prior work needs queue state and pending items to pick up where it left off. |
| Minimal tier = session only | Just session number | For housekeeping: agent only needs to know what session it is. Identity, epoch, operations all available via --extend if needed. |
| Checkpoint age from file mtime | Not from frontmatter date | Simpler, no YAML parsing needed for staleness check. mtime reflects actual last-write which is what matters. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| Missing EPOCH.md | EpochLoader returns warning string | Test 2 |
| Missing one ARC.md | Include available arcs, warn about missing | Test 3 |
| Missing CLAUDE.md | OperationsLoader returns warning for that section | Test 7 |
| Missing justfile | OperationsLoader skips recipe catalogue | Test 7 |
| No checkpoint (first session) | _resolve_tier returns "full" | Test 10 |
| Stale checkpoint (>24h) | _resolve_tier returns "full" | Test 11 |
| Unknown tier name in config | Fall back to all phases | Handled in _get_phases_for_tier |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| EpochLoader output too large | M | Extract only status tables and exit criteria, not full content. ~60-80 lines target. |
| OperationsLoader recipes list becomes stale | L | Read justfile live every time. No hardcoded recipe names in output — only categories are hardcoded. |
| Light tier insufficient for some work | M | --extend escape hatch (deferred). Agent can always re-run /coldstart full. |
| Existing tests break with new run(tier=) signature | H | run() defaults to tier="auto", auto resolves to "full" when no checkpoint — backward compatible. |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests — EpochLoader (RED)
- **input:** Layer 0 inventory complete, Layer 1 test specs 1-4 defined
- **action:** Create `tests/test_epoch_loader.py` with tests 1-4
- **output:** Test file exists, all 4 tests fail (no epoch_loader.py yet)
- **verify:** `pytest tests/test_epoch_loader.py -v 2>&1 | grep -c "FAILED\|ERROR"` equals 4

### Step 2: Implement EpochLoader (GREEN)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Create `.claude/haios/lib/epoch_loader.py` from Layer 1 Design File 1
- **output:** All 4 EpochLoader tests pass
- **verify:** `pytest tests/test_epoch_loader.py -v` exits 0, `4 passed` in output

### Step 3: Write Failing Tests — OperationsLoader (RED)
- **input:** Step 2 complete
- **action:** Create `tests/test_operations_loader.py` with tests 5-8
- **output:** Test file exists, all 4 tests fail
- **verify:** `pytest tests/test_operations_loader.py -v 2>&1 | grep -c "FAILED\|ERROR"` equals 4

### Step 4: Implement OperationsLoader (GREEN)
- **input:** Step 3 complete (tests exist and fail)
- **action:** Create `.claude/haios/lib/operations_loader.py` from Layer 1 Design File 2
- **output:** All 4 OperationsLoader tests pass
- **verify:** `pytest tests/test_operations_loader.py -v` exits 0, `4 passed` in output

### Step 5: Write Failing Tests — Tier Selection (RED)
- **input:** Step 4 complete
- **action:** Add tests 9-18 to `tests/test_coldstart_orchestrator.py`
- **output:** New tests fail (no tier methods yet)
- **verify:** `pytest tests/test_coldstart_orchestrator.py -v -k "tier"` shows failures

### Step 6: Implement Tier Selection + Integrate Loaders (GREEN)
- **input:** Step 5 complete
- **action:** Modify `coldstart_orchestrator.py`: add imports, loaders, tier methods, update run(). Note (Critique A3): existing `test_default_config_fallback_when_missing` asserts `len(phases) == 3`. Keep the hardcoded fallback at 3 phases (identity, session, work) — the fallback is for missing config, not for tiered config. New loaders are config-driven, not hardcoded-fallback.
- **output:** All tier tests pass, existing tests still pass
- **verify:** `pytest tests/test_coldstart_orchestrator.py -v` exits 0 (includes existing Test 6)

### Step 7: Update Config
- **input:** Step 6 complete
- **action:** Update `coldstart.yaml` with tier_detection, tiers, new phases
- **output:** Config has tier definitions
- **verify:** `python -c "import yaml; c=yaml.safe_load(open('.claude/haios/config/coldstart.yaml')); assert 'tiers' in c; assert 'tier_detection' in c; print('OK')"` prints OK

### Step 8: Update CLI + Justfile
- **input:** Step 7 complete
- **action:** Update cli.py cmd_coldstart() to forward tier arg. Update justfile recipe to forward args.
- **output:** `just coldstart-orchestrator --tier full` works
- **verify:** `python .claude/haios/modules/cli.py coldstart --tier minimal 2>&1 | head -5` contains [PHASE: SESSION]

### Step 9: Update coldstart.md
- **input:** Step 8 complete
- **action:** Rewrite `.claude/commands/coldstart.md` — remove Steps 3-5 (manual Reads), add tier argument docs
- **output:** coldstart.md has zero manual Read instructions
- **verify:** `grep -cE "Read \`.*EPOCH|Read \`.*ARC\.md|Read \`.*CLAUDE\.md" .claude/commands/coldstart.md` returns 0 (Step 1 Read haios.yaml preserved per ADR-047; only operational Reads eliminated)

### Step 10: Full Integration Test
- **input:** Step 9 complete
- **action:** Run full coldstart with new loaders, verify output
- **output:** Output contains all 5 phase markers + epoch context + operations context
- **verify:** `just coldstart-orchestrator --tier full 2>&1 | grep -c "PHASE:"` >= 5

### Step 11: Token Savings Measurement (Critique A7)
- **input:** Step 10 complete
- **action:** Compare baseline manual Read line counts vs new loader output line counts. Baseline: EPOCH.md ~230 lines + 4x ARC.md ~272 lines + CLAUDE.md ~159 lines = ~661 lines of manual Reads eliminated. Measure new loader output: `just coldstart-orchestrator --tier full 2>&1 | wc -l`. Record ratio in WORK.md History section.
- **output:** Token savings ratio documented
- **verify:** New loader output < 200 lines (target: ~140-180 lines for epoch + operations combined, vs 661 manual Read lines = ~75% reduction)

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_epoch_loader.py -v` | 4 passed, 0 failed |
| `pytest tests/test_operations_loader.py -v` | 4 passed, 0 failed |
| `pytest tests/test_coldstart_orchestrator.py -v` | All passed (existing + ~10 new), 0 failed |
| `pytest tests/ -v -k "loader or coldstart"` | 0 new failures |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| EpochLoader class | `python -c "import sys; sys.path.insert(0,'.claude/haios/lib'); from epoch_loader import EpochLoader; print('OK')"` | OK |
| OperationsLoader class | `python -c "import sys; sys.path.insert(0,'.claude/haios/lib'); from operations_loader import OperationsLoader; print('OK')"` | OK |
| Tier selection logic | `python .claude/haios/modules/cli.py coldstart --tier minimal 2>&1 | grep "SESSION"` | 1+ match |
| CLI argparse + --extend | `python .claude/haios/lib/coldstart_orchestrator.py --extend epoch 2>&1` | Contains "not yet implemented" |
| Justfile forwards args | `just coldstart-orchestrator --tier full 2>&1 | grep "EPOCH"` | 1+ match |
| coldstart.yaml tiers | `python -c "import yaml; c=yaml.safe_load(open('.claude/haios/config/coldstart.yaml')); print(len(c['tiers']))"` | 3 |
| coldstart.md no operational Reads | `grep -cE "Read \\\`.*EPOCH\|Read \\\`.*ARC\\.md\|Read \\\`.*CLAUDE\\.md" .claude/commands/coldstart.md` | 0 |
| Unit tests EpochLoader | `pytest tests/test_epoch_loader.py -v --tb=short` | 4 passed |
| Unit tests OperationsLoader | `pytest tests/test_operations_loader.py -v --tb=short` | 4 passed |
| Integration tier tests | `pytest tests/test_coldstart_orchestrator.py -v -k "tier" --tb=short` | All passed |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| Orchestrator imports new loaders | `grep "EpochLoader\|OperationsLoader" .claude/haios/lib/coldstart_orchestrator.py` | 2+ matches |
| CLI forwards tier arg | `grep "tier" .claude/haios/modules/cli.py` | 1+ match |
| No stale 3-phase fallback | `grep "identity.*session.*work" .claude/haios/lib/coldstart_orchestrator.py` | 0 matches (replaced by config-driven tiers) |
| coldstart.md no operational Reads | `grep -cE "Read \\\`.*EPOCH\|Read \\\`.*ARC\\.md\|Read \\\`.*CLAUDE\\.md" .claude/commands/coldstart.md` | 0 |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Steps 2, 4, 6 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists (orchestrator imports both loaders)
- [ ] No stale references (Consumer Integrity table above)
- [ ] coldstart.md updated (zero manual Reads)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- @docs/ADR/ADR-047-tiered-coldstart-context-injection.md (design spec)
- @docs/work/active/WORK-180/WORK.md (work item)
- @docs/work/active/WORK-162/WORK.md (parent design)
- @.claude/haios/lib/coldstart_orchestrator.py (target modification)
- @.claude/haios/lib/identity_loader.py (sibling pattern)
- @.claude/haios/lib/session_loader.py (sibling pattern)
- @docs/ADR/ADR-045-three-tier-entry-point-architecture.md (tier model)
- Memory: 85923 (minimum viable context contract), 87131 (ADR-047 decision)

---
