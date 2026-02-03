# generated: 2026-01-18
# System Auto: last updated on: 2026-02-02T23:57:02
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

**State-Aware Capabilities (E2.5 - phases within lifecycles):**
- in EXPLORE phase (Investigation/Design): must allow unrestricted reading, note capture
- in SPECIFY phase (Design): must allow spec writing
- in CRITIQUE phase (Design): must allow critique invocation, revision
- in PLAN phase (Implementation): must allow plan writing
- in DO phase (Implementation): must BLOCK AskUser, must BLOCK spec-write, must allow only artifact-*
- in CHECK phase (Implementation): must allow verification, test execution
- in DONE phase (Implementation): must allow knowledge commit, work closure

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

## Lifecycle Requirements (E2.5 - Session 294)

*Updated from E2.4 "Flow Requirements" - lifecycles are now independent, not chained.*

**Independent Lifecycles:**
- must allow Investigation lifecycle: EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE
- must allow Design lifecycle: EXPLORE → SPECIFY → CRITIQUE → COMPLETE
- must allow Implementation lifecycle: PLAN → DO → CHECK → DONE
- must allow Validation lifecycle: VERIFY → JUDGE → REPORT
- must allow Triage lifecycle: SCAN → ASSESS → RANK → COMMIT

**Lifecycle Independence:**
- must allow each lifecycle to complete without chaining to next
- must allow pause points as valid completion states (S27 Breath Model)
- must allow batch mode (multiple items in same lifecycle phase)
- must treat chaining as caller choice, not callee side-effect

**Critique within Design Lifecycle:**
- must enforce critique as hard gate within Design lifecycle (SPECIFY → CRITIQUE)
- must block Design COMPLETE until critique verdict = PROCEED

**Queue Lifecycle (orthogonal):**
- must track queue position separately from lifecycle phase
- must allow: backlog → ready → active → done
- must allow work item to be `queue: done` without spawning next lifecycle
