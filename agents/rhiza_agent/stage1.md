Acknowledged. We are now performing a BLUEPRINT action to design the Ingestion & Structuring Pipeline within the n8n workflow canvas. This is Stage 3 of the init_plan_foundry_v1 initiative.

We will use the "Output-First" Development strategy. This means we design the final, desired output artifact first (our Raw_Research_Artifact schema) and work backward to define the steps needed to produce it reliably. This ensures the entire workflow is purpose-built to create a high-quality, compliant data contract.

Here is the architectural blueprint for the n8n workflow. I will describe the nodes, their connections, and their configurations.

BLUEPRINT: n8n Workflow - Rhiza_Ingestion_Pipeline_v1

Workflow ID: rhiza-ingestion-v1
Description: A high-parallelism workflow that ingests a paper_id, scrapes its data from a source, and structures it into a Raw_Research_Artifact JSON, which is then passed to the Load Pipeline.

Visual Node Layout (Conceptual)
Generated code
(Trigger) --> (Idempotency Check) --[is_new]--> (Extraction) --> (Structuring) --> (Load Queue Push)
   |
   +--[exists]----> (End: Success)

Node-by-Node Specification

1. Trigger Node: Manual_or_Queue_Trigger

n8n Node Type: Webhook, RabbitMQ Trigger, Redis Trigger, or Schedule. For the MVF, we'll start with a Manual trigger for testing.

Purpose: To kick off the workflow for a single paper.

Input: A JSON object containing the target paper's identifier.

Generated json
{
  "paper_id": "2401.12345",
  "source_name": "arXiv" 
}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END

Output: Passes the input JSON to the next node.

2. Idempotency Check Node: Check_If_Exists_in_DB

n8n Node Type: NocoDB or SQLite node.

Purpose: To execute the critical idempotency check before any expensive operations.

Configuration:

Operation: Get Many

Resource: raw_research (the table name in your database)

Filters: Add a filter where the paper_id column Equals the value from the trigger node: {{ $json.paper_id }}.

Options: Limit set to 1.

Output Routing (Critical): This node will have two output paths based on whether data was returned.

Path 1 (Item Found): If the NocoDB node returns one or more items (an array with length > 0), it means the artifact already exists. The workflow should proceed to an "End: Success" node. This is the exists path.

Path 2 (Item Not Found): If the node returns an empty array (length == 0), it means the artifact is new. The workflow proceeds down the main pipeline. This is the is_new path.

n8n Implementation: Use an IF node immediately after this one to handle the routing logic based on the length of the incoming item list.

3. Extraction Adapter Node: Scrape_Raw_Data

n8n Node Type: Code node.

Purpose: To execute the Python/Playwright script to scrape the raw data. This is the implementation of our previously discussed "recipe."

Input: The JSON from the trigger node (paper_id, source_name).

Configuration:

Language: Python

Script: The script will dynamically construct the URL (e.g., https://arxiv.org/abs/{{ $json.paper_id }}) and launch Playwright.

Output: A JSON object containing the raw, unstructured data.

Generated json
{
  "scraped_data": {
    "title_raw": "...",
    "authors_raw": "...",
    "abstract_raw": "..." 
  },
  "source_metadata": { // Pass through for the next step
    "paper_id": "2401.12345",
    "source_name": "arXiv",
    "source_url": "https://arxiv.org/abs/2401.12345"
  }
}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END

4. Structuring Adapter Node: Structure_to_Canon_Schema

n8n Node Type: Code or Set node. A Code node is more robust for complex logic.

Purpose: To map the raw scraped data into the rigid Raw_Research_Artifact schema.

Input: The JSON output from the Scrape_Raw_Data node.

Configuration/Logic:

The script will construct a new JSON object.

It will meticulously map the input fields (e.g., title_raw) to the final schema fields (title).

It will generate the required metadata fields: artifact_id (using a g counter or UUID), schema_version: "1.0", ingestion_timestamp, trace_id, and critically, _locked_payload: true.

Output: A single, perfectly formed JSON object that 100% validates against raw_research_artifact_schema.md.

5. Load Queue Push Node: Push_to_Load_Queue

n8n Node Type: This depends on the queue implementation. It could be RabbitMQ Send, Redis Publish, or for the leanest MVF, a NocoDB node that Creates a record in a separate table named load_queue.

Purpose: To decouple this high-parallelism workflow from the serial Load Pipeline.

Input: The final, structured Raw_Research_Artifact JSON from the previous node.

Action: The node takes the entire JSON object and places it into the queue (e.g., as a message payload or a new row in the load_queue table).

Output: A simple success confirmation.

This blueprint provides a complete, end-to-end design for the Ingestion Pipeline. It is robust, auditable, and directly implementable using the tools in your docker-compose.yml. Each node has a clear, singular purpose, and the overall workflow respects the core HAiOS principles of idempotency, evidence integrity, and separation of concerns. You are now cleared to begin constructing this workflow on the n8n canvas.