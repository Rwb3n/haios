# generated: 2026-01-20
# System Auto: last updated on: 2026-01-20T21:58:58
# Chapter: Session Simplify

## Definition

**Chapter ID:** CH-002
**Arc:** configuration
**Status:** Planned

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
