---
template: implementation_plan
status: complete
date: 2025-12-23
backlog_id: E2-145
title: "Validate Script Section Enforcement"
author: Hephaestus
lifecycle_phase: plan
session: 103
spawned_by: E2-140
version: "1.5"
generated: 2025-12-23
last_updated: 2025-12-23T13:03:59
---
# Implementation Plan: Validate Script Section Enforcement

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.
-->

---

## Goal

Template validation will mechanically enforce section requirements (L4), detecting both missing sections AND placeholder-only content, upgrading from L2 (documented suggestion) to L4 (automated enforcement).

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/lib/validate.py` |
| Lines of code affected | ~50 | Add investigation sections, placeholder detection |
| New files to create | 0 | Extending existing module |
| Tests to write | 5 | Investigation sections, placeholder detection |
| Dependencies | 0 | Self-contained validation logic |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single file, existing function |
| Risk of regression | Low | Additive, existing tests cover current behavior |
| External dependencies | Low | Pure Python string matching |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 15 min | High |
| Add investigation sections | 10 min | High |
| Add placeholder detection | 20 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/validate.py:79-87 - investigation template registry
        "investigation": {
            "required_fields": ["template", "status", "date", "backlog_id"],
            "optional_fields": [...],
            "allowed_status": ["draft", "active", "pending", "closed", "complete", "archived"],
            "expected_sections": [],  # <-- EMPTY! No section enforcement
        },
```

**Behavior:** Investigation files have no section enforcement. Sections can be deleted silently.

**Result:** Governance relies on L2 (operator remembers). Session 102 found investigations with deleted sections.

### Desired State

```python
# .claude/lib/validate.py - investigation template with expected sections
        "investigation": {
            ...
            "expected_sections": [
                "Context",
                "Prior Work Query",
                "Objective",
                "Scope",
                "Hypotheses",
                "Exploration Plan",
                "Evidence Collection",
                "Findings",
                "Spawned Work Items",
                "Ground Truth Verification",
                "Closure Checklist",
            ],
        },
```

Plus placeholder detection:
```python
# .claude/lib/validate.py - new function
def is_placeholder_content(section_content: str) -> bool:
    """Detect placeholder-only content in sections."""
    patterns = [
        r'\[.*?\]',      # [bracketed placeholders]
        r'\bTODO\b',     # TODO markers
        r'\bTBD\b',      # TBD markers
        r'\bFIXME\b',    # FIXME markers
    ]
    # Strip markdown formatting and check
    ...
```

**Behavior:** Validation fails if investigation section is missing/has placeholder content without SKIPPED rationale.

**Result:** L4 mechanical enforcement - cannot save incomplete investigation without explicit skip.

---

## Tests First (TDD)

### Test 1: Investigation Template Has Expected Sections
```python
def test_investigation_has_expected_sections(self):
    """Investigation template should have expected_sections defined."""
    from validate import get_template_registry

    registry = get_template_registry()
    sections = registry["investigation"]["expected_sections"]

    assert len(sections) > 0
    assert "Findings" in sections
    assert "Hypotheses" in sections
    assert "Spawned Work Items" in sections
```

### Test 2: Placeholder Detection Basic
```python
def test_is_placeholder_content_detects_brackets(self):
    """Should detect [placeholder] patterns as placeholder content."""
    from validate import is_placeholder_content

    assert is_placeholder_content("[Document findings here]") == True
    assert is_placeholder_content("[TODO: fill in]") == True
    assert is_placeholder_content("Actual content without brackets") == False
```

### Test 3: Placeholder Detection TODO/TBD
```python
def test_is_placeholder_content_detects_todo(self):
    """Should detect TODO and TBD markers."""
    from validate import is_placeholder_content

    assert is_placeholder_content("TODO: implement this") == True
    assert is_placeholder_content("TBD") == True
    assert is_placeholder_content("This is done") == False
```

### Test 4: Section Validation Rejects Placeholder-Only
```python
def test_section_with_only_placeholder_fails(self, tmp_path):
    """Section with only placeholder content should fail validation."""
    from validate import check_section_coverage

    content = '''---
template: implementation_plan
status: draft
date: 2025-12-23
backlog_id: E2-TEST
---
# Test Plan

## Goal

[One sentence: What capability will exist?]

## Effort Estimation (Ground Truth)

Actual content here with metrics.
'''
    result = check_section_coverage("implementation_plan", content)

    assert result["all_covered"] == False
    assert "Goal" in result["placeholder_sections"]
```

### Test 5: Skip Rationale Still Valid
```python
def test_skip_rationale_bypasses_placeholder_check(self, tmp_path):
    """SKIPPED rationale should bypass placeholder check."""
    from validate import check_section_coverage

    content = '''...
## Goal

**SKIPPED:** Trivial fix, no formal goal needed
'''
    result = check_section_coverage("implementation_plan", content)

    assert "Goal" in result["skipped_sections"]
    assert "Goal" not in result.get("placeholder_sections", [])
```

---

## Detailed Design

### Exact Code Change 1: Add Investigation Expected Sections

**File:** `.claude/lib/validate.py`
**Location:** Lines 79-87 in `get_template_registry()`

**Current Code:**
```python
        "investigation": {
            "required_fields": ["template", "status", "date", "backlog_id"],
            "optional_fields": [
                "title", "author", "session", "lifecycle_phase", "subtype",
                "spawned_by", "spawns", "blocked_by", "related", "milestone",
            ],
            "allowed_status": ["draft", "active", "pending", "closed", "complete", "archived"],
            "expected_sections": [],  # Investigations have flexible structure
        },
```

**Changed Code:**
```python
        "investigation": {
            "required_fields": ["template", "status", "date", "backlog_id"],
            "optional_fields": [
                "title", "author", "session", "lifecycle_phase", "subtype",
                "spawned_by", "spawns", "blocked_by", "related", "milestone",
                "memory_refs",
            ],
            "allowed_status": ["draft", "active", "pending", "closed", "complete", "archived"],
            "expected_sections": [
                "Context",
                "Prior Work Query",
                "Objective",
                "Scope",
                "Hypotheses",
                "Exploration Plan",
                "Evidence Collection",
                "Findings",
                "Spawned Work Items",
                "Ground Truth Verification",
                "Closure Checklist",
            ],
        },
```

### Exact Code Change 2: Add Placeholder Detection Function

**File:** `.claude/lib/validate.py`
**Location:** After `extract_sections()` function (~line 242)

**New Code:**
```python
def is_placeholder_content(text: str) -> bool:
    """Detect if text is placeholder-only content.

    Placeholder patterns:
    - [bracketed text] - common template placeholder
    - TODO, TBD, FIXME - work markers
    - Very short content (<20 chars after stripping)

    Args:
        text: Section content to check

    Returns:
        True if content appears to be placeholder-only.
    """
    if not text:
        return True

    # Strip markdown formatting
    stripped = re.sub(r'[#*_`\->\n\r]', ' ', text).strip()

    # Very short content is likely placeholder
    if len(stripped) < 20:
        return True

    # Check for placeholder patterns
    # Content is placeholder if ONLY placeholder patterns exist
    non_placeholder = re.sub(r'\[.*?\]', '', stripped)  # Remove [brackets]
    non_placeholder = re.sub(r'\bTODO\b.*', '', non_placeholder, flags=re.IGNORECASE)
    non_placeholder = re.sub(r'\bTBD\b.*', '', non_placeholder, flags=re.IGNORECASE)
    non_placeholder = re.sub(r'\bFIXME\b.*', '', non_placeholder, flags=re.IGNORECASE)
    non_placeholder = non_placeholder.strip()

    # If nothing left after removing placeholders, it's placeholder content
    return len(non_placeholder) < 20
```

### Exact Code Change 3: Enhance check_section_coverage()

**File:** `.claude/lib/validate.py`
**Location:** Lines 244-293 in `check_section_coverage()`

**Add to result dict:**
```python
    result = {
        "all_covered": True,
        "missing_sections": [],
        "skipped_sections": [],
        "present_sections": [],
        "placeholder_sections": [],  # <-- NEW
    }
```

**Add placeholder check in the section loop:**
```python
            if match:
                section_content = match.group(1)
                # Check for SKIPPED marker (case-insensitive)
                if re.search(r"\*\*SKIPPED:\*\*", section_content, re.IGNORECASE):
                    result["skipped_sections"].append(section)
                elif is_placeholder_content(section_content):
                    # Section exists but only has placeholder content
                    result["placeholder_sections"].append(section)
                    result["all_covered"] = False
                else:
                    result["present_sections"].append(section)
```

### Call Chain Context

```
PostToolUse hook
    |
    +-> validate.py:validate_template()
            |
            +-> check_section_coverage()
            |       |
            |       +-> get_expected_sections()
            |       +-> extract_sections()
            |       +-> is_placeholder_content()  # <-- NEW
            |
            +-> Returns errors if sections missing/placeholder
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| 11 sections for investigation | Exclude "Design Outputs", "Session Progress", "References" | These are optional per template comments |
| 20-char minimum threshold | After stripping placeholders | Short content is likely incomplete |
| Case-insensitive TODO/TBD | `re.IGNORECASE` | Catch all variants |
| SKIPPED bypasses placeholder check | Check SKIPPED first | Explicit skip > mechanical detection |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Section with code block containing TODO | May false positive | Acceptable - rare |
| Legitimate short section | SKIPPED rationale | Test 5 |
| Empty section | is_placeholder returns True | Test 2 |
| Section with only markdown formatting | Strip before check | Implicit |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add tests to `tests/test_lib_validate.py`
- [ ] Verify all 5 tests fail (red)

### Step 2: Add Investigation Expected Sections
- [ ] Update `get_template_registry()` with 11 sections
- [ ] Add `memory_refs` to optional_fields
- [ ] Test 1 passes (green)

### Step 3: Add is_placeholder_content Function
- [ ] Add function after `extract_sections()`
- [ ] Tests 2, 3 pass (green)

### Step 4: Enhance check_section_coverage
- [ ] Add `placeholder_sections` to result
- [ ] Add placeholder check in section loop
- [ ] Tests 4, 5 pass (green)

### Step 5: Integration Verification
- [ ] All tests pass: `pytest tests/test_lib_validate.py -v`
- [ ] Full suite: `pytest tests/ -v`

### Step 6: README Sync
**SKIPPED:** No new files, existing README at `.claude/lib/README.md` doesn't need update

---

## Verification

- [ ] Tests pass: `pytest tests/test_lib_validate.py -v`
- [ ] Full suite passes
- [ ] Demo: Run `just validate` on an investigation with placeholders

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| False positive on code examples | Low | Check for SKIPPED first, code blocks rare in sections |
| Breaks existing investigations | Medium | Add sections incrementally, existing files grandfathered |
| Performance on large files | Low | Regex is fast, only runs on Write |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 103 | 2025-12-23 | - | Plan created | Ready for next session |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/validate.py` | `is_placeholder_content()` exists, investigation has sections | [ ] | |
| `tests/test_lib_validate.py` | 5 new tests exist and pass | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_lib_validate.py -v -k "placeholder or investigation"
# Expected: 5+ tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- **Spawned by:** E2-140 (plan audit revealed gap)
- **Related:** Session 102 checkpoint (section skip discussion)
- **Pattern:** L2 → L4 upgrade (documented suggestion to mechanical enforcement)
- **Template:** `.claude/templates/investigation.md` (source of section list)

---
