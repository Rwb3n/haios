# generated: 2025-12-29
# System Auto: last updated on: 2025-12-30T21:02:29
# Section 2D: Cycle Extensibility

**STATUS: SUPERSEDED by SECTION-2F-CYCLE-DEFINITIONS-SCHEMA.md (Session 150)**

Generated: 2025-12-29 (Session 149)
Purpose: Unified config-driven extensibility for cycles (initial sketch)

---

## The Pattern

**Normalize into configurable YAML, keep code as thin executor.**

Same pattern as hooks:
- Hooks: `hook-handlers.yaml` + handler modules
- Cycles: `cycle-definitions.yaml` + executor skills

---

## Existing DAG (in Skills)

```
NODE LEVEL:
  backlog → discovery → plan → implement → close

PHASE LEVEL (from skills):
  discovery: HYPOTHESIZE → EXPLORE → CONCLUDE → CHAIN
  plan: VERIFY → POPULATE → READY → CHAIN
  implement: PLAN → DO → CHECK → DONE → CHAIN
  close: VALIDATE → OBSERVE → ARCHIVE → MEMORY → CHAIN
```

---

## Proposed Config: cycle-definitions.yaml

```yaml
cycles:
  investigation-cycle:
    node: discovery
    phases:
      - name: HYPOTHESIZE
        exit_gate: hypothesis_formed
        scaffold: []
      - name: EXPLORE
        exit_gate: evidence_gathered
        scaffold: []
      - name: CONCLUDE
        exit_gate: conclusion_reached
        scaffold: []
      - name: CHAIN
        action: invoke_routing_gate

  implementation-cycle:
    node: implement
    phases:
      - name: PLAN
        exit_gate: plan_reviewed
        scaffold: [preflight-checker]
      - name: DO
        exit_gate: implementation_complete
      - name: CHECK
        exit_gate: tests_pass
        scaffold: [validation-agent]
      - name: DONE
        exit_gate: why_captured
      - name: CHAIN
        action: invoke_routing_gate
```

---

## Proposed Config: routing-rules.yaml

**SUPERSEDED:** Routing is now embedded in ChainConfig per cycle in cycle-definitions.yaml.
See SECTION-2F for authoritative schema.

```yaml
# OLD PROPOSAL (not used):
routing:
  rules:
    - condition: "id.startswith('INV-')"
      action: invoke_investigation_cycle
    - condition: "has_plan == True"
      action: invoke_implementation_cycle
    - condition: "default"
      action: invoke_work_creation_cycle
  fallback: await_operator
```

---

## Benefits

1. **Visible workflow** - DAG explicit in config
2. **Customizable** - Add phases/gates without code
3. **Testable** - Config can be validated
4. **Portable** - Different projects, different workflows

---

## Full Config Structure

```
.claude/haios/config/
├── hook-handlers.yaml      # Handlers
├── cycle-definitions.yaml  # Cycle phases, gates, scaffolds
├── routing-rules.yaml      # CHAIN phase routing
├── gates.yaml              # Gate check definitions
└── thresholds.yaml         # Context %, stale days
```
