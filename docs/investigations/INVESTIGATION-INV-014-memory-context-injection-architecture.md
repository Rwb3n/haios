---
template: investigation
status: complete
date: 2025-12-14
backlog_id: INV-014
title: "Investigation: Memory Context Injection Architecture"
author: Hephaestus
lifecycle_phase: conclude
version: "1.1"
session: 72
spawned_by: INV-010
closed_session: 102
closure_note: "Findings consolidated into INV-023 (ReasoningBank Feedback Loop). H2 resolved (mode param). H3 (meta-strategies) confirmed, feeds INV-023 H2. Remaining items (truncation, format) deferred - injection disabled."
generated: 2025-12-23
last_updated: 2025-12-23T11:01:13
---
# Investigation: Memory Context Injection Architecture

@docs/README.md
@docs/epistemic_state.md

---

## Context

Session 72 observed that the memory context injection (visible in `<system-reminder>` blocks) suffers from multiple issues:
1. Content is truncated mid-sentence ("nuanc" instead of "nuanced")
2. Strategies are meta-level (about searching) not domain-relevant
3. Format uses semicolons that look odd
4. Recently implemented `mode` parameter (ADR-037) is NOT used

Example of problematic injection:
```
--- Memory Context (learned_from: 10, strategy: default_hybrid) ---
strategies[3]{title,content}:
  Leverage Hybrid Search,The 'default_hybrid' approach; which combines different search techniques; proved effective in this scenario. This suggests that when a query is nuanc
```

---

## Objective

1. Determine if current memory injection is relevant and useful
2. Understand why truncation occurs and design better solution
3. Identify other architectural issues for improvement
4. Integrate ADR-037 retrieval modes into the injection pipeline

---

## Scope

### In Scope
- `UserPromptSubmit.ps1` hook (lines 42-90) - invokes memory retrieval
- `memory_retrieval.py` - generates embedding, searches, formats TOON output
- Format and truncation decisions
- Integration with ADR-037 retrieval modes
- Strategy quality for prompt injection use case

### Out of Scope
- Overall memory storage architecture
- Synthesis pipeline changes
- Hook timing/performance (handled elsewhere)

---

## Hypotheses

1. **H1: Truncation is hardcoded** - Content limited to 150 chars arbitrarily, causing mid-word cuts
2. **H2: Mode not passed** - `memory_retrieval.py` doesn't use ADR-037 `mode` parameter
3. **H3: Strategies are wrong type** - Strategy extraction captures meta-patterns (how to search) not domain knowledge (what to do)
4. **H4: No type filtering** - SynthesizedInsight can appear, diluting actionable content
5. **H5: Format sacrifices readability** - TOON semicolon replacement makes content hard to parse

---

## Initial Findings (Session 72)

### H1: CONFIRMED - Hardcoded Truncation

**Location:** `.claude/hooks/memory_retrieval.py` lines 82, 90-91

```python
# Line 82 - Strategy truncation
content = s.get('content', '')[:150]

# Line 90-91 - Memory truncation
content = r.get('content', '')[:150]
```

**Impact:** "nuanc" instead of "nuanced", sentences cut mid-thought

**Design Questions:**
- Why 150? Token budget? Context window?
- Should truncation be sentence-aware?
- Should we show fewer items but complete?

### H2: CONFIRMED - Mode Not Passed

**Location:** `.claude/hooks/memory_retrieval.py` lines 131-135

```python
result = retrieval.search_with_experience(
    query=query,
    space_id=None,
    filters=None
    # NO mode parameter!
)
```

**Impact:** Uses default `semantic` mode instead of purpose-built modes

**Fix:** Should use `mode='session_recovery'` or a new `prompt_injection` mode that filters for actionable content

### H3: LIKELY - Strategies Are Meta-Level

**Observed strategies:**
- "Leverage Hybrid Search" - about searching
- "Evaluate Synthesis Quality from Context" - about evaluation
- "Clarify Scope for Ambiguous Queries" - about query handling

**Analysis:** These are ReasoningBank traces about HOW the system searches, not WHAT the user should do. Strategy extraction prompt may be too generic.

**Root Cause Hypothesis:** `extraction.py::extract_strategy()` extracts patterns about system behavior, not domain knowledge. Needs investigation.

### H4: CONFIRMED - No Type Filtering in Injection

**Location:** `memory_retrieval.py` line 75

```python
filtered = [r for r in results if r.get('score', 0) >= SIMILARITY_THRESHOLD]
```

Only filters by score threshold (0.7), not by type. SynthesizedInsight can appear.

### H5: CONFIRMED - Format Readability Issue

**Location:** `memory_retrieval.py` lines 83, 91

```python
content = content.replace('\n', ' ').replace(',', ';')
```

**Purpose:** TOON format uses commas as delimiters, so commas in content must be escaped

**Impact:** "when a query is nuanced, it suggests" becomes "when a query is nuanced; it suggests" - looks like grammar error

---

## Investigation Steps

1. [x] Read UserPromptSubmit.ps1 hook mechanism
2. [x] Read memory_retrieval.py implementation
3. [x] Identify truncation source
4. [x] Check mode parameter usage
5. [ ] Analyze strategy extraction prompt in extraction.py
6. [ ] Design improved injection format
7. [ ] Propose mode or type filter for prompt injection
8. [ ] Consider sentence-aware truncation

---

## Recommendations (Preliminary)

### Quick Wins (Session 72)
1. **Add mode parameter:** Pass `mode='session_recovery'` to exclude SynthesizedInsight
2. **Increase truncation limit:** 150 → 300 chars or sentence-aware

### Architectural Improvements
1. **New retrieval mode:** `prompt_injection` - filters for actionable types (Decision, Directive, techne)
2. **Strategy extraction fix:** Investigate if strategy prompt needs domain focus
3. **Format redesign:** Consider JSON with truncation indicators (`...`) or structured sections

### Questions for Operator
1. What's the token budget for memory injection?
2. Should strategies be included at all, or only memories?
3. Is TOON format worth the readability cost?

---

## Spawned Work Items

- [ ] E2-059: memory_retrieval.py add mode parameter (quick fix)
- [ ] E2-060: Sentence-aware truncation for injection
- [ ] E2-061: Strategy extraction quality audit (may merge with INV-003)
- [ ] E2-062: `prompt_injection` retrieval mode

---

## Expected Deliverables

- [x] Initial findings documented
- [ ] Root cause analysis of strategy quality
- [ ] Design proposal for improved injection
- [ ] Memory storage (concepts)

---

## References

- INV-010: Memory Retrieval Architecture Mismatch (parent investigation)
- ADR-037: Hybrid Retrieval Architecture (implemented modes)
- `.claude/hooks/UserPromptSubmit.ps1` - Hook entry point
- `.claude/hooks/memory_retrieval.py` - Retrieval and formatting
- `haios_etl/extraction.py` - Strategy extraction logic

---
