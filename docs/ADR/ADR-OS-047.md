ADR-OS-047: Tagged Initiative and Execution Contexts
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Context: Based on the analysis of the "Tagged Task Lists" pattern from the Task Master repository, this ADR provides a formal mechanism for managing parallel workstreams.
1. Context
The HAiOS, in its current v1.0 form, operates on a single, global timeline of initiatives and tasks. As we scale our operations to handle multiple, concurrent Initiative Plans (e.g., developing Project Odin while simultaneously refactoring the 2A System), this single timeline will become a major bottleneck. It risks:
Context Contamination: Agents working on one initiative may be distracted by or incorrectly use artifacts from another.
State Management Conflicts: Concurrent modifications to the central state files (global_registry_map.txt, etc.) by different initiatives could lead to race conditions and data corruption.
Lack of Correlation with Development Branches: There is no clear, 1:1 mapping between a HAiOS Initiative and a git branch, making it difficult to align architectural work with code changes.
The Task Master project demonstrated a proven pattern for solving this: using tags to create isolated, parallel "views" of the central state. This ADR formalizes the adoption of this pattern for the entire HAiOS.
2. Models & Frameworks Applied
Specification-Driven Development (SDD Framework): This protocol is a Tower Layer architectural decision. It defines the foundational pattern for how the Foundation Layer (our state management tools) and Implementation Layer (our Builder agents) will handle parallel work.
Separation of Concerns: This pattern creates a strong separation of concerns between different workstreams, preventing them from interfering with each other.
PocketFlow (Flow and Node): Our orchestration logic must be updated to be "tag-aware." The SharedState passed to each Flow will now include the active tag.
3. Decision
We will adopt a formal Tagged Context System for all HAiOS operations. This system will be managed via a new, universal --tag command-line argument and integrated into our core state management artifacts and agent protocols.
The "Napkin Sketch" of the Tagged Context System:
Generated code
+------------------------------------+
                                  |    CENTRAL STATE ARTIFACTS         |
                                  |  (e.g., global_registry_map.txt)   |
                                  |                                    |
                                  | - Entry 1 { tags: ["main"] }       |
                                  | - Entry 2 { tags: ["main"] }       |
                                  | - Entry 3 { tags: ["odin-mvp"] }   |
                                  | - Entry 4 { tags: ["main", "rhiza"] } |
                                  +------------------┬-----------------+
                                                     │
                             +-----------------------+-----------------------+
                             │                                               │
                             ▼                                               ▼
+------------------------------------------+      +------------------------------------------+
|  VIRTUAL VIEW 1: `haios --tag main status` |      | VIRTUAL VIEW 2: `haios --tag odin-mvp status` |
|                                          |      |                                          |
|  - Shows only Entry 1, 2, 4              |      |  - Shows only Entry 3                    |
|                                          |      |                                          |
+------------------------------------------+      +------------------------------------------+
Use code with caution.
Implementation Details
Schema Update: All major state artifacts (global_registry_map.txt, global_issues_summary.txt, etc.) and all plan artifacts (Initiative Plan, Execution Plan) must be updated to include an optional tags: List[str] field in their schema.
CLI Interface: The main HAiOS CLI (main.py or equivalent) must implement a global --tag <tag-name> option.
If the --tag option is not provided, the system will default to the tag main.
The active tag must be propagated to all downstream operations and agents for that session.
Core Logic Modification: All functions that read from or write to the central state must be refactored to be tag-aware.
Read operations (e.g., "list all initiatives") must filter the results to only include entries that contain the active tag.
Write operations (e.g., "create new execution plan") must automatically add the active tag to the new artifact's tags array.
New Tag Management Commands: The CLI will include new commands for managing tags:
haios tag list: Lists all unique tags currently in the system.
haios tag create <new-tag> --from <source-tag>: Creates a new "branch" of work. This command will find all artifacts with the <source-tag> and create new, duplicate entries for them, but with the <new-tag> instead. This is a powerful "forking" operation for the entire project state.
4. Consequences
Positive:
Enables True Parallel Development: We can now work on the Rhiza initiative and Project Odin simultaneously in isolated contexts without them interfering.
Aligns Architecture with Code: We can create tags that have the same name as our git branches (e.g., feature/odin-mvp), creating a perfect 1:1 mapping between the architectural state and the code state.
Improves Agent Focus: When an agent is invoked with a specific tag, its view of the world is constrained to only the artifacts relevant to its current task, reducing the risk of "Context Contamination."
Negative:
Increases the complexity of our state management logic. All of our core file I/O functions need to be refactored.
Introduces the risk of "tag sprawl" if not managed properly. We will need a Project Guideline for tag naming conventions and archival.