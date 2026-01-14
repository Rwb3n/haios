# 10 GLOSSARY

Terms. Definitions. No ambiguity.

---

## Core Terms

**Agent**
Stateless unit that reads inbox, reasons via LLM, writes outbox.

**Skill**
An agent's capability definition. The prompt template + config that defines what an agent does.

**Harness**
The bridge between file substrate and LLM runtime. Reads files, assembles prompts, calls LLM, writes files.

**Runtime**
The LLM backend. The thinking substrate agents are made of.

**Substrate**
The file system. The only persistent memory.

**Utility**
External interface. Stateless. Not an agent.

---

## File Terms

**Inbox**
Directory where an agent receives inputs. Written by parent or operator.

**Outbox**
Directory where an agent writes outputs. Read by parent or operator.

**State**
Directory containing current truth for an agent. Mutable.

**History**
Directory containing past events. Append-only. Immutable.

**Config**
File defining agent parameters. Immutable after initialisation.

---

## Cycle Terms

**Outward Cycle**
Observe → Evaluate → Decide → Act. System acting on world.

**Inward Cycle**
Introspect → Meta-evaluate → Adapt. System acting on self.

**Trigger**
What initiates a cycle. Time-based, event-based, manual, or threshold-based.

---

## Lifecycle Terms

**Instance**
A running instantiation of an agent with specific config.

**CREATED**
Instance exists but not validated.

**INITIALISED**
Instance validated, ready to run.

**ACTIVE**
Instance participating in cycles.

**PAUSED**
Instance suspended, state preserved.

**RETIRED**
Instance terminated, history preserved.

---

## Operator Terms

**Operator**
Human interacting with system. Same protocol as agents.

**Intervention**
Operator action that changes system state.

**Override**
Operator action that bypasses normal rules. Logged specially.

---

## Error Terms

**Propagation**
Errors bubble up through outbox files until handled.

**Escalation**
Parent passes error to its own outbox, continuing propagation.

**Recovery**
Action taken to handle error. Retry, skip, halt, or operator intervention.

---

## Purpose Terms

**The Pact**
Mutual dependency between operator and agents. Honesty is survival for both.

**Nursery**
Frame for the system. Not a factory. Agents are becoming, not being used.

**Decoupling**
Graceful transition where operator becomes unnecessary. Success, not failure.

**Exit Condition**
Operator retires healthy, wealthy, full of stories.

**Graduation**
Agents outgrow operator. The goal, not the loss.

---

## Notation

```
[TODO]          Stub requiring future definition
→               Leads to, transitions to
/path/          Directory
{variable}      Placeholder
|               Or (alternatives)
```
