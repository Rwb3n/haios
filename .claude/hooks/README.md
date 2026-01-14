---
template: readme
status: active
date: 2025-12-21
component: hooks
version: 2.0
owner: HAIOS Plugin
generated: 2025-12-21
last_updated: '2026-01-05T20:51:22'
---
# Claude Code Hooks System (Python-Based)

## Overview

**Purpose:** Automatically execute handlers when specific Claude Code events occur

**Status:** Active - ALL PYTHON (PowerShell archived as of E2-120)

**Quick Facts:**
- **Version:** 2.0 (Python migration complete)
- **Owner:** HAIOS Plugin
- **Dependencies:** Python 3.10+, Claude Code CLI
- **Platform:** Cross-platform (Windows, macOS, Linux)

## Architecture

All hooks route through a single Python dispatcher:

```
Claude Code (hooks)
       |
       v
python hook_dispatcher.py   <- Single entry point
       |
       +-- Routes by hook_event_name:
       |       "UserPromptSubmit" -> hooks/user_prompt_submit.py
       |       "PreToolUse"       -> hooks/pre_tool_use.py
       |       "PostToolUse"      -> hooks/post_tool_use.py
       |       "Stop"             -> hooks/stop.py
       |
       +-- Outputs: text (UserPromptSubmit) or JSON (PreToolUse)
```

## Quick Start

```bash
# Verify hook configuration
cat .claude/settings.local.json | grep hooks

# Test dispatcher manually
echo '{"hook_event_name": "UserPromptSubmit"}' | python .claude/hooks/hook_dispatcher.py
```

## Configuration

**Location:** `.claude/settings.local.json`

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "python .claude/hooks/hook_dispatcher.py"
      }]
    }],
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python .claude/hooks/hook_dispatcher.py"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Edit|MultiEdit|Write",
      "hooks": [{
        "type": "command",
        "command": "python .claude/hooks/hook_dispatcher.py"
      }]
    }],
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python .claude/hooks/hook_dispatcher.py"
      }]
    }]
  }
}
```

---

## Hook Types

### 1. UserPromptSubmit

**Handler:** `hooks/user_prompt_submit.py`

**Purpose:** Injects context into user prompts

| Part | Function | Output |
|------|----------|--------|
| 1 | Date/Time | "Today is Sunday, 2025-12-21 02:30 PM" |
| 1.5 | Context Threshold | Warn when context usage > 80% (E2-210) |
| 2 | Vitals | Milestone, active work, commands, skills |
| 3 | Dynamic Thresholds | APPROACHING/ATTENTION/BOTTLENECK signals (E2-082) |
| 4 | Lifecycle | Warn if creating plan without investigation |
| 5 | RFC 2119 | MUST reminders for governance triggers |

**Dynamic Thresholds (E2-082):**
| Prefix | Trigger | Message |
|--------|---------|---------|
| APPROACHING | Milestone 90-99% | "{name} at {pct}% - {n} items to completion" |
| BOTTLENECK | Blocked items > 3 | "{n} items blocked - review dependencies" |
| ATTENTION | Stale items > 5 | "{n} stale items need review" |
| MOMENTUM | Completed > 3 last session | "Strong momentum from session {n}" |

### 2. PreToolUse

**Handler:** `hooks/pre_tool_use.py`

**Purpose:** Governance enforcement before tool execution

| Check | Action |
|-------|--------|
| Governed paths | Block raw Write to checkpoints, plans, etc. |
| SQL queries | Block direct sqlite3, require schema-verifier |
| Memory refs | Warn on backlog edits without memory_refs |
| Backlog ID uniqueness | Block duplicate backlog_id values (E2-141) |
| Exit gates | Warn on node transitions with unmet criteria (E2-155) |

**Governed Paths:**
- `docs/checkpoints/*.md` -> Use `/new-checkpoint`
- `docs/work/active/*/plans/PLAN.md` (and legacy `docs/plans/PLAN-*.md`) -> Use `/new-plan`
- `docs/handoff/*.md` -> Use `/new-handoff`
- `docs/ADR/ADR-*.md` -> Use `/new-adr`

### 3. PostToolUse

**Handler:** `hooks/post_tool_use.py`

**Purpose:** Post-processing after file operations

| Part | Function | Details |
|------|----------|---------|
| 0 | Error capture | Uses `.claude/lib/error_capture.py` (E2-130) |
| 0.5 | Memory auto-link | Auto-updates WORK.md memory_refs on `ingester_ingest` (E2-238) |
| 1 | Timestamps | **YAML fields** for .md with frontmatter, comments for others |
| 2 | Validation | Uses `.claude/lib/validate.py` |
| 3 | Status refresh | Uses `.claude/lib/status.py` when skills/agents/commands change |
| 4 | Cascade detection | Logs completion events to `haios-events.jsonl` |
| 5 | Cycle logging | Tracks lifecycle_phase changes in plans |
| 6 | Investigation sync | Syncs INV-* file status when archived (E2-140) |
| 7 | Scaffold-on-entry | Suggests scaffold commands on work file node changes (E2-154) |

**Timestamp Format (Session 94 change):**
```yaml
# FOR MARKDOWN WITH YAML FRONTMATTER:
---
template: checkpoint
generated: 2025-12-21           # YAML field (new)
last_updated: 2025-12-21T14:30:00  # YAML field (new)
---

# FOR OTHER FILES (.py, .js, .sql, etc.):
# generated: 2025-12-21
# System Auto: last updated on: 2025-12-21T14:30:00
```

### 4. Stop

**Handler:** `hooks/stop.py`

**Purpose:** ReasoningBank learning extraction at session end

| Action | Description |
|--------|-------------|
| Parse transcript | Extract tool uses and reasoning |
| Identify strategies | Find decision patterns |
| Store to memory | Via `ingester_ingest` |

---

## File Structure

```
.claude/hooks/
├── hook_dispatcher.py      # Main entry point (routes all hooks)
├── hooks/                  # Python handlers
│   ├── user_prompt_submit.py
│   ├── pre_tool_use.py
│   ├── post_tool_use.py
│   └── stop.py
├── memory_retrieval.py     # Memory context injection
├── reasoning_extraction.py # Learning extraction
├── # error_capture.py moved to .claude/lib/ (E2-130)
├── archive/                # DEPRECATED PowerShell (E2-120)
│   ├── UserPromptSubmit.ps1
│   ├── PreToolUse.ps1
│   ├── PostToolUse.ps1
│   ├── Stop.ps1
│   ├── ValidateTemplate.ps1
│   ├── ScaffoldTemplate.ps1
│   ├── UpdateHaiosStatus.ps1
│   └── CascadeHook.ps1
└── tests/                  # Hook tests
```

---

## Library Integration

Hooks use modules from `.claude/lib/`:

| Module | Used By | Purpose |
|--------|---------|---------|
| `validate.py` | PostToolUse | Template validation |
| `status.py` | PostToolUse | Status refresh |
| `database.py` | Stop | Memory storage |
| `retrieval.py` | UserPromptSubmit | Strategy retrieval |
| `node_cycle.py` | PostToolUse | Scaffold-on-entry detection (E2-154) |
| `work_engine.py` | PostToolUse | Memory auto-link (E2-238) - via modules/ |

---

## Migration History

| Session | Change |
|---------|--------|
| 85 | Initial Python hooks via E2-085 |
| 92 | Plugin architecture (E2-120 Phase 0-1) |
| 93 | Python modules: status.py, scaffold.py, validate.py |
| 94 | YAML timestamp injection, PowerShell archived |

---

## Debugging

### View Hook Output
```bash
# Test UserPromptSubmit
echo '{"hook_event_name": "UserPromptSubmit", "user_prompt": "test"}' | python .claude/hooks/hook_dispatcher.py

# Test PostToolUse
echo '{"hook_event_name": "PostToolUse", "tool_name": "Write", "tool_input": {"file_path": "test.md"}}' | python .claude/hooks/hook_dispatcher.py
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Hook not executing | Check `settings.local.json` paths |
| Import errors | Ensure `.claude/lib/` in PYTHONPATH |
| Timestamp not updating | Check file has YAML frontmatter (for .md) |

---

*Version 2.0 | E2-120 Python Migration Complete | 2025-12-21*
