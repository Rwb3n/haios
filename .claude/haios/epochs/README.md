# generated: 2026-01-20
# System Auto: last updated on: 2026-01-20T21:11:47
# Epochs Directory

## Purpose

Epochs contain **design and architecture**, not implementation.

---

## Hierarchy

```
Epoch (tight)
  └── Arc (volumous)
        └── Chapter (tight)
              └── Work Item (implementation)
```

| Level | Pressure | Contains |
|-------|----------|----------|
| **Epoch** | Tight | Mission, exit criteria, arc list |
| **Arc** | Volumous | Theme, architecture, chapter list |
| **Chapter** | Tight | Problem, requirements, success criteria |
| **Work Item** | N/A | Implementation (lives in docs/work/) |

---

## Key Principle

**Epochs are design. Work items are implementation.**

- Epoch files define WHAT and WHY
- Work items define HOW and execute
- Chapters bridge design to implementation

---

## File Types

| File | Template | Purpose |
|------|----------|---------|
| `EPOCH.md` | - | Epoch definition |
| `ARC.md` | `.claude/templates/arc.md` | Arc definition |
| `CH-NNN-name.md` | `.claude/templates/chapter.md` | Chapter specification |

---

## Chapter → Work Item Flow

```
Chapter (design)
    │
    ├── Approved by operator
    │
    └── Triaged into Work Items
            │
            ├── WORK-001: Implement R1
            ├── WORK-002: Implement R2
            └── WORK-003: Integration test
```

Chapters define requirements. Work items implement them.

---

## Directory Structure

```
epochs/
├── README.md                 # This file
├── E2_3/                     # Current epoch
│   ├── EPOCH.md
│   ├── arcs/
│   │   ├── configuration/
│   │   │   ├── ARC.md
│   │   │   ├── CH-001-discovery-root.md
│   │   │   └── ...
│   │   └── {other-arcs}/
│   ├── architecture/         # Cross-cutting architecture docs
│   └── observations/         # Session observations
└── archive/                  # Completed epochs
```

---

## Governance (Future)

- PreToolUse hook validates epoch file edits use templates
- Chapters require operator approval before work item creation
- Work items must reference parent chapter

---

## References

- @.claude/templates/arc.md
- @.claude/templates/chapter.md
- @.claude/haios/config/haios.yaml (epoch.current)
