# Schema: Raw_Research_Artifact

**ID:** `schema-raw-research-artifact-v1.0`  
**Description:**  
This schema defines the structure for a pristine, untainted research artifact immediately after Stage 1 (Ingestion & Structuring) of the Rhiza protocol. Its purpose is to store the raw, scraped data in a standardized format with full provenance, before any analysis or interpretation occurs.

---

## 1. Top-Level Structure

The artifact is a single JSON object with two top-level keys: `metadata` and `payload`.

```json
{
  "metadata": { ... },
  "payload": { ... }
}
```

---

## 2. `metadata` Object

Contains all metadata related to the ingestion process and the artifact's identity.

| Key                    | Type                | Required | Description                                                                                      | Example                        |
|------------------------|---------------------|----------|--------------------------------------------------------------------------------------------------|--------------------------------|
| `artifact_id`          | String              | Yes      | A unique, system-generated ID for this artifact, typically `raw_research_artifact_<g>`.          | `raw_research_artifact_g1024`  |
| `paper_id`             | String              | Yes      | The canonical identifier of the paper from its source (e.g., arXiv ID, DOI). Used for idempotency checks. | `2401.12345`                   |
| `source_name`          | String              | Yes      | The name of the data source from which the paper was scraped.                                    | `arXiv`                        |
| `source_url`           | String (URI)        | Yes      | The exact URL from which the data was scraped.                                                   | `https://arxiv.org/abs/2401.12345` |
| `schema_version`       | String              | Yes      | The semantic version of this schema to which the artifact conforms.                              | `1.0`                          |
| `ingestion_timestamp`  | String (ISO 8601)   | Yes      | The UTC timestamp of when the ingestion was performed.                                           | `2025-07-11T22:30:00Z`         |
| `ingestion_agent_version` | String           | Yes      | The version of the specific ingestion script/adapter that created this artifact.                 | `arxiv_adapter_v1.1.0`         |
| `trace_id`             | String              | Yes      | The OpenTelemetry trace ID for the entire ingestion workflow run, linking this artifact to logs and metrics. | `abcdef1234567890`             |
| `_locked_payload`      | Boolean             | Yes      | A constraint lock (ADR-OS-010). Must be `true` upon creation, as the raw payload is immutable evidence and must never be altered. | `true`                         |

---

## 3. `payload` Object

Contains the structured, but uninterpreted, content scraped from the source. **All fields are strings.** The goal is to capture the raw text content from key sections.

| Key                | Type    | Required | Description                                                                                       |
|--------------------|---------|----------|---------------------------------------------------------------------------------------------------|
| `title`            | String  | Yes      | The full title of the paper.                                                                      |
| `authors`          | String  | Yes      | The list of authors as a single string, exactly as it appears on the source page.                 |
| `abstract`         | String  | Yes      | The full text of the abstract.                                                                    |
| `categories`       | String  | Yes      | The list of categories or subjects as a single string (e.g., `cs.DC, cs.AI`).                     |
| `publication_date` | String  | Yes      | The date of publication or submission as a string.                                                |
| `full_text_raw`    | String  | No       | The full text of the paper, extracted as plain text. Optional; may be omitted for some sources.   |
| `raw_html_content` | String  | No       | The raw HTML content of the source page. For deep forensic analysis; generally omitted from the primary artifact.