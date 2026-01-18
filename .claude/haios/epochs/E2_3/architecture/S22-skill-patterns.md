# generated: 2026-01-06
# System Auto: last updated on: 2026-01-06T22:37:35
# Section 22: Skill Patterns

Generated: 2026-01-06 (Session 179)
Source: Operator-Agent dialogue
Status: PRINCIPLE (foundational)
Depends: S20 (Pressure Dynamics), S21 (Cognitive Notation)

---

## The Insight

A single pass is the anti-pattern. The agent thinks linearly: "I did EXPLORE, now CONCLUDE." But real work is iterative.

**The agent's failure mode:** Jump straight to extraction without survey passes. Miss the forest for the first tree.

**The principle:** Skills have internal rhythm - multiple passes suited to their purpose. The exit condition isn't "I completed the phase" - it's "nothing new emerged" (saturation).

---

## Pattern Library

Patterns are composable building blocks. Each has:
- Pass structure
- Pressure per pass ([MAY] or [MUST])
- Exit condition
- Failure mode it counters

### Exploration Patterns

**exploration:zoom** - Progressive refinement (wide→narrow, shallow→deep)

```
Pass 1: Survey      [MAY]   → identify containers (folders, modules)
Pass 2: Catalog     [MAY]   → identify items (files, functions)
Pass 3: Select      [MUST]  → pick relevant subset (commit to scope)
Pass 4: Scan        [MAY]   → identify structure (sections, signatures)
Pass 5: Extract     [MAY]   → deep read (content, logic)
Pass 6: Synthesize  [MUST]  → connect findings (commit to conclusion)
```

Exit: Δfindings < threshold (saturation)
Counters: Linear completion bias, missing context

**exploration:radial** - Expand from center

```
Pass 1: Core        [MAY]   → identify central concept
Pass 2: Adjacent    [MAY]   → what touches the core?
Pass 3: Peripheral  [MAY]   → what touches the adjacent?
Pass N: Boundary    [MUST]  → where does relevance end? (commit)
```

Exit: Relevance drops below threshold
Counters: Tunnel vision, missing connections

---

### Creation Patterns

**creation:scaffold** - Structure then fill

```
Pass 1: Skeleton    [MUST]  → structure exists (commit to shape)
Pass 2: Flesh       [MAY]   → fill in content
Pass 3: Refine      [MAY]   → improve what's there
Pass 4: Polish      [MUST]  → final state (commit to done)
```

Exit: All sections filled, quality bar met
Counters: Premature detail, losing structure

**creation:accretion** - Build up incrementally

```
Pass 1: Seed        [MUST]  → minimal working thing (commit)
Pass 2: Add         [MAY]   → add one capability
Pass 3: Add         [MAY]   → add another
Pass N: Complete    [MUST]  → all capabilities present (commit)
```

Exit: Feature list complete
Counters: Over-engineering, analysis paralysis

---

### Validation Patterns

**validation:checklist** - Sequential verification

```
Check 1: Gate₁      [MUST]  → pass/fail
Check 2: Gate₂      [MUST]  → pass/fail
Check N: Gate_N     [MUST]  → pass/fail
Verdict:            [MUST]  → all pass = approved
```

Exit: All gates pass OR any gate fails
Counters: Optimistic confidence, skipping verification

**validation:adversarial** - Try to break it

```
Pass 1: Happy path  [MUST]  → does it work normally?
Pass 2: Edge cases  [MAY]   → what about boundaries?
Pass 3: Break it    [MAY]   → actively try to fail
Pass 4: Verdict     [MUST]  → survived attacks? (commit)
```

Exit: No more attack vectors found
Counters: False confidence, untested assumptions

---

### Transformation Patterns

**transformation:pipeline** - Staged processing

```
Stage 1: Parse      [MUST]  → input → structured (commit to interpretation)
Stage 2: Transform  [MAY]   → structured → modified
Stage 3: Validate   [MUST]  → modified → verified (commit to correctness)
Stage 4: Emit       [MUST]  → verified → output (commit to result)
```

Exit: Output produced and validated
Counters: Garbage in/garbage out, silent corruption

---

### Observation Patterns

**observation:recall** - Memory to capture

```
Pass 1: What        [MAY]   → what happened? (freeform)
Pass 2: Surprise    [MAY]   → what was unexpected?
Pass 3: Capture     [MUST]  → write it down (commit: non-empty)
```

Exit: At least one observation captured OR explicit "none"
Counters: Ceremonial completion, skipping reflection

**observation:contrast** - Expected vs actual

```
Pass 1: Expected    [MAY]   → what did you predict?
Pass 2: Actual      [MAY]   → what happened?
Pass 3: Delta       [MUST]  → what's the difference? (commit)
Pass 4: Learn       [MUST]  → what does delta teach? (commit)
```

Exit: Learning extracted from delta
Counters: Not updating mental models, repeating mistakes

---

## Pattern Composition

Phases pick patterns that fit their purpose:

| Phase Purpose | Uses Pattern |
|---------------|--------------|
| Understand something | exploration:zoom or exploration:radial |
| Build something | creation:scaffold or creation:accretion |
| Verify something | validation:checklist or validation:adversarial |
| Improve something | exploration:zoom (applied to existing work) |
| Transform something | transformation:pipeline |
| Reflect on something | observation:recall or observation:contrast |

**Key insight:** "Refine" is exploration applied to creation output. Phases aren't locked to one pattern.

---

## Cycle Composition Examples

```yaml
# Standard investigation
investigation-cycle-v1:
  HYPOTHESIZE: exploration:zoom
  EXPLORE: exploration:zoom
  CONCLUDE: observation:recall

# Adversarial investigation
investigation-cycle-v2:
  HYPOTHESIZE: exploration:zoom
  EXPLORE: exploration:zoom
  CHALLENGE: validation:adversarial
  CONCLUDE: observation:contrast

# Standard implementation
implementation-cycle-v1:
  PLAN: exploration:zoom
  DO: creation:scaffold
  CHECK: validation:checklist
  REFINE: exploration:zoom
  DONE: observation:recall

# Incremental implementation
implementation-cycle-v2:
  PLAN: exploration:zoom
  DO: creation:accretion
  CHECK: validation:adversarial
  DONE: observation:contrast
```

---

## Experimentation

Composability enables experimentation:

1. **Define patterns** - building blocks with clear semantics
2. **Compose cycles** - combine patterns into workflows
3. **Test cycles** - which composition works for which problem?
4. **Iterate** - discover new patterns, refine compositions

The architecture becomes a **design space** to explore, not a fixed structure.

---

## The Zoom Pattern (Detailed)

The most common exploration pattern, shown in full:

```
Scope:    WIDE ────────────────────────► NARROW
Depth:    SHALLOW ─────────────────────► DEEP

Pass 1:   [████████████████████]  containers   (many, surface)
Pass 2:   [████████████████]      items        (many, surface)
Pass 3:   [████████]              items        (few, surface)   ← COMMIT
Pass 4:   [████]                  structure    (few, medium)
Pass 5:   [██]                    content      (few, deep)
Pass 6:   [█]                     synthesis    (one, deepest)   ← COMMIT
```

Like algorithms:
- Breadth-first → Depth-first
- Map → Filter → Reduce
- Divide and conquer

---

## Related

- S20: Pressure Dynamics (rhythm: [MAY]/[MUST])
- S21: Cognitive Notation (signals: MUST, |>, etc.)
- S10: Skills Taxonomy (skill categories)
- Breath chapter: Where pattern experimentation happens

---

*This document defines composable skill patterns discovered through operator-agent dialogue. Patterns are building blocks; cycles are compositions.*
