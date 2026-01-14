# Strategic Execution Plan

**Date:** 2025-12-06
**Context:** Phase 8 Complete -> Phase 9/11 Transition
**Objective:** Align operational cleanup with strategic architectural shifts.

## 1. Strategic Context Analysis

The project is pivoting from **"Building the Engine"** (ETL, Vector DB, Extraction) to **"Running the Engine"** (Sessions, Governance, Feedback).

-   **Vision Anchor:** Demands "ReasoningBank" learning loop. This is technically "closed" but operationally requires the **File-Based Epoch Architecture** to capture the feedback signal for humans.
-   **Epistemic State:** Claims alignment with File-Based Epochs. This architecture is the *missing link* between the raw database and the "Governance Flywheel".

**Conclusion:** The "File-Based Epoch Architecture" is not just a feature; it is the **Critical Path** to Epoch 2. All other tasks are secondary hygiene.

## 2. Priority Matrix

| Item | Strategic Value | Urgency | Decision |
|------|-----------------|---------|----------|
| **File-Based Epoch Arch** | **High** (Enables Flywheel) | **High** (Next Session) | **BATCH A** |
| **Epistemic State Sync** | **High** (Trust) | **Medium** | **BATCH B** |
| **Audit Report Linking** | Medium (Hygiene) | Low | **BATCH B** |
| **Sub-directory READMEs** | Medium (Onboarding) | Low | **BATCH B** |
| **Re-embed Corpus** | Medium (Quality) | Low | **BATCH C** |
| **vec0 Migration** | Low (Optimization) | Low | **DEFER** |
| **Consolidate Session 27** | Low (Aesthetic) | Low | **DROP** |
| **Metrics Endpoint** | Low | Low | **DROP** |

## 3. Execution Batches

### Batch A: The Strategic Pivot (Architecture)
*Goal: Enable the File-Based Session workflow.*
1.  **Formalize Architecture:** Move `HANDOFF-file-based-epoch-architecture.md` to `docs/specs/TRD-SESSION-ARCHITECTURE-v1.md`.
2.  **Implement Hooks:** Create/Update `SessionStart`, `UserPromptSubmit`, `Stop`, `PostToolUse` in `.claude/hooks/`.
3.  **Verify:** Run a "dummy session" to verify folder creation and logging.

### Batch B: Epistemic Hardening (Documentation)
*Goal: Ensure the documentation reflects the new reality.*
1.  **Update `epistemic_state.md`:** Explicitly detail the new Session Architecture as "Implemented".
2.  **Link Reports:** Add Audit Reports to `docs/README.md`.
3.  **Create READMEs:** `docs/checkpoints/README.md` and `docs/handoff/README.md` explaining the new "Keep it Clean" policy.

### Batch C: Data Quality Cycle (Optimization)
*Goal: Ensure the memory is pristine.*
1.  **Re-embed Corpus:** Run the gap-fill script to ensure 100% embeddings.
2.  **AntiPattern Scan:** Manual `grep` for "AP-" to confirm extraction reality.

## 4. Defer / Drop List

-   **DROP:** Consolidating Session 27 files. (Too much effort for zero functional gain. Just archive them eventually).
-   **DROP:** Metrics Endpoint. (YAGNI).
-   **DEFER:** `vec0` migration. (Current performance is fine).

## 5. Dependencies

```
[Start]
   |
   +--> [Batch A: Architecture] --+
   |                              |
   +--> [Batch B: Docs] <---------+ (Docs needed to describe Arch)
   |
   +--> [Batch C: Optimization] (Independent)
```

## 6. Recommendations

**Immediate Next Action:** Execute **Batch A**. Implementing the File-Based Epoch Architecture will immediately improve the quality of *this* and future sessions, enabling the very feedback loop we need to validate the rest.
