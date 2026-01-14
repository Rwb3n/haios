---
template: implementation_plan
status: complete
date: 2025-12-07
backlog_id: PLAN-FILE-LIFECYCLE
title: "File Lifecycle and Status Automation"
author: Hephaestus
version: "1.0"
session: 39
priority: high
lifecycle_phase: complete
completed_session: 48
completion_note: "Phase 1-2 complete. Phase 3 (Memory Integration) moved to E2-021/E2-008."
---
# generated: 2025-12-07
# System Auto: last updated on: 2025-12-10 22:04:39
# Implementation Plan: File Lifecycle and Status Automation

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Implement two interconnected systems:
1. **haios-status.json Auto-Update** - Eliminate manual status file maintenance
2. **File Lifecycle Model** - Standardize document progression through phases with governance

---

## Problem Statement

**Current Pain Points:**
1. `haios-status.json` is manually updated, causing drift from reality
2. No standardized lifecycle for documents (investigation ? plan ? execution)
3. Template validation schema is out of sync with actual template types
4. Self-awareness mechanisms (/coldstart, /haios) show stale data

**Why This Matters:**
- Agents lose trust in status data when it's stale
- No clear "what happens next" guidance after creating documents
- Governance can't enforce lifecycle rules without a model

---

## Architecture Overview

### System Context Diagram

```
+-------------------------------------------------------------------------+
�                           HAIOS GOVERNANCE LAYER                         �
+-------------------------------------------------------------------------�
�                                                                          �
�  +--------------+    +--------------+    +--------------+               �
�  �  /coldstart  �    �    /haios    �    �   /status    �               �
�  �   Command    �    �   Command    �    �   Command    �               �
�  +--------------+    +--------------+    +--------------+               �
�         �                   �                   �                        �
�         +-------------------+-------------------+                        �
�                             ?                                            �
�                 +-----------------------+                                �
�                 �  UpdateHaiosStatus.ps1 �?---- TRIGGER                  �
�                 �    (Auto-Update)       �                               �
�                 +-----------------------+                                �
�                             �                                            �
�         +-------------------+-------------------+                        �
�         ?                   ?                   ?                        �
�  +-------------+    +-------------+    +-------------+                  �
�  �  Templates  �    �   Memory    �    �  PM/Backlog �                  �
�  �  Directory  �    �   Stats     �    �   Parsing   �                  �
�  +-------------+    +-------------+    +-------------+                  �
�         �                   �                   �                        �
�         +-------------------+-------------------+                        �
�                             ?                                            �
�                 +-----------------------+                                �
�                 �   haios-status.json   �?---- OUTPUT                    �
�                 �    (Auto-Generated)    �                               �
�                 +-----------------------+                                �
�                                                                          �
+-------------------------------------------------------------------------+
```

### File Lifecycle State Machine

```
                              +-------------------------------------+
                              �         HAIOS FILE LIFECYCLE         �
                              +-------------------------------------+

    +---------+
    � TRIGGER �  Problem surfaces / Task assigned / Session starts
    +---------+
         �
         ?
+-----------------+
�     OBSERVE     �  Gather information, identify scope
�   (discovery)   �
+-----------------�
� � investigation �
� � handoff       �
+-----------------+
         �
         ?
+-----------------+
�     CAPTURE     �  Document findings, preserve knowledge
�   (document)    �
+-----------------�
� � report        �
� � checkpoint    �
� � analysis      �
+-----------------+
         �
         ?
+-----------------+
�     DECIDE      �  Choose approach, record rationale
�    (choose)     �
+-----------------�
� � ADR           �
� � proposal      �
+-----------------+
         �
         ?
+-----------------+
�      PLAN       �  Specify implementation, define success
�   (specify)     �
+-----------------�
� � plan          �
� � TRD           �
+-----------------+
         �
         ?
+-----------------+
�    EXECUTE      �  Build, implement, code
�    (build)      �
+-----------------�
� � (code files)  �
� � (tests)       �
+-----------------+
         �
         ?
+-----------------+         +-----------------+
�     VERIFY      �--------?�     OBSERVE     �  (cycle back)
�   (validate)    �  fail   �   (new issue)   �
+-----------------�         +-----------------+
� � evaluation    �
� � report        �
+-----------------+
         � pass
         ?
+-----------------+
�    COMPLETE     �  Archive, update status, extract learnings
�   (archive)     �
+-----------------�
� � checkpoint    �
� � memory store  �
+-----------------+
```

### Document Status Transitions

```
+------------------------------------------------------------------+
�                    STATUS STATE MACHINE                           �
+------------------------------------------------------------------+

                    +---------+
                    �  draft  �?-----------------+
                    +---------+                  �
                         � approve               � reopen
                         ?                       �
                    +---------+            +-----------+
            +------?� active  �-----------?� on_hold   �
            �       +---------+  block     +-----------+
            �            �
            �            � finish
            �            ?
            �       +-----------+
            �       � completed �
            �       +-----------+
            �             � archive
            �             ?
            �       +----------+
            +-------� archived �  (reactivate rarely)
                    +----------+
```

### Data Flow: Auto-Update Process

```
+-------------------------------------------------------------------------+
�                    haios-status.json AUTO-UPDATE FLOW                    �
+-------------------------------------------------------------------------+

  +-----------------+
  �  /haios called  �
  +-----------------+
           �
           ?
  +-----------------+     +---------------------------------------------+
  � Scan Templates  �----?� .claude/templates/*.md                      �
  � Directory       �     � Extract: template field from YAML           �
  +-----------------+     +---------------------------------------------+
           �
           ?
  +-----------------+     +---------------------------------------------+
  � Scan Hooks      �----?� .claude/hooks/*.ps1                         �
  � Directory       �     � Extract: script names, match to events      �
  +-----------------+     +---------------------------------------------+
           �
           ?
  +-----------------+     +---------------------------------------------+
  � Query Memory    �----?� python -c "mcp__haios-memory__memory_stats" �
  � Stats           �     � Extract: concepts, entities, traces counts  �
  +-----------------+     +---------------------------------------------+
           �
           ?
  +-----------------+     +---------------------------------------------+
  � Parse Backlog   �----?� docs/pm/backlog.md                          �
  �                 �     � Extract: count items by status              �
  +-----------------+     +---------------------------------------------+
           �
           ?
  +-----------------+     +---------------------------------------------+
  � Find Latest     �----?� docs/checkpoints/*.md                       �
  � Checkpoint      �     � Extract: session number from filename       �
  +-----------------+     +---------------------------------------------+
           �
           ?
  +-----------------+     +---------------------------------------------+
  � Write Updated   �----?� .claude/haios-status.json                   �
  � Status File     �     � Merge: static config + dynamic data         �
  +-----------------+     +---------------------------------------------+
           �
           ?
  +-----------------+
  � Display to User �
  +-----------------+
```

---

## Proposed Changes

### Phase 1: haios-status.json Auto-Update

#### 1.1 Create UpdateHaiosStatus.ps1
- [ ] Create `.claude/hooks/UpdateHaiosStatus.ps1`
- [ ] Implement template directory scanning
- [ ] Implement hooks directory scanning
- [ ] Implement Python subprocess for memory_stats()
- [ ] Implement backlog.md parsing
- [ ] Implement checkpoint session extraction
- [ ] Merge with static config and write JSON

#### 1.2 Wire to Commands
- [ ] Update `/haios` command to call UpdateHaiosStatus.ps1 first
- [ ] Update `/coldstart` command to refresh status on init
- [ ] Add optional `--refresh` flag for manual trigger

#### 1.3 Extend haios-status.json Schema
- [ ] Add `memory.concepts_count`, `memory.entities_count`, etc.
- [ ] Add `pm.high_priority_count`, `pm.blocked_count`
- [ ] Add `last_updated` timestamp
- [ ] Add `lifecycle_stats` section (count by phase)

### Phase 2: File Lifecycle Model

#### 2.1 Standardize Template Fields
- [ ] Add `lifecycle_phase` field to all templates (observe|capture|decide|plan|execute|verify)
- [ ] Ensure `status` field is consistent (draft|active|completed|archived|on_hold)
- [ ] Add optional `next_phase` hint field

#### 2.2 Update Validator Schema
- [ ] Add `report` as valid template type (fix current error)
- [ ] Add `lifecycle_phase` as valid field
- [ ] Add `session`, `title`, `priority` as valid fields
- [ ] Create `.claude/validation-schema.json` as authoritative source

#### 2.3 Lifecycle Guidance Integration
- [ ] Update `/new-*` commands to set initial lifecycle_phase
- [ ] Add lifecycle transition hints in template placeholders
- [ ] Consider PostToolUse hook to suggest next phase

### Phase 3: Memory Integration

#### 3.1 Index Template Metadata to Memory
- [ ] Extract YAML front matter on file creation
- [ ] Store as concepts with `content_type: techne` (operational knowledge)
- [ ] Enable queries like "find all active plans"

#### 3.2 Lifecycle Queries
- [ ] Add MCP tool `lifecycle_status` - show documents by phase
- [ ] Add MCP tool `lifecycle_suggest` - recommend next action based on current state

---

## Output Schema: Enhanced haios-status.json

```json
{
  "last_updated": "2025-12-07T11:15:00Z",
  "hooks": {
    "PreToolUse": { "scripts": ["PreToolUse.ps1"], "features": ["governance"] },
    "UserPromptSubmit": { "scripts": ["UserPromptSubmit.ps1"], "features": ["memory_injection"] },
    "PostToolUse": { "scripts": ["PostToolUse.ps1"], "features": ["timestamps", "validation"] },
    "Stop": { "scripts": ["Stop.ps1"], "features": ["reasoning_extraction"] }
  },
  "templates": {
    "valid_types": ["checkpoint", "plan", "report", "handoff", "ADR"],
    "count": 5
  },
  "memory": {
    "status": "online",
    "concepts_count": 62526,
    "entities_count": 7993,
    "artifacts_count": 614,
    "reasoning_traces": 348,
    "embeddings_count": 60279
  },
  "pm": {
    "backlog_path": "docs/pm/backlog.md",
    "total_items": 12,
    "active_count": 4,
    "high_priority": 2,
    "blocked": 0,
    "last_session": 39
  },
  "lifecycle": {
    "observe": 2,
    "capture": 5,
    "decide": 1,
    "plan": 3,
    "execute": 0,
    "verify": 1
  },
  "skills": ["extract-content", "memory-agent"],
  "agents": ["The-Proposer", "The-Adversary"]
}
```

---

## Verification

### Automated Tests
- [ ] UpdateHaiosStatus.ps1 produces valid JSON
- [ ] Template scanning finds all .md files in templates/
- [ ] Memory stats subprocess returns expected format
- [ ] Backlog parsing handles edge cases (empty, malformed)

### Manual Verification
- [ ] `/haios` shows fresh data after file changes
- [ ] `/coldstart` initializes with current status
- [ ] New documents get correct lifecycle_phase
- [ ] Validator accepts new fields without errors

### Documentation
- [ ] Update CLAUDE.md with lifecycle model
- [ ] Update docs/OPERATIONS.md with status automation
- [ ] Update .claude/hooks/README.md with new scripts
- [ ] Add lifecycle diagram to docs/README.md

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Python subprocess fails in PowerShell | High | Fallback to cached/default values |
| Circular updates (status triggers hook triggers status) | High | Guard against re-entry in script |
| Backlog parsing breaks on format change | Medium | Defensive parsing with defaults |
| Lifecycle model too rigid | Medium | Make lifecycle_phase optional |
| Memory MCP unavailable | Medium | Graceful degradation, show "offline" |

---

## Implementation Order

```
Week 1: Phase 1 (Auto-Update)
+-- Day 1-2: Create UpdateHaiosStatus.ps1
+-- Day 3: Wire to /haios and /coldstart
+-- Day 4-5: Test and refine

Week 2: Phase 2 (Lifecycle Model)
+-- Day 1-2: Update templates with new fields
+-- Day 3: Fix validator schema
+-- Day 4-5: Update commands

Week 3: Phase 3 (Memory Integration)
+-- Day 1-3: Template metadata indexing
+-- Day 4-5: Lifecycle query tools
```

---

## Design Principles

1. **Diagrams are paramount** - Visual alignment between user and agent reduces ambiguity
2. **Doing right should be easy** - Automation removes friction from correct behavior
3. **Graceful degradation** - System works even when components unavailable
4. **Evidence over declaration** - Status derived from reality, not manually claimed

---

## References

- Report: `docs/reports/2025-12-07-01-REPORT-haios-status-auto-update-investigation.md`
- Session 38 Checkpoint: `docs/checkpoints/2025-12-07-01-SESSION-38-governance-pm-structure.md`
- PM Self-Awareness Plan: `docs/plans/PLAN-PM-SELF-AWARENESS.md`
- CLAUDE.md Governance Section: `CLAUDE.md` (Epoch 2 Governance System)

---
