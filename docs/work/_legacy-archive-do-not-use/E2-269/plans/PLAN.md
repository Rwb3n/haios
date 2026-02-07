---
template: implementation_plan
status: complete
date: 2026-01-04
backlog_id: E2-269
title: manifest.yaml Creation
author: Hephaestus
lifecycle_phase: plan
session: 172
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-05T20:08:41'
---
# Implementation Plan: manifest.yaml Creation

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Create `.claude/haios/manifest.yaml` that declares all HAIOS plugin components (18 commands, 15 skills, 7 agents, 4 hooks) per SECTION-18 schema, enabling future plugin portability.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | No existing files modified |
| Lines of code affected | 0 | New file creation |
| New files to create | 1 | `.claude/haios/manifest.yaml` |
| Tests to write | 3 | Schema validation, component count, YAML parse |
| Dependencies | 0 | Standalone YAML file |

**Component Counts (from file system):**
- Commands: 18 (excluding README.md)
- Skills: 15 directories
- Agents: 7 (excluding README.md)
- Hook handlers: 4 (pre_tool_use, post_tool_use, user_prompt_submit, stop)

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | YAML file only, no code integration yet |
| Risk of regression | Low | No existing behavior to break |
| External dependencies | Low | Just ruamel.yaml for validation |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 10 min | High |
| Create manifest.yaml | 20 min | High |
| Validation and docs | 10 min | High |
| **Total** | 40 min | High |

---

## Current State vs Desired State

### Current State

```
.claude/haios/
├── config/                    # EXISTS: haios.yaml, cycles.yaml, components.yaml
├── manifesto/                 # EXISTS: L0-L7 context files
├── modules/                   # EXISTS: 5 Chariot modules
└── (no manifest.yaml)         # MISSING
```

**Behavior:** Components (commands, skills, agents, hooks) exist only in Claude CLI target paths (`.claude/commands/`, `.claude/skills/`, etc.). No declarative manifest exists to describe what the plugin provides.

**Result:** HAIOS cannot be distributed as a portable plugin. No installer can read what components exist.

### Desired State

```
.claude/haios/
├── manifest.yaml              # NEW: Plugin declaration
├── config/
├── manifesto/
└── modules/
```

**Behavior:** `manifest.yaml` declares all plugin components with metadata, sources, and generation rules per SECTION-18 schema.

**Result:** Future installer can read manifest.yaml to generate target-specific outputs (Claude CLI, Gemini, Cursor, etc.).

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Manifest File Exists and Parses
```python
def test_manifest_exists_and_parses():
    """Verify manifest.yaml exists and is valid YAML."""
    from pathlib import Path
    import yaml

    manifest_path = Path(".claude/haios/manifest.yaml")
    assert manifest_path.exists(), "manifest.yaml must exist"

    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)

    assert isinstance(manifest, dict), "manifest must be a dict"
    assert "plugin" in manifest, "manifest must have 'plugin' section"
    assert "components" in manifest, "manifest must have 'components' section"
```

### Test 2: Component Counts Match Reality
```python
def test_component_counts_match_file_system():
    """Verify manifest declares correct number of components."""
    from pathlib import Path
    import yaml

    with open(".claude/haios/manifest.yaml") as f:
        manifest = yaml.safe_load(f)

    # Count actual files (excluding READMEs)
    commands = [f for f in Path(".claude/commands").glob("*.md") if f.name != "README.md"]
    skills = list(Path(".claude/skills").glob("*/SKILL.md"))
    agents = [f for f in Path(".claude/agents").glob("*.md") if f.name != "README.md"]

    assert len(manifest["components"]["commands"]) == len(commands), f"Expected {len(commands)} commands"
    assert len(manifest["components"]["skills"]) == len(skills), f"Expected {len(skills)} skills"
    assert len(manifest["components"]["agents"]) == len(agents), f"Expected {len(agents)} agents"
    assert len(manifest["components"]["hooks"]) == 4, "Expected 4 hook handlers"
```

### Test 3: Required Fields Present
```python
def test_required_fields_present():
    """Verify manifest has all required fields per SECTION-18."""
    import yaml

    with open(".claude/haios/manifest.yaml") as f:
        manifest = yaml.safe_load(f)

    # Plugin metadata
    assert "name" in manifest["plugin"]
    assert "version" in manifest["plugin"]
    assert "description" in manifest["plugin"]

    # Targets
    assert "targets" in manifest
    assert any(t["id"] == "claude" for t in manifest["targets"])

    # Dependencies
    assert "dependencies" in manifest
    assert "mcp_servers" in manifest["dependencies"]
```

---

## Detailed Design

### New File: `.claude/haios/manifest.yaml`

This is a new file creation (no existing code to modify). The manifest follows SECTION-18-PORTABLE-PLUGIN-SPEC.md schema.

### Full Manifest Content

```yaml
# .claude/haios/manifest.yaml
# Plugin manifest - declares everything HAIOS provides
# Schema: SECTION-18-PORTABLE-PLUGIN-SPEC.md

# Plugin metadata
plugin:
  name: "haios"
  version: "2.0.0"
  description: "Hybrid AI Operating System - Trust Engine for AI agents"
  author: "Ruben Perez"
  license: "Proprietary"
  min_cli_version: "1.0.0"

# Target LLM declarations
targets:
  - id: "claude"
    name: "Claude CLI"
    version: ">=1.0.0"
    output_path: ".claude/"

# Component declarations
components:
  # Commands (18 total)
  commands:
    - id: "close"
      source: "commands/close/"
    - id: "coldstart"
      source: "commands/coldstart/"
    - id: "haios"
      source: "commands/haios/"
    - id: "implement"
      source: "commands/implement/"
    - id: "new-adr"
      source: "commands/new-adr/"
    - id: "new-checkpoint"
      source: "commands/new-checkpoint/"
    - id: "new-handoff"
      source: "commands/new-handoff/"
    - id: "new-investigation"
      source: "commands/new-investigation/"
    - id: "new-plan"
      source: "commands/new-plan/"
    - id: "new-report"
      source: "commands/new-report/"
    - id: "new-work"
      source: "commands/new-work/"
    - id: "ready"
      source: "commands/ready/"
    - id: "reason"
      source: "commands/reason/"
    - id: "schema"
      source: "commands/schema/"
    - id: "status"
      source: "commands/status/"
    - id: "tree"
      source: "commands/tree/"
    - id: "validate"
      source: "commands/validate/"
    - id: "workspace"
      source: "commands/workspace/"

  # Skills (15 total)
  skills:
    - id: "audit"
      source: "skills/audit/"
      category: "utility"
    - id: "checkpoint-cycle"
      source: "skills/checkpoint-cycle/"
      category: "cycle"
    - id: "close-work-cycle"
      source: "skills/close-work-cycle/"
      category: "cycle"
    - id: "design-review-validation"
      source: "skills/design-review-validation/"
      category: "bridge"
    - id: "dod-validation-cycle"
      source: "skills/dod-validation-cycle/"
      category: "bridge"
    - id: "extract-content"
      source: "skills/extract-content/"
      category: "utility"
    - id: "implementation-cycle"
      source: "skills/implementation-cycle/"
      category: "cycle"
    - id: "investigation-cycle"
      source: "skills/investigation-cycle/"
      category: "cycle"
    - id: "memory-agent"
      source: "skills/memory-agent/"
      category: "utility"
    - id: "observation-triage-cycle"
      source: "skills/observation-triage-cycle/"
      category: "cycle"
    - id: "plan-authoring-cycle"
      source: "skills/plan-authoring-cycle/"
      category: "cycle"
    - id: "plan-validation-cycle"
      source: "skills/plan-validation-cycle/"
      category: "bridge"
    - id: "routing-gate"
      source: "skills/routing-gate/"
      category: "bridge"
    - id: "schema-ref"
      source: "skills/schema-ref/"
      category: "utility"
    - id: "work-creation-cycle"
      source: "skills/work-creation-cycle/"
      category: "cycle"

  # Agents (7 total)
  agents:
    - id: "anti-pattern-checker"
      source: "agents/anti-pattern-checker/"
      required: false
    - id: "investigation-agent"
      source: "agents/investigation-agent/"
      required: false
    - id: "preflight-checker"
      source: "agents/preflight-checker/"
      required: true
    - id: "schema-verifier"
      source: "agents/schema-verifier/"
      required: true
    - id: "test-runner"
      source: "agents/test-runner/"
      required: false
    - id: "validation-agent"
      source: "agents/validation-agent/"
      required: false
    - id: "why-capturer"
      source: "agents/why-capturer/"
      required: false

  # Hooks (4 handlers)
  hooks:
    - event: "PreToolUse"
      handler: "hooks/handlers/pre_tool_use.py"
    - event: "PostToolUse"
      handler: "hooks/handlers/post_tool_use.py"
    - event: "UserPromptSubmit"
      handler: "hooks/handlers/user_prompt_submit.py"
    - event: "Stop"
      handler: "hooks/handlers/stop.py"

  # Configuration files
  config:
    - source: "config/"

  # Context files (manifesto)
  context:
    - source: "manifesto/"

# Dependencies
dependencies:
  mcp_servers:
    - name: "haios-memory"
      required: true
      config_path: ".mcp.json"
    - name: "context7"
      required: false
      config_path: ".mcp.json"

  python:
    version: ">=3.10"
    packages:
      - "ruamel.yaml>=0.17"
      - "litellm>=1.0"

# Versioning
versioning:
  strategy: "semver"
  changelog: "CHANGELOG.md"
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Skip `generates` fields | Omit for now | Installer not implemented yet; focus on declaration |
| Use current paths as source | `commands/close/` etc. | These are where source would be if structure was complete |
| Mark only 2 agents required | preflight-checker, schema-verifier | These are MUST per CLAUDE.md governance |
| Categorize skills | cycle/bridge/utility | Matches SECTION-10 taxonomy |
| Version 2.0.0 | Major version | This is Epoch 2 architecture |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| README.md files | Excluded from counts | Test 2 filters by name |
| Empty categories | Allowed (valid YAML) | N/A - all categories populated |
| Missing source dirs | Declaration only | Not validated until installer exists |

### Open Questions

**Q: Should we validate that source paths exist?**

Not for E2-269. The manifest declares intent; source structure migration is E2-267. Premature validation would block progress.

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_manifest.py` with 3 tests from Tests First section
- [ ] Run `pytest tests/test_manifest.py` - verify all 3 fail (manifest doesn't exist yet)

### Step 2: Create manifest.yaml
- [ ] Create `.claude/haios/manifest.yaml` with full content from Detailed Design
- [ ] Test 1 (exists and parses) passes

### Step 3: Verify Component Counts
- [ ] Confirm 18 commands, 15 skills, 7 agents, 4 hooks declared
- [ ] Test 2 (component counts) passes

### Step 4: Verify Required Fields
- [ ] Confirm plugin metadata, targets, dependencies present
- [ ] Test 3 (required fields) passes

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/README.md` to document manifest.yaml
- [ ] **MUST:** Verify README mentions manifest.yaml exists

### Step 6: Consumer Verification
- [ ] N/A - new file, no consumers yet (installer not implemented)

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Source paths don't exist yet | Low | Declaration only; E2-267 handles structure |
| Component count drift | Low | Test 2 verifies against file system |
| Schema deviation from SECTION-18 | Medium | Simplified schema for MVP; full schema in future |
| Installer references deprecated haios_etl | Low | Use new module paths in install hooks |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/manifest.yaml` | Exists, valid YAML, has plugin/components/dependencies | [ ] | |
| `tests/test_manifest.py` | 3 tests exist and pass | [ ] | |
| `.claude/haios/README.md` | **MUST:** Documents manifest.yaml | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_manifest.py -v
# Expected: 3 tests passed
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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- @docs/work/active/INV-052/SECTION-18-PORTABLE-PLUGIN-SPEC.md - Manifest schema specification
- INV-057 - Commands Skills Templates Portability investigation (parent)
- SECTION-10-SKILLS-TAXONOMY.md - Skill category definitions

---
