---
template: implementation_plan
status: complete
date: 2026-02-16
backlog_id: WORK-135
title: "Manifest Auto-Sync Mechanism"
author: Hephaestus
lifecycle_phase: plan
session: 381
version: "1.5"
generated: 2026-02-16
last_updated: 2026-02-16T08:16:00
---
# Implementation Plan: Manifest Auto-Sync Mechanism

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Memory 85021-85024 queried (manifest drift pattern) |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

A `manifest-sync` justfile recipe that regenerates the `components` section of `manifest.yaml` from disk, plus improved test diagnostics that report exactly which items are missing or extra.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `tests/test_manifest.py`, `justfile` |
| Lines of code affected | ~50 | test improvements + new recipe |
| New files to create | 1 | `scripts/manifest_sync.py` |
| Tests to write | 5 | See Tests First section |
| Dependencies | 1 | `ruamel.yaml` (already a dependency) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Standalone script, justfile recipe |
| Risk of regression | Low | Existing test_manifest.py has 3 tests |
| External dependencies | Low | Only filesystem + YAML |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Script | 20 min | High |
| Recipe + integration | 10 min | High |
| **Total** | **45 min** | |

---

## Current State vs Desired State

### Current State

**`tests/test_manifest.py:32-54`** — `test_component_counts_match_file_system`:
```python
# Only checks counts, not which items differ
assert len(manifest["components"]["commands"]) == len(commands), \
    f"Expected {len(commands)} commands, got {len(manifest['components']['commands'])}"
```

**Behavior:** Test catches drift as count mismatch only. When 15 skills were missing (S355), the error said "Expected 33 skills, got 18" — no indication which 15.

**No sync mechanism exists.** The S355 fix was manual: hand-edit manifest.yaml to add 15 entries.

### Desired State

**`scripts/manifest_sync.py`** — standalone sync script:
```python
def sync_manifest(manifest_path, dry_run=False):
    """Scan disk, compute diff, update manifest components."""
```

**`tests/test_manifest.py`** — improved diagnostics:
```python
# Reports exactly which items are missing/extra
assert disk_set == manifest_set, f"Missing: {disk_set - manifest_set}, Extra: {manifest_set - disk_set}"
```

**Behavior:** `just manifest-sync` regenerates components from disk. `just manifest-sync --dry-run` shows diff without writing. Test shows specific missing/extra items.

---

## Tests First (TDD)

### Test 1: Sync detects missing skill
```python
def test_sync_detects_missing_skill(tmp_path):
    """manifest_sync reports skill on disk but not in manifest."""
    # Create a skill dir on disk
    skill_dir = tmp_path / "skills" / "new-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# New Skill")
    # Create manifest missing that skill
    manifest = {"components": {"skills": [], "commands": [], "agents": []}}
    diff = compute_manifest_diff(manifest, skills_dir=tmp_path / "skills",
                                  commands_dir=tmp_path / "commands",
                                  agents_dir=tmp_path / "agents")
    assert "new-skill" in diff["skills"]["missing_from_manifest"]
```

### Test 2: Sync detects extra manifest entry
```python
def test_sync_detects_extra_manifest_entry(tmp_path):
    """manifest_sync reports manifest entry with no disk counterpart."""
    manifest = {"components": {
        "skills": [{"id": "ghost-skill", "source": "skills/ghost-skill/", "category": "utility"}],
        "commands": [], "agents": []
    }}
    (tmp_path / "skills").mkdir()
    (tmp_path / "commands").mkdir()
    (tmp_path / "agents").mkdir()
    diff = compute_manifest_diff(manifest, skills_dir=tmp_path / "skills",
                                  commands_dir=tmp_path / "commands",
                                  agents_dir=tmp_path / "agents")
    assert "ghost-skill" in diff["skills"]["extra_in_manifest"]
```

### Test 3: Sync updates manifest in place
```python
def test_sync_updates_manifest(tmp_path):
    """sync_manifest writes updated manifest with correct entries."""
    manifest_path = tmp_path / "manifest.yaml"
    # Write initial manifest missing a skill
    # Create skill on disk
    # Run sync_manifest(manifest_path, dry_run=False)
    # Re-read manifest
    # Assert new skill present
```

### Test 4: Round-trip stability (ruamel.yaml)
```python
def test_roundtrip_stability(tmp_path):
    """Verify ruamel.yaml round-trip preserves manifest formatting."""
    manifest_path = tmp_path / "manifest.yaml"
    original = "# Comment\nplugin:\n  name: test\ncomponents:\n  skills: []\n  commands: []\n  agents: []\n"
    manifest_path.write_text(original)
    # Load and save without changes
    sync_manifest(manifest_path, dry_run=False)
    assert manifest_path.read_text() == original
```

### Test 5: Improved test shows diff not just count
```python
def test_component_diff_shows_names(self, manifest):
    """Verify drift detection reports specific missing/extra items."""
    # This replaces the old count-only test
    disk_skills = {d.parent.name for d in Path(".claude/skills").glob("*/SKILL.md")}
    manifest_skills = {s["id"] for s in manifest["components"]["skills"]}
    missing = disk_skills - manifest_skills
    extra = manifest_skills - disk_skills
    assert not missing, f"Skills on disk but not in manifest: {missing}"
    assert not extra, f"Skills in manifest but not on disk: {extra}"
```

---

## Detailed Design

### Exact Code Change

**New File:** `scripts/manifest_sync.py`

```python
"""Manifest auto-sync: regenerate components from disk."""
from pathlib import Path
from ruamel.yaml import YAML

def compute_manifest_diff(manifest: dict, *,
                           skills_dir: Path, commands_dir: Path,
                           agents_dir: Path) -> dict:
    """Compare disk state to manifest, return diff per component type."""
    result = {}
    # Skills: dirs containing SKILL.md
    disk_skills = {d.parent.name for d in skills_dir.glob("*/SKILL.md")}
    manifest_skills = {s["id"] for s in manifest.get("components", {}).get("skills", [])}
    result["skills"] = {
        "missing_from_manifest": sorted(disk_skills - manifest_skills),
        "extra_in_manifest": sorted(manifest_skills - disk_skills),
    }
    # Commands: .md files excluding README.md
    disk_cmds = {f.stem for f in commands_dir.glob("*.md") if f.name != "README.md"}
    manifest_cmds = {c["id"] for c in manifest.get("components", {}).get("commands", [])}
    result["commands"] = {
        "missing_from_manifest": sorted(disk_cmds - manifest_cmds),
        "extra_in_manifest": sorted(manifest_cmds - disk_cmds),
    }
    # Agents: .md files excluding README.md
    disk_agents = {f.stem for f in agents_dir.glob("*.md") if f.name != "README.md"}
    manifest_agents = {a["id"] for a in manifest.get("components", {}).get("agents", [])}
    result["agents"] = {
        "missing_from_manifest": sorted(disk_agents - manifest_agents),
        "extra_in_manifest": sorted(manifest_agents - disk_agents),
    }
    return result

def sync_manifest(manifest_path: Path, *, dry_run: bool = False) -> dict:
    """Sync manifest components with disk. Returns diff applied."""
    yaml = YAML()
    yaml.preserve_quotes = True
    with open(manifest_path) as f:
        manifest = yaml.load(f)

    base = manifest_path.parent.parent.parent  # .claude/haios/manifest.yaml -> repo root
    # Resolve component dirs relative to .claude/
    claude_dir = manifest_path.parent.parent  # .claude/haios/ -> .claude/
    diff = compute_manifest_diff(
        manifest,
        skills_dir=claude_dir / "skills",
        commands_dir=claude_dir / "commands",
        agents_dir=claude_dir / "agents",
    )

    if dry_run:
        return diff

    # Add missing items
    for skill_id in diff["skills"]["missing_from_manifest"]:
        manifest["components"]["skills"].append({
            "id": skill_id,
            "source": f"skills/{skill_id}/",
            "category": "utility",  # default, operator can refine
        })
    for cmd_id in diff["commands"]["missing_from_manifest"]:
        manifest["components"]["commands"].append({
            "id": cmd_id, "source": f"commands/{cmd_id}/"
        })
    for agent_id in diff["agents"]["missing_from_manifest"]:
        manifest["components"]["agents"].append({
            "id": agent_id, "source": f"agents/{agent_id}/",
            "required": False,
        })

    # Remove extra items (on disk deleted but still in manifest)
    for component_type in ["skills", "commands", "agents"]:
        extra = set(diff[component_type]["extra_in_manifest"])
        if extra:
            manifest["components"][component_type] = [
                item for item in manifest["components"][component_type]
                if item["id"] not in extra
            ]

    # Sort each section by id for stable output
    for component_type in ["skills", "commands", "agents"]:
        manifest["components"][component_type].sort(key=lambda x: x["id"])

    # Note: Header comment counts (e.g. "# Skills (34 total)") are NOT updated
    # by sync. They are unreliable metadata — the manifest entries ARE the truth.
    # Removing stale counts is a separate cleanup concern.

    # Write back
    if not dry_run:
        with open(manifest_path, "w") as f:
            yaml.dump(manifest, f)

    return diff

if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    manifest_path = Path(".claude/haios/manifest.yaml")
    diff = sync_manifest(manifest_path, dry_run=dry_run)
    has_changes = any(
        diff[ct]["missing_from_manifest"] or diff[ct]["extra_in_manifest"]
        for ct in ["skills", "commands", "agents"]
    )
    if not has_changes:
        print("Manifest is in sync.")
    else:
        for ct in ["skills", "commands", "agents"]:
            for item in diff[ct]["missing_from_manifest"]:
                print(f"  + {ct}: {item}" + (" (would add)" if dry_run else " (added)"))
            for item in diff[ct]["extra_in_manifest"]:
                print(f"  - {ct}: {item}" + (" (would remove)" if dry_run else " (removed)"))
```

### Call Chain Context

```
Operator / CI
    |
    +-> just manifest-sync [--dry-run]
    |       Calls: python scripts/manifest_sync.py [--dry-run]
    |       Reads: .claude/haios/manifest.yaml
    |       Scans: .claude/skills/*/SKILL.md, .claude/commands/*.md, .claude/agents/*.md
    |       Writes: .claude/haios/manifest.yaml (unless dry_run)
    |
    +-> pytest tests/test_manifest.py
            Uses: compute_manifest_diff() for better diagnostics
```

### Function/Component Signatures

```python
def compute_manifest_diff(manifest: dict, *,
                           skills_dir: Path, commands_dir: Path,
                           agents_dir: Path) -> dict:
    """
    Compare disk state to manifest components.

    Args:
        manifest: Parsed manifest.yaml dict
        skills_dir: Path to skills directory
        commands_dir: Path to commands directory
        agents_dir: Path to agents directory

    Returns:
        Dict with keys 'skills', 'commands', 'agents', each containing
        'missing_from_manifest' and 'extra_in_manifest' lists.
    """

def sync_manifest(manifest_path: Path, *, dry_run: bool = False) -> dict:
    """
    Sync manifest.yaml components with disk state.

    Args:
        manifest_path: Path to manifest.yaml
        dry_run: If True, compute diff but don't write

    Returns:
        The diff that was (or would be) applied.
    """
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Standalone script vs hook | Standalone script + recipe | Hooks fire on every Write — too noisy. Recipe is explicit, operator-controlled. Memory 85023 listed both options; script is simpler and less invasive. |
| ruamel.yaml vs pyyaml | ruamel.yaml | Preserves comments and formatting. Already a project dependency. |
| Default category for new skills | `"utility"` | Safe default. Operator can refine. Better than requiring interactive input. |
| Remove extra entries? | Yes, with output | If a skill is deleted from disk but still in manifest, remove it. Print what was removed. |
| Sort after sync | Yes, by id | Stable diff-friendly output. Current manifest is already sorted. |
| Header comment counts | Not updated by sync | Unreliable metadata — manifest entries are the truth. Stale counts (e.g. "34 total" when 33 exist) are a separate cleanup. (Critique A4) |
| Hooks in sync scope | Excluded | Fixed structure (4 event handlers), different format (event+handler, not id+source), changes extremely rarely. (Critique A7) |
| Justfile recipe count | Single recipe with `*args` | Pass-through supports `--dry-run`. Two recipes would be redundant. (Critique A5) |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Manifest already in sync | Print "Manifest is in sync." and exit | Test 3 (no-op case) |
| New skill with no SKILL.md | Not detected (glob requires SKILL.md) | By design — incomplete skills shouldn't be in manifest |
| README.md in commands/agents dirs | Excluded from glob | Existing pattern preserved |
| Empty manifest components | Treated as empty set, all disk items are "missing" | Test 1 |
| Manifest file doesn't exist | Error (intentional — manifest must exist) | N/A |

### Open Questions

None — design is straightforward.

---

## Open Decisions (MUST resolve before implementation)

**No operator decisions required.** The WORK.md lists options but this plan selects Option 1 (sync recipe) + Option 3 (improved test diagnostics), which together satisfy both acceptance criteria.

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_manifest_sync.py` with Tests 1-3
- [ ] Update `tests/test_manifest.py` with Test 4 (diff-based diagnostics)
- [ ] Verify all new tests fail (red)

### Step 2: Implement `scripts/manifest_sync.py`
- [ ] Create `compute_manifest_diff()` function
- [ ] Create `sync_manifest()` function
- [ ] Create `__main__` CLI entry point
- [ ] Tests 1-3 pass (green)

### Step 3: Update existing test diagnostics
- [ ] Replace count-based assertions with set-diff assertions in `test_component_counts_match_file_system`
- [ ] Test 4 passes (green)

### Step 4: Add justfile recipe
- [ ] Add single `manifest-sync *args` recipe to justfile (supports `--dry-run` via pass-through)

### Step 5: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)
- [ ] Demo: `just manifest-sync --dry-run` shows "in sync"

### Step 6: Consumer Verification
- [ ] Verify no existing code depends on old test assertion format
- [ ] WORK.md deliverables all checked

---

## Verification

- [ ] Tests pass
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ruamel.yaml reformats manifest | Medium | Use `preserve_quotes=True` and verify output matches style |
| New skills get wrong category | Low | Default to "utility", print warning for operator to refine |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 381 | 2026-02-16 | - | Plan authored | - |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-135/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Mechanism to detect or prevent manifest drift | [ ] | `just manifest-sync` recipe exists and works |
| Test improvement: show which items are missing, not just count delta | [ ] | `test_component_counts_match_file_system` uses set-diff |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `scripts/manifest_sync.py` | compute_manifest_diff + sync_manifest functions | [ ] | |
| `tests/test_manifest_sync.py` | 3 tests for sync logic | [ ] | |
| `tests/test_manifest.py` | Set-diff diagnostics in count test | [ ] | |
| `justfile` | `manifest-sync` recipe exists | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_manifest_sync.py tests/test_manifest.py -v
just manifest-sync --dry-run
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] **Runtime consumer exists** — `just manifest-sync` recipe calls `scripts/manifest_sync.py`
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** Consumer verification complete

---

## References

- `WORK-135` — Work item
- `.claude/haios/manifest.yaml` — Target manifest
- `tests/test_manifest.py` — Existing test
- Memory: 85021-85024 (manifest drift pattern from S355)
