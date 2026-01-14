# 03 AGENTS

Agents all the way down.

---

## What is an Agent

An agent is: harness + prompt template + LLM call.

- Reads inbox
- Thinks (LLM)
- Writes outbox
- Dies

Stateless. Single cycle. No persistence except files.

---

## Skill Anatomy

```
skill-name/
├── SKILL.md          # Metadata + instructions
├── config.yaml       # Parameters
├── inbox/            # Inputs
├── outbox/           # Outputs
├── state/            # Persistent state (if any)
├── history/          # Append-only log
└── sub_agents/       # Children (optional)
```

---

## Invocation Protocol

Parent invokes child:

```
1. Parent writes to child/inbox/
2. Parent triggers child harness
3. Child reads inbox, thinks, writes outbox
4. Parent reads child/outbox/
5. Parent continues
```

Files only. No RPC. No message queues.

---

## Composition Rules

- Any agent can invoke sub-agents
- Depth is arbitrary
- No cycles (agent cannot invoke ancestor)
- Children cannot read parent state
- Children cannot write outside own outbox

---

## Agent Types

[TODO: Define common agent archetypes]

- Orchestrator
- Worker
- Evaluator
- Adaptor

---

## Self-Documenting Outputs

Every agent output must be readable by a cold-started LLM.

Test: "If an LLM reads only this file, can it act on it?"
