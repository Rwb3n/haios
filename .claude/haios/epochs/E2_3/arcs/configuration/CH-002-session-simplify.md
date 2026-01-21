# generated: 2026-01-20
# System Auto: last updated on: 2026-01-21T17:59:01
# Chapter: Session Simplify

## Definition

**Chapter ID:** CH-002
**Arc:** configuration
**Status:** Complete

---

## Problem

Agent reads 258KB JSON file to get one integer.

Current state:
```
haios-status.json (258KB)
    └── session_delta
            └── current_session: 214
```

Agent parses entire file, navigates nested structure, extracts number.

---

## Agent Need

> "I need to know the session number. Give me just the number."

---

## Requirements

### R1: Single Value File

```
.claude/session
```

Contents: `215`

That's it. One integer. One file.

### R2: Read is Trivial

```bash
cat .claude/session
# Output: 215
```

### R3: Increment is Trivial

```bash
just session-start
# Reads current, increments, writes new
```

### R4: Discoverable

Path declared in haios.yaml discovery section (CH-001).

---

## Interface

**Get session:**
```
Input: None
Output: Integer
```

**Start session:**
```
Input: None
Output: New session number (incremented)
Side effect: .claude/session updated
```

---

## Success Criteria

- [ ] Session number retrievable without parsing JSON
- [ ] `just session-start` works with new file
- [ ] Coldstart uses new file
- [ ] Old haios-status.json session_delta still updated (backward compat)

---

## Migration

1. Create `.claude/session` with current value
2. Update `just session-start` to use new file
3. Update coldstart to read new file
4. Keep session_delta in haios-status.json (other consumers may exist)
5. Eventually deprecate session_delta

---

## Non-Goals

- Session history
- Session metadata
- Multi-agent session handling

---

## Triage Notes

**Selected as first chapter for triage calibration** (Session 215).

Purpose: Test the chapter → work item process on a small, contained scope before applying to larger chapters.

Learnings from triage will feed back into pipeline/CH-007 (Chapter Triage) design.

---

## Triage Result (Session 216)

**Status:** Approved and triaged

| Work Item | Requirements | Blocked By | Description |
|-----------|--------------|------------|-------------|
| WORK-002 | R1, R2 | None | Create `.claude/session` file |
| WORK-003 | R3 | WORK-002 | Update `just session-start` |
| WORK-004 | R3 | WORK-003 | Update coldstart |

**Decisions made:**
- ADR-043: Runtime state at `.claude/` level (not `.claude/haios/`)
- R4 (Discoverable) deferred to CH-001 implementation

---

## Acceptance (Session 218)

**Process:** CH-009 Chapter Acceptance (first application)

### Checklist

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Acceptance criteria satisfied | **PASS** | All 4 criteria verified |
| Requirements variance resolved | **PASS** | Spec updated (see below) |
| Runtime integration exists | **PASS** | coldstart, just session-start, hooks |

### Variance Observed

**Issue:** Implementation updated prose (coldstart.md) instead of code (ContextLoader).

**Root Cause:** Configuration Arc didn't mandate module-first pattern.

**Resolution:** Added "Design Constraints (Session 218 Learning)" section to ARC.md.

**Future Work:** CH-007 (Coldstart Orchestrator) will unify prose and modules.

### Acceptance Record

- **Accepted:** 2026-01-21
- **Session:** 218
- **Process:** CH-009 (first validation)
- **Variance:** Documented in ARC.md Design Constraints
