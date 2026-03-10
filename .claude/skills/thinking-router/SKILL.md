---
name: thinking-router
type: workflow
trigger: facing a problem that benefits from structured thinking, or when the user requests a specific thinking mode
cadence: on demand (agent-initiated or manual)
---

# Thinking Router

Select 1-3 cognitive thinking modes to apply before working on a problem.

## Mode Index

| Mode | Lens |
|------|------|
| Causal | Trace cause and effect chains |
| Abstract | Extract general principles from specifics |
| Nonlinear | Explore feedback loops and emergent behavior |
| Recursive | Decompose into self-similar subproblems |
| Epistemic | Examine what you know, don't know, and can't know |
| Heuristic | Apply practical rules of thumb and mental shortcuts |
| Bayesian | Update beliefs based on evidence and priors |
| Dialectical | Explore opposing viewpoints to find synthesis |
| Integrative | Hold multiple models simultaneously, find creative resolution |
| Probabilistic | Reason about likelihoods and distributions |
| Hypothetical | Construct and test "what if" scenarios |
| Counterfactual | Examine "what would have happened if" alternatives |

## Routing

### Manual invocation

User requests a mode or says `/thinking-router`. Read the requested mode file(s) from `modes/`, apply them.

### Agent-initiated

When you judge a thinking mode would genuinely add value, select based on task signals:

| Task type | Recommended modes |
|-----------|------------------|
| Debugging | Causal + Hypothetical |
| Design / architecture | Integrative + Abstract |
| Risk / uncertainty | Bayesian + Probabilistic |
| Evaluating trade-offs | Dialectical + Counterfactual |
| Exploring unknowns | Epistemic + Heuristic |
| Decomposing complexity | Recursive + Nonlinear |

Pick 1-3 modes. Read their files from `modes/` for guiding questions and structure.

## Output Format

For each selected mode, produce a visible reasoning block:

**Thinking [Mode Name]:**
[Work through that mode's guiding questions]

**Thinking [Mode Name 2]:** (if layered)
[Work through second mode's guiding questions]

**Synthesis:** (only when 2+ modes used)
[Integrated conclusion drawing from the modes applied]

Then proceed with the task.

## Constraints

- Max 3 modes per task
- Only apply when it genuinely adds value — not every task needs this
- Read mode files for depth; don't guess the guiding questions
