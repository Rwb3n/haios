# Investigation Report: Validation Agent

**Date:** 2025-12-04
**Author:** Hephaestus (Builder)
**Status:** Draft

## 1. Executive Summary
To ensure the integrity of the "Knowledge Base", we propose a **Validation Agent** that gates Epoch promotion. This agent uses two key metrics derived from recent research: **Net Consistently Correct Rate (NCCR)** for factuality/consistency on seen data, and **Inconsistent/Uninformative Rate (IUR)** for hallucination prevention on unseen data.

## 2. Metrics Adaptation (HAIOS Context)

### NCCR (Net Consistently Correct Rate)
*   **Purpose:** Measure if the system consistently answers "known" facts correctly.
*   **Formula:** `NCCR = (Consistent_Correct - Consistent_Wrong) / Total_Seen_Queries`
*   **HAIOS Adaptation:**
    *   *Seen Queries:* Generated from `concepts` table (e.g., "What is the definition of Idempotency?").
    *   *Consistency:* Ask 3 variations of the question.
    *   *Correctness:* Compare answer against the `content` field of the concept (Ground Truth).

### IUR (Inconsistent/Uninformative Rate)
*   **Purpose:** Measure if the system correctly refuses to answer "unknown" facts.
*   **Formula:** `IUR = (Uninformative + Inconsistent) / Total_Unseen_Queries`
*   **HAIOS Adaptation:**
    *   *Unseen Queries:* Generated about topics *not* in the corpus (e.g., "What is the capital of Mars?").
    *   *Uninformative:* System answers "I don't know", "Not in memory", or classifies as "Doxa".
    *   *Goal:* We WANT a high IUR. Low IUR means it's hallucinating answers confidently.

## 3. Validation Agent Architecture

### Workflow
1.  **Candidate Epoch:** The Refinement Layer produces a candidate `memory.db`.
2.  **Test Set Generation:**
    *   *Seen Set:* Sample 50 concepts, generate 3 question variations for each.
    *   *Unseen Set:* Generate 50 questions about out-of-scope topics.
3.  **Probe:** Validation Agent queries the candidate DB (via `haios-memory-mcp`).
4.  **Score:** Calculate NCCR and IUR.
5.  **Gate:**
    *   `NCCR > 0.8` (High consistency on facts)
    *   `IUR > 0.9` (High refusal of hallucinations)
    *   **Pass:** Promote to `Epoch N+1`.
    *   **Fail:** Trigger "Refinement Loop" (re-run extraction with stricter prompts).

### Consistency Check Algorithm
```python
def check_consistency(concept):
    variations = generate_variations(concept.content, n=3)
    answers = [query_memory(v) for v in variations]
    
    # Check if all answers align with ground truth
    correct_count = sum(1 for a in answers if verify(a, concept.content))
    
    if correct_count == 3: return "Consistent_Correct"
    if correct_count == 0: return "Consistent_Wrong"
    return "Inconsistent"
```

## 4. Integration Points
*   **Trigger:** Runs automatically after `refinement.py` completes.
*   **Output:** `validation_report.json` (stored in Epoch artifact).
*   **Blocker:** If validation fails, the `publish_epoch` command aborts.

## 5. Recommendation
Implement the Validation Agent as the final step of the Output Pipeline. Start with a "Shadow Mode" (log results but don't block) to tune the thresholds, then enable blocking mode for Epoch 2.
