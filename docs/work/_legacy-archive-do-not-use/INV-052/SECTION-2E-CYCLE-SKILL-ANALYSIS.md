# generated: 2025-12-30
# System Auto: last updated on: 2025-12-30T21:08:05
# Section 2E: Cycle Skill Analysis

Generated: 2025-12-30 (Session 150)
Purpose: Comprehensive analysis of 7 cycle skills for normalization

---

## Cycles Analyzed

| Cycle | Phases | Terminal? |
|-------|--------|-----------|
| implementation-cycle | PLAN -> DO -> CHECK -> DONE -> CHAIN | No |
| investigation-cycle | HYPOTHESIZE -> EXPLORE -> CONCLUDE -> CHAIN | No |
| close-work-cycle | VALIDATE -> OBSERVE -> ARCHIVE -> MEMORY -> CHAIN | No |
| work-creation-cycle | VERIFY -> POPULATE -> READY -> CHAIN | No |
| checkpoint-cycle | SCAFFOLD -> FILL -> VERIFY -> CAPTURE -> COMMIT | Yes |
| observation-triage-cycle | SCAN -> TRIAGE -> PROMOTE | Yes |
| plan-authoring-cycle | ANALYZE -> AUTHOR -> VALIDATE -> CHAIN | No |

---

## Common Patterns

### Pattern 1: Phase Categories

All cycles follow roughly the same semantic structure:

```
PREPARATION -> EXECUTION -> VALIDATION -> PERSISTENCE -> ROUTING
```

| Category | Phase Examples |
|----------|---------------|
| Preparation | PLAN, HYPOTHESIZE, VERIFY, ANALYZE, SCAFFOLD, SCAN |
| Execution | DO, EXPLORE, POPULATE, AUTHOR, FILL, TRIAGE |
| Validation | CHECK, VERIFY, VALIDATE |
| Persistence | DONE, CONCLUDE, ARCHIVE, MEMORY, CAPTURE, COMMIT, PROMOTE |
| Routing | CHAIN |

### Pattern 2: Exit Gates

Three types of exit gates:

| Type | Examples | Blocking? |
|------|----------|-----------|
| **skill** | plan-validation-cycle, design-review-validation, dod-validation-cycle | Yes |
| **subagent** | preflight-checker, anti-pattern-checker, validation-agent | Yes |
| **none** | Most phases in investigation, work-creation, observation-triage | N/A |

### Pattern 3: Memory Integration

| Cycle | Query Phase | Store Phase |
|-------|-------------|-------------|
| implementation-cycle | DO (optional) | DONE |
| investigation-cycle | HYPOTHESIZE | CONCLUDE |
| close-work-cycle | None | MEMORY |
| work-creation-cycle | POPULATE (optional) | None |
| checkpoint-cycle | None | CAPTURE |
| observation-triage-cycle | None | PROMOTE |
| plan-authoring-cycle | AUTHOR | None |

### Pattern 4: CHAIN Routing

5/7 cycles use routing; 2/7 are terminal:

| Strategy | Cycles | Decision Logic |
|----------|--------|----------------|
| **routing_gate** | implementation, investigation, close-work, plan-authoring | INV-* -> investigation<br>has_plan -> implementation<br>else -> work-creation |
| **confidence_based** | work-creation | Prefix-based (INV-* -> /new-investigation) |
| **terminal** | checkpoint, observation-triage | No routing, cycle ends |

---

## Normalization Assessment

### Extractable to YAML (High Value)

1. **Phase names** - 100% extractable
2. **Exit gate declarations** - type, name, timing, blocking
3. **Memory integration** - query/store/none per phase
4. **CHAIN routing** - strategy, targets, terminal flag
5. **Scaffold actions** - recipe name, phase

### Keep in SKILL.md (Complex Logic)

1. **Exit criteria checklists** - Too detailed for YAML
2. **Guardrails** - MUST follow instructions
3. **Phase-specific actions** - "List files BEFORE writing"
4. **Tool usage patterns** - Which tools per phase
5. **Edge case handling** - Phase-specific exceptions

---

## Differences by Cycle

### Phase Count

- 3 phases: observation-triage-cycle
- 4 phases: investigation, work-creation, plan-authoring
- 5 phases: implementation, close-work, checkpoint

### Unique Features

| Cycle | Feature | Why |
|-------|---------|-----|
| close-work-cycle | OBSERVE before ARCHIVE | INV-047: capture while in active/ |
| checkpoint-cycle | SCAFFOLD first | Must create file before filling |
| checkpoint-cycle | anti-pattern-checker | Prevent unverified claims |
| observation-triage | Interactive TRIAGE | User chooses category/action/priority |
| work-creation | Confidence routing | Different from routing_gate |

---

## Recommendation: Hybrid Architecture

```
cycle-definitions.yaml (STRUCTURE)
      |
      v
Thin Executor (DISPATCH)
      |
      v
SKILL.md (LOGIC)
```

### cycle-definitions.yaml

```yaml
cycles:
  implementation-cycle:
    description: "PLAN->DO->CHECK->DONE workflow"
    phases:
      - name: PLAN
        exit_gates:
          - type: skill
            name: plan-validation-cycle
          - type: subagent
            name: preflight-checker
        memory: null
      - name: DO
        exit_gates:
          - type: skill
            name: design-review-validation
        memory: query
      - name: CHECK
        exit_gates: []
        memory: null
      - name: DONE
        exit_gates: []
        memory: store
      - name: CHAIN
        exit_gates: []
        memory: null
    chain:
      terminal: false
      routing_strategy: routing_gate
```

### Cycle Orchestrator (Session 150 - approved design)

The orchestrator sits above phase execution and ensures cycle-level completion.

```python
def execute_cycle(cycle_id: str, work_id: str):
    """
    Orchestrates full cycle execution with completion validation.
    Prevents premature closure by checking objective_complete gate.
    """
    cycle_def = load_cycle_definition(cycle_id)
    current_phase = get_current_phase(work_id)  # From WORK.md node_history

    while current_phase != 'CHAIN':
        phase_def = cycle_def.phases[current_phase]

        # Run phase
        result = execute_phase(cycle_id, current_phase, work_id)

        # Check phase exit criteria (from SKILL.md)
        if not phase_exit_criteria_met(cycle_id, current_phase, work_id):
            return CycleResult(
                status="incomplete",
                message=f"Phase {current_phase} incomplete - continue working",
                current_phase=current_phase
            )

        # Advance to next phase
        current_phase = get_next_phase(cycle_def, current_phase)
        update_work_file_phase(work_id, current_phase)

    # CRITICAL: Before CHAIN, validate cycle-level objective
    # This gate prevented INV-052 premature closure
    if not check_gate('objective_complete', work_id):
        return CycleResult(
            status="blocked",
            message="Cycle objective not met - review remaining work",
            gate_failure="objective_complete"
        )

    # Execute CHAIN routing
    return execute_chain(cycle_def.chain, work_id)


def check_gate(gate_name: str, work_id: str) -> bool:
    """
    Evaluates a gate from gates.yaml.
    For composite gates, all sub-checks must pass.
    """
    gate_def = load_gate_definition(gate_name)

    if gate_def.get('composite'):
        # Composite gate: all checks must pass
        for check in gate_def['checks']:
            if check.get('type') == 'subagent':
                result = invoke_subagent(check['subagent'], work_id)
                if not result.passed:
                    return False
            else:
                if not evaluate_check(check['check'], work_id):
                    return False
        return True
    else:
        # Simple gate
        return evaluate_check(gate_def['check'], work_id)
```

### Phase Executor (unchanged from original)

```python
def execute_phase(cycle_id: str, phase_name: str, work_id: str):
    cycle_def = load_cycle_definition(cycle_id)
    phase_def = cycle_def.phases[phase_name]

    # 1. Run exit gates
    for gate in phase_def.exit_gates:
        if gate.type == 'skill':
            invoke_skill(gate.name)
        elif gate.type == 'subagent':
            invoke_subagent(gate.name)

    # 2. Memory integration
    if phase_def.memory == 'query':
        query_memory(work_id)
    elif phase_def.memory == 'store':
        store_to_memory(work_id)

    # 3. Load skill for phase logic
    skill_instructions = load_skill_phase(cycle_id, phase_name)
    return skill_instructions
```

### SKILL.md (Unchanged)

Contains:
- Exit criteria checklists
- Guardrails
- Phase-specific actions
- Tool guidance

---

## Next Steps

1. ~~Define full cycle-definitions.yaml schema~~ (Done: SECTION-2F)
2. ~~Extract gates.yaml for gate check definitions~~ (Done: SECTION-2F)
3. ~~Design objective_complete gate~~ (Done: Session 150)
4. ~~Design cycle orchestrator~~ (Done: Session 150)
5. Prototype cycle_executor.py implementation
6. Validate against all 7 cycles

---

*Analysis from Session 150, investigation-agent evidence gathering*
