---
template: investigation
status: complete
date: 2025-12-16
backlog_id: E2-085
title: "Investigation: Hook Migration: PowerShell to Python"
author: Hephaestus
session: 80
lifecycle_phase: conclude
spawned_by: Session-80-operator-question
related: [E2-076d, E2-037, E2-007, E2-120]
version: "1.2"
closed_session: 102
closure_note: "SUPERSEDED by E2-120 (Sessions 91-94). Full Python migration completed. All PowerShell archived."
generated: 2025-12-23
last_updated: 2025-12-23T10:33:46
---
# Investigation: Hook Migration: PowerShell to Python

@docs/README.md
@docs/epistemic_state.md
@CLAUDE.md

---

## Context

PowerShell hooks suffer from recurring issues when invoked through Claude Code's bash-based execution layer:

| Issue | Frequency | Example |
|-------|-----------|---------|
| Variable mangling | Every inline PS | `$_` becomes `extglob.Line` |
| Escaping complexity | Development | `$variable` eaten by bash |
| Windows-only | Architecture | No Linux/Mac support |
| JSON handling | Frequent | ConvertFrom-Json + PSObject dance |
| Verbose syntax | Every hook | ~500 lines across 4 hooks |

**Documented patterns:**
- CLAUDE.md: "MUST NOT use `$_`, `$Matches`, etc. in inline PowerShell through bash"
- epistemic_state.md: "PowerShell-Bash Interop: Recurring pattern where `$_` and `$variable` get mangled. Sessions 49, 50."

**Current state:**
- 4 hooks: UserPromptSubmit, PreToolUse, PostToolUse, Stop
- ~500 lines PowerShell total
- UserPromptSubmit most complex (~150 lines with Vitals, Lifecycle, RFC2119)
- Stop already calls Python (reasoning_extraction.py)
- memory_retrieval.py is Python (currently disabled but exists)

---

## Objective

Determine the optimal migration path from PowerShell to a cross-platform, escaping-safe language for HAIOS hooks.

---

## Scope

### In Scope
- Evaluate language alternatives (Python, Node.js, compiled)
- Assess migration effort per hook
- Design hook architecture (dispatcher pattern vs individual scripts)
- Cross-platform wrapper approach
- Compatibility with Claude Code hook system

### Out of Scope
- Rewriting haios_etl (already Python, stays Python)
- Hook functionality changes (preserve current behavior)
- Performance optimization beyond acceptable thresholds

---

## Hypotheses

1. **H1:** Python is optimal because it's already in the project, cross-platform, and handles JSON trivially
2. **H2:** Startup time penalty (~200-300ms) is acceptable since hooks already tolerate multi-second delays
3. **H3:** A single dispatcher entry point is cleaner than 4 separate scripts
4. **H4:** Thin shell wrappers can abstract OS differences

---

## Options Analysis

### Option A: Python (Recommended)

**Architecture:**
```
Claude Code
    |
    v
wrapper.sh/.ps1 (thin, OS-specific)
    |
    v
hook_dispatcher.py (single entry point)
    |
    +-- user_prompt_submit()
    +-- pre_tool_use()
    +-- post_tool_use()
    +-- stop()
```

**Pros:**
- Already in project (haios_etl, memory_retrieval.py)
- Cross-platform native
- JSON: `json.loads(stdin)` - done
- Can import haios_etl modules for DB access
- No escaping issues
- Clean, readable code

**Cons:**
- Startup time ~200-300ms per invocation
- Requires Python installed (already required)

**Effort:** Medium (~2-3 sessions)

### Option B: Node.js

**Pros:**
- Fast startup (~50ms)
- Native JSON
- Cross-platform
- Claude Code is JS-based

**Cons:**
- Another runtime dependency
- No existing codebase to leverage
- Would need separate DB access layer

**Effort:** Medium

### Option C: Compiled (Rust/Go)

**Pros:**
- Fastest startup
- Single binary, no runtime
- True cross-platform

**Cons:**
- Overkill for hooks
- Compile step in dev workflow
- Can't easily call haios_etl Python code
- Higher development complexity

**Effort:** High

### Option D: Hybrid (Gradual Migration)

**Pros:**
- No big-bang rewrite
- Already proven (memory_retrieval.py, reasoning_extraction.py)
- Migrate hot spots first

**Cons:**
- Two languages to maintain
- Inconsistent codebase

**Effort:** Low per-hook, but ongoing maintenance cost

---

## Investigation Steps

### Phase 1: Architecture Design
1. [x] Document current hook inventory and complexity
2. [x] Evaluate language options (Python, Node.js, compiled)
3. [x] Recommend architecture (Python dispatcher)
4. [ ] Design dispatcher interface (how hooks receive/return data)
5. [ ] Design wrapper strategy (OS abstraction)

### Phase 2: Proof of Concept
6. [ ] Create `hook_dispatcher.py` skeleton
7. [ ] Implement UserPromptSubmit in Python (most complex)
8. [ ] Create wrapper scripts (.sh + .ps1)
9. [ ] Test vitals injection works
10. [ ] Test lifecycle guidance works
11. [ ] Test RFC2119 reminders work

### Phase 3: Full Migration
12. [ ] Migrate PreToolUse
13. [ ] Migrate PostToolUse
14. [ ] Migrate Stop (simplest - already calls Python)
15. [ ] Update settings.local.json configuration
16. [ ] Verify all functionality preserved

### Phase 4: Cleanup
17. [ ] Archive PowerShell hooks
18. [ ] Update CLAUDE.md documentation
19. [ ] Update hooks README
20. [ ] Store migration learnings to memory

---

## Findings

### Current Hook Inventory

| Hook | Lines | Complexity | Python Deps |
|------|-------|------------|-------------|
| UserPromptSubmit.ps1 | ~150 | High | haios-status-slim.json read |
| PreToolUse.ps1 | ~120 | Medium | None |
| PostToolUse.ps1 | ~100 | Medium | None |
| Stop.ps1 | ~50 | Low | Already calls reasoning_extraction.py |
| **Total** | ~420 | - | - |

### Startup Time Analysis

Current hooks already tolerate delays:
- Memory retrieval had 8s timeout (Session 35)
- Vitals injection acceptable at ~100ms
- Python startup (~250ms) is well within acceptable range

### Claude Code Hook Interface

Hooks receive JSON on stdin:
```json
{
  "session_id": "...",
  "transcript_path": "...",
  "cwd": "...",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "user's prompt text"
}
```

Hooks output text to stdout (injected as context).

This interface is language-agnostic - Python can handle it trivially.

---

## Recommendation

**Proceed with Option A: Python migration**

Rationale:
1. Already proven in project (haios_etl, existing Python scripts)
2. Clean JSON handling eliminates escaping bugs
3. Cross-platform without wrapper complexity
4. Can leverage haios_etl for database access
5. Startup penalty is acceptable

---

## Spawned Work Items

- [x] E2-085: Hook System Migration (PowerShell to Python) - backlog item created

---

## Expected Deliverables

- [x] Options analysis document (this investigation)
- [x] Recommendation (Python)
- [ ] Implementation plan (PLAN-E2-085)
- [ ] Migration execution
- [ ] Memory storage (concepts)

---

## References

- CLAUDE.md: PowerShell-Bash escaping warnings
- epistemic_state.md: Known behavioral patterns
- `.claude/hooks/UserPromptSubmit.ps1`: Current implementation
- `.claude/hooks/PreToolUse.ps1`: Current implementation
- `.claude/hooks/PostToolUse.ps1`: Current implementation
- `.claude/hooks/Stop.ps1`: Current implementation
- `.claude/hooks/memory_retrieval.py`: Existing Python hook script
- `.claude/hooks/reasoning_extraction.py`: Existing Python hook script

---
