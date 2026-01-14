# generated: 2025-12-30
# System Auto: last updated on: 2025-12-30T21:24:01
# Section 2F: Cycle Definitions Schema

Generated: 2025-12-30 (Session 150)
Purpose: Full schema for cycle-definitions.yaml

---

## Schema Overview

```yaml
# .claude/haios/config/cycle-definitions.yaml
# Authoritative structure for all cycle skills

version: "1.0"
cycles:
  <cycle-id>:
    description: string
    node: string | null           # DAG node this cycle operates on
    phases: Phase[]
    chain: ChainConfig
```

---

## Phase Schema

```yaml
Phase:
  name: string                    # UPPERCASE phase name
  description: string             # Human-readable purpose
  exit_gates: ExitGate[]          # Gates that MUST pass before exit
  memory: "query" | "store" | null
  scaffold: ScaffoldConfig | null
  tools: string[]                 # Preferred tools for this phase
```

---

## ExitGate Schema

```yaml
ExitGate:
  type: "skill" | "subagent" | "gate"
  name: string                    # Skill/subagent/gate identifier
  timing: "pre" | "during" | "post"  # When to invoke (default: post)
  blocking: boolean               # If false, can continue on failure (default: true)
  condition: string | null        # Optional condition (e.g., ">3 files")
```

---

## ScaffoldConfig Schema

```yaml
ScaffoldConfig:
  recipe: string                  # Just recipe name (e.g., "scaffold checkpoint")
  args: string[]                  # Recipe arguments
  when: "phase_start" | "phase_end"
```

---

## ChainConfig Schema

```yaml
ChainConfig:
  terminal: boolean               # If true, no routing (cycle ends)
  routing_strategy: "routing_gate" | "confidence_based" | "none"
  targets: string[]               # Valid target cycles
  fallback: string                # What to do if no target matches
```

---

## Full Example: cycle-definitions.yaml

```yaml
version: "1.0"

cycles:
  implementation-cycle:
    description: "PLAN->DO->CHECK->DONE workflow for implementations"
    node: implement
    phases:
      - name: PLAN
        description: "Validate plan and preflight check"
        exit_gates:
          - type: skill
            name: plan-validation-cycle
            timing: post
            blocking: true
          - type: subagent
            name: preflight-checker
            timing: post
            blocking: true
            condition: ">3 files"
        memory: null
        scaffold: null
        tools: [Read, Glob]

      - name: DO
        description: "Execute implementation"
        exit_gates:
          - type: skill
            name: design-review-validation
            timing: during
            blocking: true
        memory: query
        scaffold: null
        tools: [Edit, Write, Bash]

      - name: CHECK
        description: "Verify implementation correctness"
        exit_gates:
          - type: subagent
            name: validation-agent
            timing: post
            blocking: true
        memory: null
        scaffold: null
        tools: [Bash, Read]

      - name: DONE
        description: "Capture WHY and finalize"
        exit_gates: []
        memory: store
        scaffold: null
        tools: [ingester_ingest]

      - name: CHAIN
        description: "Route to next work"
        exit_gates: []
        memory: null
        scaffold: null
        tools: []

    chain:
      terminal: false
      routing_strategy: routing_gate
      targets:
        - investigation-cycle
        - implementation-cycle
        - work-creation-cycle
      fallback: await_operator

  investigation-cycle:
    description: "HYPOTHESIZE->EXPLORE->CONCLUDE workflow for investigations"
    node: discovery
    phases:
      - name: HYPOTHESIZE
        description: "Form hypotheses and verify investigation exists"
        exit_gates: []
        memory: query
        scaffold: null
        tools: [Read, Glob, memory_search_with_experience]

      - name: EXPLORE
        description: "Gather evidence via investigation-agent"
        exit_gates:
          - type: subagent
            name: investigation-agent
            timing: during
            blocking: true
        memory: query
        scaffold: null
        tools: [Read, Grep, Glob, Bash, WebSearch]

      - name: CONCLUDE
        description: "Synthesize findings and spawn work items"
        exit_gates: []
        memory: store
        scaffold: null
        tools: [Edit, ingester_ingest, /new-adr, /new-plan]

      - name: CHAIN
        description: "Route to next work"
        exit_gates: []
        memory: null
        scaffold: null
        tools: []

    chain:
      terminal: false
      routing_strategy: routing_gate
      targets:
        - investigation-cycle
        - implementation-cycle
        - work-creation-cycle
      fallback: await_operator

  close-work-cycle:
    description: "VALIDATE->OBSERVE->ARCHIVE->MEMORY workflow for closure"
    node: close
    phases:
      - name: VALIDATE
        description: "Check DoD criteria"
        exit_gates:
          - type: skill
            name: dod-validation-cycle
            timing: pre
            blocking: true
        memory: null
        scaffold: null
        tools: [Read, Bash]

      - name: OBSERVE
        description: "Capture observations before archival"
        exit_gates: []
        memory: null
        scaffold:
          recipe: "scaffold-observations"
          args: ["{{work_id}}"]
          when: phase_start
        tools: [Edit]

      - name: ARCHIVE
        description: "Move to archive"
        exit_gates: []
        memory: null
        scaffold: null
        tools: [Bash]

      - name: MEMORY
        description: "Store closure summary"
        exit_gates: []
        memory: store
        scaffold: null
        tools: [ingester_ingest]

      - name: CHAIN
        description: "Route to next work"
        exit_gates: []
        memory: null
        scaffold: null
        tools: []

    chain:
      terminal: false
      routing_strategy: routing_gate
      targets:
        - investigation-cycle
        - implementation-cycle
        - work-creation-cycle
      fallback: await_operator

  work-creation-cycle:
    description: "VERIFY->POPULATE->READY workflow for new work items"
    node: backlog
    phases:
      - name: VERIFY
        description: "Validate work file exists"
        exit_gates:
          - type: gate
            name: work_file_exists
            timing: pre
            blocking: true
        memory: null
        scaffold: null
        tools: [Read, Glob]

      - name: POPULATE
        description: "Fill in Context and Deliverables"
        exit_gates:
          - type: gate
            name: no_placeholders
            timing: post
            blocking: true
        memory: query
        scaffold: null
        tools: [Edit, memory_search_with_experience]

      - name: READY
        description: "Mark ready for work"
        exit_gates: []
        memory: null
        scaffold: null
        tools: [Edit]

      - name: CHAIN
        description: "Route to appropriate cycle"
        exit_gates: []
        memory: null
        scaffold: null
        tools: []

    chain:
      terminal: false
      routing_strategy: confidence_based
      targets:
        - investigation-cycle      # INV-* prefix
        - implementation-cycle     # has spawned_by_investigation
        - reason                   # else
      fallback: await_operator

  checkpoint-cycle:
    description: "SCAFFOLD->FILL->VERIFY->CAPTURE->COMMIT workflow for session capture"
    node: null                      # Not tied to DAG node
    phases:
      - name: SCAFFOLD
        description: "Create checkpoint file"
        exit_gates: []
        memory: null
        scaffold:
          recipe: "scaffold checkpoint"
          args: ["{{session}}", "{{title}}"]
          when: phase_start
        tools: [Bash]

      - name: FILL
        description: "Populate checkpoint sections"
        exit_gates: []
        memory: null
        scaffold: null
        tools: [Edit]

      - name: VERIFY
        description: "Validate completion claims"
        exit_gates:
          - type: subagent
            name: anti-pattern-checker
            timing: post
            blocking: true
        memory: null
        scaffold: null
        tools: []

      - name: CAPTURE
        description: "Store learnings to memory"
        exit_gates: []
        memory: store
        scaffold: null
        tools: [ingester_ingest]

      - name: COMMIT
        description: "Git commit session"
        exit_gates: []
        memory: null
        scaffold: null
        tools: [Bash]

    chain:
      terminal: true
      routing_strategy: none
      targets: []
      fallback: null

  observation-triage-cycle:
    description: "SCAN->TRIAGE->PROMOTE workflow for observation processing"
    node: null
    phases:
      - name: SCAN
        description: "Find untriaged observations"
        exit_gates: []
        memory: null
        scaffold: null
        tools: [Bash, Glob]

      - name: TRIAGE
        description: "Categorize and prioritize observations"
        exit_gates: []
        memory: null
        scaffold: null
        tools: [AskUserQuestion, Edit]

      - name: PROMOTE
        description: "Create work items or store insights"
        exit_gates: []
        memory: store
        scaffold: null
        tools: [/new-work, ingester_ingest]

    chain:
      terminal: true
      routing_strategy: none
      targets: []
      fallback: null

  plan-authoring-cycle:
    description: "ANALYZE->AUTHOR->VALIDATE workflow for plan creation"
    node: plan
    phases:
      - name: ANALYZE
        description: "Understand context and requirements"
        exit_gates: []
        memory: query
        scaffold: null
        tools: [Read, Glob, memory_search_with_experience]

      - name: AUTHOR
        description: "Write plan with section order enforcement"
        exit_gates: []
        memory: null
        scaffold: null
        tools: [Edit]

      - name: VALIDATE
        description: "Check plan completeness"
        exit_gates:
          - type: skill
            name: plan-validation-cycle
            timing: post
            blocking: true
        memory: null
        scaffold: null
        tools: []

      - name: CHAIN
        description: "Route to implementation"
        exit_gates: []
        memory: null
        scaffold: null
        tools: []

    chain:
      terminal: false
      routing_strategy: routing_gate
      targets:
        - implementation-cycle
      fallback: await_operator
```

---

## Gates Registry (gates.yaml)

Separate file for gate check definitions:

```yaml
# .claude/haios/config/gates.yaml
version: "1.0"

gates:
  work_file_exists:
    description: "Work file WORK.md exists"
    check: "glob('docs/work/active/{{id}}/WORK.md').length > 0"

  no_placeholders:
    description: "Context/Deliverables have no placeholders"
    check: |
      content = read('docs/work/active/{{id}}/WORK.md')
      not content.contains('[Problem') and
      not content.contains('[Deliverable')

  tests_pass:
    description: "pytest returns exit code 0"
    check: "bash('pytest').exit_code == 0"

  why_captured:
    description: "Memory refs populated in work file"
    check: |
      yaml = parse_frontmatter('docs/work/active/{{id}}/WORK.md')
      len(yaml.memory_refs) > 0

  plan_file_exists:
    description: "Plan file exists for work item"
    check: "glob('docs/work/active/{{id}}/plans/PLAN.md').length > 0"

  # OBJECTIVE COMPLETION GATE (Session 150 - approved design)
  # Defense in depth: checkboxes + remaining work + anti-pattern check
  objective_complete:
    description: "Work item objective is fully met"
    composite: true
    checks:
      - name: deliverables_checked
        description: "All Deliverables items are checked [x]"
        check: |
          content = read('docs/work/active/{{id}}/WORK.md')
          deliverables = extract_section(content, '## Deliverables')
          unchecked = regex_count(deliverables, r'- \[ \]')
          unchecked == 0

      - name: no_remaining_work
        description: "No remaining work declared"
        check: |
          # Check work directory for files with "Remaining Work" sections
          files = glob('docs/work/active/{{id}}/*.md')
          for file in files:
            content = read(file)
            if has_section(content, '## Remaining Work'):
              items = extract_section(content, '## Remaining Work')
              # Empty or only contains "None" is acceptable
              if items.strip() and not items.contains('None'):
                return false
          return true

      - name: anti_pattern_check
        description: "Anti-pattern checker validates completion claims"
        type: subagent
        subagent: anti-pattern-checker
        timing: pre
        blocking: true
```

---

## Migration Path

### Phase 1: Create Config Files
1. Create `.claude/haios/config/cycle-definitions.yaml`
2. Create `.claude/haios/config/gates.yaml`
3. Validate against existing skills

### Phase 2: Thin Executor
1. Create `.claude/lib/cycle_executor.py`
2. Parse cycle-definitions.yaml
3. Route to appropriate phase

### Phase 3: Update Skills
1. Skills reference config for structure
2. Keep phase-specific logic in SKILL.md
3. Remove duplicated CHAIN logic

### Phase 4: Validate
1. Run each cycle end-to-end
2. Verify gates fire correctly
3. Verify memory integration works

---

*Schema definition from Session 150*
