# ADR Clarification Record: {{ADR-ID}}

## 1  |  Clarifying Question

<!-- question here -->

## 2. Final Consensus Summary
<!-- This section is completed by the Scribe AFTER the dialogue is finished. -->
<!-- It is a concise, 1-3 paragraph summary of the final, accepted protocol or solution. -->
<!-- It replaces the old, pre-filled "Summary" section. -->

## 3. Final Context & Assumptions
<!-- Also completed by the Scribe post-dialogue. This captures the FINAL agreed-upon context. -->

### 3.1. Key Assumptions
<!-- List the core assumptions the final solution rests upon. -->
- *Assumption 1...*
- *Assumption 2...*

### 3.2. Dependencies
<!-- List the hard dependencies for this solution to work. -->
- *ADR-OS-XXX must be implemented first.*
- *Relies on the `BPS` side-car service.*

### 3.3. Risks & Mitigations
<!-- List the identified risks of the final solution and their agreed-upon mitigations. -->
- **Risk:** *[Identified risk, e.g., "BPS becomes a single point of failure."]*
  - **Mitigation:** *[Agreed mitigation, e.g., "BPS must be deployed in a 3-node HA configuration with Raft consensus."]*

---
<!-- The rest of the document follows from here -->
## 4. Clarification Question
<!-- The question that initiated the dialogue. -->

## 5. Full Dialogue Record (Reviews & Dissents)
<!-- The entire turn-by-turn conversation is placed here. -->

### Architect-1 (g*) — Initial Proposal
> ...

### Architect-2 (g*) — Review & Dissent
> ...

## 6. Canonization & Integration Directives
<!-- This section is completed by the Scribe *after* "No Further Dissent" is declared. It serves as the formal "commit message" for integrating the new knowledge from this clarification into the main HAiOS architectural canon. -->

### 6.1 Synthesis of Final Consensus
<!-- A concise, 1-3 paragraph summary of the final, accepted protocol or solution that was forged in the dialogue. This is the human-readable "what we decided". -->

### 6.2 Architectural Artifacts to be Modified
<!-- A checklist of specific, addressable artifacts that MUST be updated to reflect the consensus. This creates a formal work queue. -->

| Artifact ID / Path                               | Type of Change Required (CREATE, UPDATE, DEPRECATE) | Summary of Change                                                                      |
|--------------------------------------------------|---------------------------------------------------|----------------------------------------------------------------------------------------|

### 6.3 New Terminology for Global Glossary
<!-- A list of new terms introduced in this clarification that must be added to the project's global glossary to prevent ambiguity. -->

| Term | Definition |
|------|------------|
