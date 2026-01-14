---
template: implementation_plan
status: approved
date: 2025-12-06
backlog_id: E2-002
title: "PLAN-EPOCH2-002: Implement /validate Command"
author: Hephaestus
project_phase: Phase 8 Complete
version: "1.0"
---
# generated: 2025-12-06
# System Auto: last updated on: 2025-12-08 22:53:07
# Implementation Plan: Implement /validate Slash Command

@docs/README.md
@.claude/COMMANDS-REF.md

> **ID:** PLAN-EPOCH2-002-COMMAND-VALIDATE
> **Status:** Draft (VERIFIED by Hephaestus - 2025-12-06)
> **Author:** Genesis (Architect)
> **Target:** Hephaestus (Builder)
> **Context:** Epoch 2 Enablement (Turn-by-Turn Execution)

## 1. Goal
Reduce governance friction by implementing a `/validate` slash command that allows agents (and the user) to verify template compliance on-demand with a single keyword.

## 2. Problem Statement (VERIFIED CORRECT)
Currently, validating a document against the "File-Based Epoch" standards requires manually running a PowerShell script (`.claude/hooks/ValidateTemplate.ps1`). This high-friction barrier leads to "drift" where documents are saved without valid headers or structure.

**Note:** `ValidateTemplateHook.ps1` runs automatically on PostToolUse (Edit/Write), but:
- It only validates files AFTER they're written
- There's no on-demand validation for arbitrary files
- No way to batch-validate or check files before editing

## 3. Proposed Changes

### 3.1. Create `.claude/commands/validate.md`
This markdown file defines the slash command logic.

**Command Specification:**
```markdown
---
allowed-tools: Bash
description: Validate a markdown file against HAIOS templates (TRD, ADR, Checkpoint, etc.)
argument-hint: [file_path]
---

# Validate Template

Ref: @.claude/hooks/ValidateTemplate.ps1

## Logic
1. If NO arguments are provided:
   - Run the validation script on the ACTIVE active document (if known) or ask user for target.
2. If Argument is provided:
   - Run: `powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/ValidateTemplate.ps1 -FilePath "$1"`

## Output
- Present the stdout from the script (Status, Errors, Warnings) clearly to the user.
- If errors exist, suggest immediate fixes.
```

## 4. Verification Plan

### 4.1 Test Command
1.  Run `/validate docs/plans/PLAN-EPOCH2-001-HOOKS-WIRING.md`
2.  Expectation: Steps through validation (YAML check, Logic check) and reports "✅ Valid".

### 4.2 Test Failure Case
1.  Create `invalide_file.md` simply containing "Hello World".
2.  Run `/validate invalide_file.md`
3.  Expectation: Reports "❌ Error: Missing YAML header".

## 5. Risks
*   **Pathing:** Ensuring the relative path to `.claude/hooks/ValidateTemplate.ps1` resolves correctly from where the agent runs the command.


<!-- VALIDATION ERRORS (2025-12-06 14:57:19):
  - ERROR: Missing 'template' field in YAML header
  - ERROR: Only 1 @ reference(s) found (minimum 2 required)
-->
