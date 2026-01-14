# generated: 2025-12-17
# System Auto: last updated on: 2025-12-21 11:47:33
# HAIOS Reference Documentation

This directory contains reference documentation for on-demand loading.

## HAIOS-Specific References

Extracted from CLAUDE.md during E2-079:

| File | Lines | Contents |
|------|-------|----------|
| **OPERATIONS.md** | 86 | Commands, testing, MCP services |
| **GOVERNANCE.md** | 238 | Hooks, templates, lifecycle, memory tools |
| **ARCHITECTURE.md** | 91 | Tech stack, agent patterns, coordination |
| **CHECKLISTS.md** | 127 | Pre/post implementation, DoD, verification |

## Claude Code References

General Claude Code documentation for the `claude-code-guide` subagent:

| File | Lines | Contents |
|------|-------|----------|
| **SDK-REF.md** | 2,492 | Claude Agent SDK documentation |
| **SKILLS-REF.md** | 1,485 | Skill development guide |
| **HOOKS-REF.md** | 1,133 | Hook system documentation |
| **MCP-REF.md** | 801 | MCP server integration |
| **MARKETPLACE-REF.md** | 433 | Plugin marketplace |
| **PLUGINS-REF.md** | 395 | Plugin development |
| **TROUBLESHOOTING-REF.md** | 358 | Common issues and fixes |
| **SUBAGENTS-REF.md** | 345 | Subagent patterns |
| **COMMANDS-REF.md** | 272 | Slash command reference |
| **USER-CAUGHT-BUGS.md** | 25 | Known Claude Code bugs |

## Usage

```
# To read a reference file:
Read .claude/REFS/GOVERNANCE.md

# Or use @ notation:
@.claude/REFS/OPERATIONS.md
```

## Philosophy

This follows the L1/L3 progressive context pattern:
- **L1 (CLAUDE.md)**: Core identity, critical rules, governance triggers (~200 lines)
- **L3 (REFS/)**: Detailed reference material, loaded when needed

---
*Part of E2-079: CLAUDE.md De-bloat*
