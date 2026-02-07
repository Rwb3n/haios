# generated: 2025-12-30
# System Auto: last updated on: 2025-12-30T21:32:40
# Section 2G: Cycle Extension Guide

Generated: 2025-12-30 (Session 150)
Purpose: How to create custom cycles without breaking the system

---

## Overview

Cycles are configurable workflows defined in YAML, executed by a thin orchestrator.

**Core principle:** YAML defines WHAT (structure), SKILL.md defines HOW (logic).

---

## Adding a New Cycle

### Step 1: Define in cycle-definitions.yaml

```yaml
# .claude/haios/config/cycle-definitions.yaml
cycles:
  # ... existing cycles ...

  my-custom-cycle:
    description: "Brief description of workflow purpose"
    node: null                    # null = standalone, or bind to DAG node
    phases:
      - name: FIRST_PHASE
        description: "What this phase accomplishes"
        exit_gates: []            # Gates that must pass before exit
        memory: query             # query | store | null
        scaffold: null            # ScaffoldConfig or null
        tools: [Read, Glob]       # Suggested tools

      - name: SECOND_PHASE
        description: "Next step"
        exit_gates:
          - type: gate
            name: my_custom_check
            blocking: true
        memory: null
        scaffold: null
        tools: [Edit]

      - name: CHAIN                # Required for non-terminal cycles
        description: "Route to next work"
        exit_gates: []
        memory: null
        scaffold: null
        tools: []

    chain:
      terminal: false             # true = no routing, cycle ends
      routing_strategy: routing_gate
      targets:
        - investigation-cycle
        - implementation-cycle
        - work-creation-cycle
      fallback: await_operator
```

### Step 2: Create SKILL.md

```
.claude/haios/skills/my-custom-cycle/
├── SKILL.md          # Phase-specific logic, guardrails, exit criteria
└── README.md         # Optional: when to use, examples
```

SKILL.md contains:
- Exit criteria checklists per phase
- Guardrails (MUST follow instructions)
- Phase-specific actions
- Tool usage guidance
- Edge case handling

### Step 3: Register Custom Gates (if needed)

```yaml
# .claude/haios/config/gates.yaml
gates:
  # ... existing gates ...

  my_custom_check:
    description: "What this gate validates"
    check: |
      content = read('docs/work/active/{{id}}/WORK.md')
      # Custom validation logic
      return content.contains('required_field')
```

### Step 4: Bind to Node (optional)

If your cycle should be the default for a DAG node:

```yaml
# .claude/haios/config/node-bindings.yaml
nodes:
  my_node:
    cycle: my-custom-cycle
    entry_gate: work_file_exists
```

---

## Extension Points

| Extension | Location | Purpose |
|-----------|----------|---------|
| New cycle | cycle-definitions.yaml | Define phase structure |
| Phase logic | SKILL.md | Define what happens in each phase |
| Custom gate | gates.yaml | Add validation checks |
| Node binding | node-bindings.yaml | Map cycle to DAG node |
| Custom scaffold | ScaffoldConfig in phase | Auto-create files on phase entry |

---

## Constraints

1. **Phase names MUST be UPPERCASE** - Convention for visibility
2. **CHAIN phase required** for non-terminal cycles - Enables routing
3. **exit_gates are blocking by default** - Set `blocking: false` to warn-only
4. **memory: store requires ingester** - Phase must call ingester_ingest
5. **Orchestrator is single executor** - All cycles run through same executor

---

## Terminal vs Routed Cycles

**Terminal cycles** (checkpoint-cycle, observation-triage-cycle):
```yaml
chain:
  terminal: true
  routing_strategy: none
  targets: []
  fallback: null
```

**Routed cycles** (implementation-cycle, investigation-cycle):
```yaml
chain:
  terminal: false
  routing_strategy: routing_gate  # or confidence_based
  targets: [cycle-a, cycle-b]
  fallback: await_operator
```

---

## Open Questions

1. **Auto-discovery** - Should executor scan YAML for cycles, or require manifest?
2. **Versioning** - How to version cycle definitions for migration?
3. **Validation** - Should there be a cycle schema validator?
4. **Testing** - How to test a cycle without executing it?
5. **Inheritance** - Can cycles extend/override other cycles?

---

## Example: Review Cycle

A hypothetical code review cycle:

```yaml
cycles:
  review-cycle:
    description: "Code review workflow"
    node: null
    phases:
      - name: PREPARE
        description: "Gather diff and context"
        exit_gates: []
        memory: query
        tools: [Bash, Read]

      - name: REVIEW
        description: "Analyze code changes"
        exit_gates: []
        memory: null
        tools: [Read, Grep]

      - name: FEEDBACK
        description: "Document findings"
        exit_gates:
          - type: gate
            name: feedback_provided
        memory: store
        tools: [Edit]

      - name: CHAIN
        exit_gates: []
        memory: null
        tools: []

    chain:
      terminal: true  # Review ends, doesn't route
      routing_strategy: none
      targets: []
      fallback: null
```

---

*Initial guide - to be expanded as executor is implemented*
