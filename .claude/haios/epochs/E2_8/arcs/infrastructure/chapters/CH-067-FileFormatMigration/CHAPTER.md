---
id: CH-067
name: File Format Migration
arc: infrastructure
epoch: E2.8
status: Active
work_items:
- id: WORK-244
  title: CHAPTER.md YAML Frontmatter Migration (Phase 1)
  status: Active
  type: implementation
- id: WORK-245
  title: ARC.md YAML Frontmatter Migration (Phase 2)
  status: Active
  type: implementation
exit_criteria:
- text: CHAPTER.md files have YAML frontmatter; consumers read frontmatter instead
    of regex
  checked: false
- text: ARC.md files have YAML frontmatter; 4 duplicate chapter table parsers eliminated
  checked: false
- text: All existing tests pass after migration (backward-compatible fallback)
  checked: false
- text: Zero regex parsing of machine-relevant fields in hierarchy files
  checked: false
dependencies: []
---
# generated: 2026-03-07
# System Auto: last updated on: 2026-03-07T00:33:00
# Chapter: FileFormatMigration

## Chapter Definition

**Chapter ID:** CH-067
**Arc:** infrastructure
**Epoch:** E2.8
**Name:** File Format Migration
**Status:** Active

---

## Purpose

Migrate hierarchy files (CHAPTER.md, ARC.md, EPOCH.md) from unstructured bold-markdown to YAML frontmatter. Eliminates 9 fragmented regex parsers across 5 consumer modules, replacing them with standard frontmatter reads. Phased: CHAPTER first (highest fragility), ARC second (highest deduplication), EPOCH third (minimal fields, deferred).

Spawned from WORK-240 investigation findings (mem:89402-89407).

---

## Work Items

| ID | Title | Status | Type |
|----|-------|--------|------|
| WORK-244 | CHAPTER.md YAML Frontmatter Migration (Phase 1) | Complete | implementation |
| WORK-245 | ARC.md YAML Frontmatter Migration (Phase 2) | Active | implementation |

---

## Exit Criteria

- [ ] CHAPTER.md files have YAML frontmatter; consumers read frontmatter instead of regex
- [ ] ARC.md files have YAML frontmatter; 4 duplicate chapter table parsers eliminated
- [ ] All existing tests pass after migration (backward-compatible fallback)
- [ ] Zero regex parsing of machine-relevant fields in hierarchy files

---

## Dependencies

| Direction | Target | Reason |
|-----------|--------|--------|
| None | - | No inbound or outbound dependencies |

---

## References

- @.claude/haios/epochs/E2_8/arcs/infrastructure/ARC.md (parent arc)
- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- @docs/work/active/WORK-240/WORK.md (spawning investigation)
- Memory: 89402-89407 (WORK-240 investigation findings)
