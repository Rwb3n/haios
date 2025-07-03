# Schema: Concept_Extraction_Report

**ID:** `schema-concept-extraction-report-v1.0`  
**Description:** This schema defines the structure for the intermediate artifact produced by Stage 3 (Deep Analysis & Concept Extraction) of the Rhiza protocol. Its purpose is to store the "crystal seeds"—the core concepts, algorithms, or proofs—that have been objectively extracted from a research paper, before they are mapped to internal HAiOS problems.

---

## 1. Top-Level Structure

The artifact is a single JSON object:

```json
{
  "metadata": { ... },
  "extracted_concepts": [ ... ]
}
```

---

## 2. `metadata` Object

Contains metadata linking this analysis back to its source.

| Key                   | Type         | Required | Description                                                        | Example                      |
|-----------------------|--------------|----------|--------------------------------------------------------------------|------------------------------|
| report_id             | String       | Yes      | A unique, system-generated ID for this report, typically concept_report_<g>. | concept_report_g1025         |
| source_artifact_id    | String       | Yes      | The artifact_id of the Raw_Research_Artifact that was analyzed.    | raw_research_artifact_g1024  |
| source_paper_id       | String       | Yes      | The paper_id of the source paper, for convenience.                 | 2401.12345                   |
| schema_version        | String       | Yes      | The semantic version of this schema.                               | 1.0                          |
| analysis_timestamp    | String (ISO 8601) | Yes | The UTC timestamp of when the analysis was completed.              | 2025-07-11T23:00:00Z         |
| analysis_agent_version| String       | Yes      | The version of the "Deep Analysis" agent/flow that created this report. | deep_analysis_flow_v1.0.0    |
| trace_id              | String       | Yes      | The OpenTelemetry trace ID for the analysis workflow run.          | fedcba0987654321             |

---

## 3. `extracted_concepts` Array

An array of objects, where each object represents one "crystal seed" extracted from the paper.

Each object in the array has the following structure:

| Key             | Type                | Required | Description                                                                                                   |
|-----------------|---------------------|----------|---------------------------------------------------------------------------------------------------------------|
| concept_id      | String              | Yes      | A locally unique identifier for the concept within this report (e.g., concept_1, concept_2).                  |
| concept_name    | String              | Yes      | A short, descriptive name for the concept (e.g., "Hierarchical Consensus," "Semantic Voting").               |
| summary         | String              | Yes      | A concise, one-paragraph summary of the concept, written in objective terms. It should explain what the concept is, not how we might use it. |
| type            | String (Enum)       | Yes      | The category of the concept. Must be one of: `ALGORITHM`, `PROTOCOL`, `ARCHITECTURE`, `PROOF`, `THEORETICAL_MODEL`, `DATA_STRUCTURE`, `METHODOLOGY`. |
| relevance_quote | String              | Yes      | A direct quote from the source paper's full text that best encapsulates or defines this concept. This provides direct, verifiable evidence for the extraction. |
| initial_keywords| Array of Strings    | Yes      | A list of 5-10 keywords associated with this concept, extracted from the paper.                               |

---