# ADR Documentation Issue Plan

## Overview
This plan addresses critical documentation issues identified in the ADR validation report. Issues are prioritized by severity and impact on system trust and usability.

## Issue Prioritization

### 🔴 CRITICAL (Blocks Trust & Understanding)
Issues that fundamentally mislead users about system behavior and violate HAiOS's evidence-based principles.

### 🟡 HIGH (Documentation Debt)
Issues that create confusion and maintenance burden but don't block system understanding.

### 🟢 MEDIUM (Process Improvements)
Issues that improve long-term maintainability and prevent future problems.

---

## Issue Inventory

### 🔴 ISSUE-001: ADR-OS-018 Title/Content Mismatch
**Severity**: CRITICAL  
**Impact**: Completely misleading - claims to document persistence but contains security controls  
**Root Cause**: Apparent copy-paste error or major content refactoring without title update  

**Resolution Steps**:
1. Determine intended purpose of ADR-OS-018
2. Option A: If security controls are correct content:
   - Rename to "ADR-OS-018: Foundational Security Controls & Process Isolation"
   - Update README.md index entry
   - Create new ADR for actual "Execution Status Persistence & Recovery"
3. Option B: If persistence is correct topic:
   - Move current security content to new ADR-OS-043
   - Write proper persistence & recovery content for ADR-OS-018
4. Update all cross-references to ADR-OS-018

**Verification**: Title matches content, no security content in persistence ADR

---

### 🔴 ISSUE-002: Framework Copy-Paste Errors in ADR-OS-019
**Severity**: CRITICAL  
**Impact**: Framework compliance sections reference completely unrelated frameworks  
**Root Cause**: Copy-paste from different ADR without updating framework references  

**Resolution Steps**:
1. Remove incorrect frameworks:
   - Event-driven Architecture v1.0
   - Event Ordering and Causality v1.0
2. Add correct frameworks for Observability & Budget Governance:
   - Monitoring & Observability v1.0
   - Resource Management v1.0
   - Cost Control v1.0
3. Write proper compliance proofs for each framework
4. Add self-critiques relevant to observability challenges

**Verification**: All frameworks directly relate to observability and budget governance

---

### 🔴 ISSUE-003: Framework Copy-Paste Errors in ADR-OS-020
**Severity**: CRITICAL  
**Impact**: Framework compliance sections reference agent design instead of runtime modes  
**Root Cause**: Copy-paste from agent-related ADR  

**Resolution Steps**:
1. Remove incorrect frameworks:
   - Agent Card Design Principles v1.0
   - Human-Centered Design v1.0
2. Add correct frameworks for Runtime Modes & DevEx:
   - Developer Experience v1.0
   - Mode Switching v1.0
   - Safety vs Velocity Trade-offs v1.0
3. Write proper compliance proofs for each framework
4. Add self-critiques about mode switching risks

**Verification**: All frameworks directly relate to runtime modes and developer experience

---

### 🟡 ISSUE-004: Clarifications INDEX.md Severely Outdated
**Severity**: HIGH  
**Impact**: Makes 23 clarification documents undiscoverable  
**Root Cause**: Manual index maintenance not keeping pace with clarification creation  

**Resolution Steps**:
1. Audit all clarification files (found 31 total)
2. Update INDEX.md with entries for all 31 clarifications
3. For each clarification add:
   - Title and ADR reference
   - Brief description of clarification topic
   - Link to clarification file
4. Update global event counter reference (currently shows g=70)
5. Add "Last Updated" timestamp to INDEX.md

**Verification**: INDEX.md lists all clarification files with proper descriptions

---

### 🟡 ISSUE-005: README.md Index Missing Recent ADRs
**Severity**: HIGH  
**Impact**: New architectural decisions (ADRs 040-042) are undiscoverable  
**Root Cause**: Manual index maintenance lag  

**Resolution Steps**:
1. Add entries for ADRs 040-042 to appropriate sections:
   - ADR-OS-040 → Quality, Governance & Meta-Architecture
   - ADR-OS-041 → Agent & Tool Management
   - ADR-OS-042 → Core Concepts & Data Models
2. Update status of ADRs 033-035 if no longer "PROPOSED"
3. Fix ADR-OS-018 description based on ISSUE-001 resolution
4. Add "Last Updated" timestamp to README.md

**Verification**: All 42 ADRs listed with correct descriptions and categories

---

### 🟢 ISSUE-006: Create Automated Documentation Validation
**Severity**: MEDIUM  
**Impact**: Prevents future documentation drift  
**Root Cause**: Manual processes without validation  

**Resolution Steps**:
1. Create validation script that checks:
   - ADR title matches first heading in file
   - Framework sections reference frameworks from registry
   - All ADR files have index entries
   - All clarification files have index entries
2. Add to CI pipeline as required check
3. Create auto-generation script for index files
4. Document the validation process

**Verification**: CI prevents merge of inconsistent documentation

---

## Implementation Plan

### Phase 1: Critical Fixes (Immediate)
1. [ ] ISSUE-001: Fix ADR-OS-018 mismatch
2. [ ] ISSUE-002: Fix ADR-OS-019 frameworks
3. [ ] ISSUE-003: Fix ADR-OS-020 frameworks

### Phase 2: Index Updates (This Week)
4. [ ] ISSUE-004: Update clarifications INDEX.md
5. [ ] ISSUE-005: Update README.md with all ADRs

### Phase 3: Process Improvements (Next Sprint)
6. [ ] ISSUE-006: Implement automated validation

## Success Criteria
- All ADR titles accurately describe their content
- All framework references are relevant to the ADR topic
- All documentation is discoverable through index files
- Automated validation prevents future drift

## Notes
- These issues violate HAiOS's core principle of "Evidence over Declaration"
- Documentation quality directly impacts trust in the system
- Automation is essential to maintain documentation at scale