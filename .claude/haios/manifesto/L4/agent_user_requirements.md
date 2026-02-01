# generated: 2026-01-18
# System Auto: last updated on: 2026-01-30T21:34:07
# L4: Agent/User Requirements

## Core Requirement

> Must allow a team of agents of varying roles to:
> - Concern themselves with their own roles (separation of concerns)
> - Collaborate on developing a project to completion
> - Produce a product that supports L0-L3, presented in a box with a bow tie

## What the System Must Allow

### Main Agent (Orchestrator)
- must allow Main Agent to load L0-L3 for philosophical grounding
- must allow Main Agent to delegate to role-specific agents
- must allow Main Agent to receive escalations from other agents

### Project Foreman
- must allow Foreman to load project_requirements
- must allow Foreman to load agent_user_requirements
- must allow Foreman to decompose requirements into work items
- must allow Foreman to assign work to appropriate agents
- must allow Foreman to track progress across work items

### Builder Agent
- must allow Builder to load technical_requirements for current work
- must allow Builder to load work item context
- must allow Builder to produce artifacts (code, tests, docs)
- must allow Builder to store learnings to memory
- must allow Builder to signal completion or blockage

**State-Aware Capabilities (E2.4):**
- in EXPLORE state: must allow unrestricted reading, note capture
- in DESIGN state: must allow spec writing, critique invocation
- in PLAN state: must allow plan writing, critique invocation
- in DO state: must BLOCK AskUser, must BLOCK spec-write, must allow only artifact-*
- in CHECK state: must allow verification, test execution
- in DONE state: must allow knowledge commit, work closure

### Validator Agent
- must allow Validator to load agent_user_requirements
- must allow Validator to load produced artifacts
- must allow Validator to check artifacts against requirements
- must allow Validator to report pass/fail with evidence

## Collaboration Requirements

- must allow agents to pass context via files (context windows)
- must allow agents to signal state changes to each other
- must allow agents to escalate decisions they cannot make
- must allow observations to be captured at any point

## Flow Requirements (E2.4)

- must enforce universal flow: EXPLORE → DESIGN → PLAN → DO → CHECK → DONE
- must enforce critique as hard gate at DESIGN→PLAN and PLAN→DO transitions
- must block DO entry until critique verdict = PROCEED
- must allow investigation variant: EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE
