# generated: 2025-11-30
# System Auto: last updated on: 2025-11-30 19:56:48
# AP-STALE-FOOTER: Agents Reading Only Document Headers

> **Progressive Disclosure:** [Quick Reference](../README.md) -> [Strategic Overview](../epistemic_state.md) -> **Anti-Patterns**

---

## Pattern ID: AP-STALE-FOOTER

**Status:** ACTIVE
**Discovered:** Session 16 (2025-11-30)
**Severity:** MEDIUM

---

## Description

Agents have a tendency to read the top portions of documents (headers, summaries, first sections) and make updates there, while neglecting the bottom sections (footers, references, last-updated dates). This results in inconsistent documentation where headers claim one state but footers reflect an outdated state.

---

## Symptoms

- Document headers show current session but footers reference old sessions
- Test counts in summary sections differ from test counts in footer sections
- Last Updated dates at top don't match Last Updated dates at bottom
- Navigation links at top are current but bi-directional references at bottom are stale
- Progressive disclosure headers updated but footer navigation unchanged

---

## Root Cause

1. **Context window optimization** - agents prioritize reading top content to save tokens
2. **Task completion bias** - once header is updated, task feels "done"
3. **No systematic bottom-to-top review protocol**
4. **Read tool defaults** - using offset/limit focuses on specific sections

---

## Prevention

1. **Always read FULL document before editing** - use Read tool without offset/limit parameters
2. **Add Table of Contents** at document top with section anchors
3. **Use progressive disclosure headers** that state "YOU ARE HERE"
4. **Include bi-directional reference sections** at document END
5. **After editing top sections**, EXPLICITLY scroll to and verify bottom sections
6. **Include Last Updated timestamps** in BOTH header and footer
7. **Use systematic document review** - top-to-bottom then bottom-to-top

---

## Detection

```bash
# Check for Last Updated consistency
grep -rn "Last Updated" docs/ | head -20

# Check for session number consistency
grep -rn "Session [0-9]" docs/ | sort

# Verify footer sections exist
grep -l "Documents That Link Here" docs/*.md
```

---

## Example: Before (Anti-Pattern)

```markdown
# Document Title
**Last Updated:** 2025-11-30  <!-- Updated -->

## Content
... (updated content) ...

---
**Last Updated:** 2025-11-28  <!-- STALE - not updated -->
```

## Example: After (Correct)

```markdown
# Document Title
**Last Updated:** 2025-11-30

## Content
... (updated content) ...

---
## Bi-directional References
### This Document Links To:
- [file1.md](file1.md)

### Documents That Link Here:
- [file2.md](file2.md)

---
**Last Updated:** 2025-11-30  <!-- CONSISTENT -->
```

---

## Related Patterns

| Pattern | Relationship |
|---------|--------------|
| AP-CONTEXT-LOSS | Similar - information lost across context windows |
| Progressive Disclosure | Mitigation - systematic navigation structure |
| Bi-directional References | Mitigation - forces review of document end |

---

## References

- Discovered during Session 16 documentation architecture update
- [docs/README.md](../README.md) - Example of correct implementation
- [docs/epistemic_state.md](../epistemic_state.md) - Example with bi-directional refs

---

**Document Version:** 1.0
**Created:** 2025-11-30 (Session 16)
