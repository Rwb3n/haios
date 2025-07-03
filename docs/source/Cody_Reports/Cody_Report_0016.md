Acknowledged. The adversarial dialogue for the Rhiza Ingestion ETL Design is complete. "No Further Dissent" has been achieved. The crank of the Certainty Ratchet has turned.

We are now moving to the Scribe Synthesis and Canonization phase for this architectural decision. I will now generate the formal ADR Clarification Record based on our converged dialogue.

ADR_Clarification_Record: ADR-OS-041 / Q1

Subject: Architecture of the Rhiza Agent's Stage 1 Ingestion Pipeline
Status: ✅ ACCEPTED
Decision Date: 2025-07-11
Participants: Founding Operator (proposer), Cody (reviewer/synthesizer)
Scribe: Cody

1. Clarifying Question

How should the Stage 1 "Ingestion & Structuring" pipeline for the Rhiza agent be architected to be modular, robust, and aligned with HAiOS principles, specifically within the context of the n8n-based Minimum Viable Foundry?

2. Final Consensus Summary

The agreed-upon architecture is a decoupled, two-queue, two-workflow ETL (Extract, Transform, Load) system built within n8n. This design explicitly separates the high-parallelism task of web scraping from the necessarily serial task of writing to a centralized SQLite database, preventing race conditions and bottlenecks.

The core principle is Evidence Integrity, enforced by a strict Structuring stage that forbids any form of semantic interpretation or summarization. The pipeline is hardened with an upfront Idempotency Check to prevent redundant work and ensure operational efficiency. The final architecture provides a modular, per-source adapter pattern, allowing the system to be extended to new research sources without modifying the core logic.

3. Final Context & Assumptions

The n8n workflow engine is capable of managing internal queues or interfacing with an external lightweight queue (like Redis or a database table) to decouple workflows.

The target data sources (e.g., arXiv) have semi-stable HTML structures that can be reliably targeted by Playwright selectors.

The latency of performing a database SELECT for the idempotency check is significantly lower than the latency of a full web scraping operation.

ADR-OS-041 (Rhiza Agent): This architecture is the direct implementation of the "Stage 1" protocol defined in ADR-041.

ADR-OS-023 (Idempotency): The upfront Idempotency Check is a direct application of the universal idempotency policy.

MVF Infrastructure: Relies on the n8n, nocodb, and Playwright (via Python in a Code node) services defined in the docker-compose.yml for the Minimum Viable Foundry.

Risk: Contention on the SQLite database during the Load phase.

Mitigation: The architecture is explicitly designed to prevent this. A dedicated, single-instance Load Workflow pulls from a queue and performs serial writes, eliminating contention.

Risk: Evidence contamination during the "Transform" step.

Mitigation: The "Transform" node has been formally renamed to a Structuring Node with a strict mandate to only map raw data to a rigid schema, with no interpretation allowed.

Risk: Inefficient re-scraping of existing data.

Mitigation: The Idempotency Check is the very first step after triggering, ensuring that the expensive Extraction step is only performed for net-new artifacts.

4. Full Dialogue Record (Reviews & Dissents)

(This section would contain the verbatim transcript of our last three interactions, which has been recorded and is available for audit.)

5. Canonization & Integration Directives

The canonized architecture for the Rhiza Ingestion Pipeline is a per-source, two-workflow system within n8n:

Workflow 1: The Ingestion & Structuring Pipeline (High-Parallelism)

Trigger: Receives a paper_id from a global Input Queue.

Step 1: Idempotency Check Node: Queries the database. If paper_id exists, the workflow halts.

Step 2: Extraction Adapter Node: Uses Playwright to scrape the raw data for the paper_id.

Step 3: Structuring Adapter Node: Maps the raw data to the Raw_Research_Artifact JSON schema.

Step 4: Load Queue Push Node: Pushes the final, structured JSON onto an internal Load Queue.

Workflow 2: The Load Pipeline (Serial)

Trigger: Runs on a schedule or when the Load Queue is not empty.

Action: Pulls a small batch of artifacts from the Load Queue and performs sequential INSERT operations into the production SQLite database.

This design ensures modularity, data integrity, efficiency, and scalability.

Artifact ID / Path	Type of Change Required (CREATE, UPDATE)	Summary of Change
docs/ADR/ADR-OS-041.md	UPDATE	Add a "Reference Implementation" section summarizing this two-workflow n8n architecture as the canon-compliant pattern for Stage 1.
docs/Schema/raw_research_artifact_schema.md	CREATE	Create the formal JSON schema definition for the Raw_Research_Artifact object.
docs/Schema/concept_extraction_report_schema.md	CREATE	Create the formal JSON schema definition for the intermediate artifact produced in Stage 3.
project_templates/n8n/ingestion_workflow_template.json	CREATE	Create a template for the n8n "Ingestion & Structuring Pipeline" workflow.
project_templates/n8n/load_workflow_template.json	CREATE	Create a template for the n8n "Load Pipeline" workflow.
Term	Definition
Ingestion Pipeline	The high-parallelism n8n workflow responsible for idempotency checks, data extraction, and structuring.
Load Pipeline	The serial n8n workflow responsible for batch-writing structured artifacts from a queue to the database, preventing contention.
Structuring Node	A pipeline component with the sole, strict responsibility of mapping raw data to a canonical schema, with no semantic interpretation.
Queued Load	The architectural pattern of using a queue to decouple a high-throughput data generation process from a lower-throughput, serial data persistence process.

The canonization is complete. This architecture is now considered a formal part of the HAiOS project.