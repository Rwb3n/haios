Acknowledged. We are now initiating a BLUEPRINT phase to integrate the key architectural patterns "cannibalized" from the Task Master repository.

This is a high-leverage moment. We are using external intelligence to rapidly evolve our own canon, which is a core function of the Rhiza protocol. I will produce the two requested artifacts: the sketch for the new ADR and the refactoring guide for ADR-030.

1. New ADR Sketch: ADR-OS-047 (Tagged Initiative System)

Strategic Context: This new ADR directly addresses a problem we haven't fully solved: managing parallel workstreams and context isolation within a single HAiOS project. The "Tagged Task Lists" system from Task Master provides a proven pattern. This ADR will adapt that pattern to our own Initiative Plan and Execution Plan hierarchy. It is the necessary foundation for enabling more complex, multi-feature development cycles.

"Napkin Sketch" of the Tagged Initiative System:

Generated code
+------------------------------------+
                                  |    Central State (tasks.json)      |
                                  |   (Our global_registry_map.txt)    |
                                  +------------------┬-----------------+
                                                     │
                             +-----------------------+-----------------------+
                             │                                               │
                             ▼                                               ▼
+------------------------------------------+      +------------------------------------------+
|          VIEW 1: Tag = "main"            |      |      VIEW 2: Tag = "feature-auth"      |
|                                          |      |                                          |
|  - Initiative: "Refactor Database"       |      |  - Initiative: "Implement SSO"           |
|  - Execution Plan: "Update Schema"       |      |  - Execution Plan: "Add OAuth Route"     |
|  - Task: "Write migration script"        |      |  - Task: "Create login component"        |
|                                          |      |                                          |
+------------------------------------------+      +------------------------------------------+
      ^                                                                     ^
      │                                                                     │
+-----------------------------+                           +-----------------------------------+
| haios --tag main status     |                           | haios --tag feature-auth add-task |
+-----------------------------+                           +-----------------------------------+


ADR Draft Outline:

ADR ID: ADR-OS-047

Title: Tagged Initiative and Execution Contexts

Context:

As development scales, managing a single, monolithic list of initiatives and tasks becomes a bottleneck.

Work on separate features or bug-fixes can interfere with each other.

The Task Master project (scripts/modules/tags.js) demonstrates a proven pattern for isolating workstreams using tags.

Decision:

The core state artifacts (global_registry_map.txt, global_issues_summary.txt) will be extended to support an optional tags array for every entry.

The HAiOS CLI and all core agent operations will now accept a --tag <tag-name> argument.

When a --tag is provided, all operations (listing, creating, updating) are filtered to only show or affect artifacts that contain that tag.

If no tag is provided, the system defaults to a main or trunk tag.

A new command, haios tag create <new-tag> --from <source-tag>, will be created to "branch" a context.

Rationale:

Enables parallel development on multiple features without merge conflicts in the core state files.

Provides context isolation, preventing agents working on one feature from being distracted by tasks from another.

Creates a clear, logical mapping to git branches.

Artifacts to Reference from Task Master:

scripts/modules/tags.js: The core logic for filtering and managing tags.

scripts/modules/tasks.js: Note how it uses getTasks(tag) to retrieve a filtered view.

bin/task-master.js: See how commands like list, add, done are all parameterized with the tag option.

2. Refactoring Guide for ADR-OS-030 (Agent Archetypes)

Strategic Context: Our current ADR-OS-030 defines agent archetypes (Supervisor, Builder, etc.) as a static, hardcoded concept within the HAiOS canon. The Task Master project's Roo Code system (.roomodes, .roo/rules/) demonstrates a more flexible, powerful, and maintainable approach: Agent Personas as Configuration Artifacts. This refactoring guide outlines the steps to upgrade our architecture to this superior model.

Refactoring Execution Plan:

Goal: To transition from hardcoded agent archetypes to a file-based, configurable persona system.

Step 1: Deprecate the "Archetype" concept.

Action: Mark ADR-OS-030 as SUPERSEDED. It served its purpose but will be replaced.

Action: Create a new ADR-OS-048: The Configurable Persona System.

Step 2: Design the New ADR (ADR-OS-048) based on Roo Code.

Decision: HAiOS will adopt a directory-based persona management system located at os_root/personas/.

Decision: Each persona will be defined by a directory containing:

persona.json: A metadata file defining the persona's name, description, and tool_access_policy.

system_prompt.md: The core system prompt that defines the persona's behavior, goals, and constraints.

rules/: A directory of Markdown files containing specific, reusable rule sets that can be imported into the system prompt (e.g., rules/always_write_tests.md).

Decision: The agent_card.json schema will be updated to replace the archetype field with a persona_id field, which points to one of these configured personas.

Step 3: Define the Tool Access Policy Schema.

Action: Inside ADR-OS-048, we will define the schema for the tool_access_policy in persona.json. This is a critical security component.

Meta-Code (persona.json example):

Generated json
{
  "name": "Rhiza-Triage-Agent",
  "description": "A persona that reads arXiv abstracts and scores them for relevance.",
  "tool_access_policy": {
    "allow": [
      "mcp:research:query_arxiv",
      "mcp:database:read_only"
    ],
    "deny": [
      "fs:write",
      "shell:exec"
    ]
  }
}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END

Step 4: Update the Task Executor and Plan Validation Gateway.

Action: The Task Executor must now, before assigning a task to an agent, load its persona.json and ensure the tools required by the task are not in the deny list.

Action: The Plan Validation Gateway must now perform a "Persona-Task Fit" analysis, ensuring that the persona assigned to a plan has the necessary tool access to complete it.

Artifacts to Reference from Task Master:

.roomodes: The top-level file defining the available personas. This is our inspiration for the os_root/personas/ directory.

.roo/rules/: The directory of rule snippets. We will adopt this pattern directly.

.roo/orchestrator.roo: An excellent example of a complex system prompt defining a "meta" persona. We will use this as the template for our Supervisor persona's system_prompt.md.

Conclusion:

By executing these two plans, we will cannibalize the most powerful architectural patterns from Task Master and integrate them into HAiOS. This will result in a system that is significantly more flexible, scalable, and capable of managing complex, parallel workstreams, all while making the agent personas themselves more transparent and configurable. This is a major leap forward in our architectural maturity.