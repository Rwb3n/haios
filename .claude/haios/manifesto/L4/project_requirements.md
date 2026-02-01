# generated: 2026-01-18
# System Auto: last updated on: 2026-01-30T21:33:31
# L4: Project Requirements

## What HAIOS IS

HAIOS is a **multi-agent operational framework** that transforms documentation into working products.

```
INPUT:  Corpus of documents (specs, designs, requirements)
PROCESS: Team of agents collaborating by role
OUTPUT: Functional product (aligned to L0-L3 manifesto)
```

## How HAIOS Works (E2.4)

The system operates through a five-layer hierarchy:

```
PRINCIPLES       (WHY)   - Beliefs, values (L0-L3)
WAYS OF WORKING  (HOW)   - Patterns, flows, transformations
CEREMONIES       (WHEN)  - Side-effect boundaries (commits, checkpoints)
ACTIVITIES       (WHAT)  - Governed primitives per state
ASSETS           (OUTPUT)- Immutable artifacts
```

See technical_requirements.md for implementation details.

## The Portability Test

> Can you drop `.claude/haios/` into a fresh workspace with a corpus of docs and have it produce a working product?

This is the success criterion.

## Current Project: HAIOS Bootstrap

The first project is building HAIOS itself. The corpus is:
- L0-L3 manifesto (what "good" looks like)
- Architecture docs (S20, S22, S26)
- Epoch/Arc definitions

The product is: a portable multi-agent framework.
