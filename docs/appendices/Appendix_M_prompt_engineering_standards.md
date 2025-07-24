Appendix M: Prompt Engineering Standards
1. Purpose
This appendix provides the canonical standards for all prompt and instruction engineering within the HAiOS. It is a Bridge Layer specification that codifies the production-proven best practices for commanding LLM-based agents like Claude Code.
All agents, particularly the Planner and Orchestrator personas, must adhere to these standards when generating instructions for Builder agents. This is not a set of recommendations; it is a mandatory protocol to ensure reliability, efficiency, and governance.
2. The HAiOS Agent Instruction Protocol (HAIP)
This protocol, formalized in ADR-OS-055, is the foundational principle of all our agent interactions.
Principle 1: NO CONTENT EMBEDDING IN PROMPTS
Rationale: To maintain a strict separation between instruction (the prompt) and data (the context). This ensures all context is a durable, traceable artifact and prevents prompt contamination.
VIOLATION: claude -p "Refactor this code: class Foo..."
COMPLIANT: claude -p "Read file foo.py and refactor its contents according to the rules in guidelines.md"
Principle 2: ORCHESTRATOR CONTROLS METADATA
Rationale: To prevent agent hallucination from corrupting our structured data artifacts. The trusted, deterministic orchestrator script creates the data "skeleton."
VIOLATION: claude -p "Create a new JSON entry for your response with a role and timestamp."
COMPLIANT: claude -p "Read dialogue.json and use the Edit tool to fill the 'content' field of the last entry."
3. The DCIO/XML Prompt Structure
All complex prompts directed at Builder agents must follow the Data -> Context -> Instructions -> Output (DCIO) format and must be structured with XML tags for clarity and improved instruction following.
3.1. Standard XML Tags
<objective>: A single sentence describing the ultimate goal of the task.
<context_artifacts>: A list of file paths the agent should Read to understand the context. This enforces the HAIP.
<instructions>: A numbered list of the specific, sequential actions the agent must take.
<output_specification>: A precise description of the desired output, including file paths, data formats, and schemas.
<example>: A few-shot example of the desired output artifact.
3.2. Template
<prompt>
  <objective>
    Your goal is to [single, clear objective].
  </objective>

  <context_artifacts>
    - Read file: [path/to/relevant/adr.md]
    - Read file: [path/to/source/code.py]
    - Read file: [path/to/test/specification.yml]
  </context_artifacts>

  <instructions>
    1. [First action, e.g., "Analyze the provided context artifacts."]
    2. [Second action, e.g., "Generate the Python code for the new PocketFlow node."]
    3. [Third action, e.g., "Write the generated code to the file at path/to/new_node.py."]
  </instructions>

  <output_specification>
    - You must create one new file.
    - The file must be located at `path/to/new_node.py`.
    - The content of the file must be valid Python code that passes a standard linter.
  </output_specification>

  <example>
    <![CDATA[
    # An example of a well-formed output file
    from pocketflow import AsyncNode

    class MyNewNode(AsyncNode):
        ...
    ]]>
  </example>
</prompt>
4. The Modular & Hierarchical Instruction Architecture
As mandated by our analysis of production-grade agentic systems, we must avoid monolithic prompt files. Our os_root/personas/ directory structure is the implementation of this standard.
CLAUDE.md (or equivalent): The root instruction file for a persona. It should be < 500 tokens and contain only the highest-level, immutable principles of that persona.
commands/: A directory of reusable, task-specific instruction sets (e.g., refactor_pocketflow_node.md). These are the "verbs" of our agent.
configs/: A directory of environment-specific modifications (e.g., strict_mode.md which might add instructions for more verbose logging).
The Orchestrator is responsible for dynamically assembling the final prompt by combining the core CLAUDE.md with the relevant command and config files for a given task. This is a form of "just-in-time" context loading at the instruction level.
5. Token Budget Governance
Context is a finite and expensive resource. All orchestration logic must actively manage the token budget.
Standard Budget Allocation (Guideline):
70% Essential Information: The core data and instructions.
20% Examples & Formatting: Few-shot examples and structural elements (like XML tags).
10% Buffer: A safety margin.
Mandatory Context Clearing: The orchestrator must issue a context-clearing command (e.g., /clear for Claude Code) between logically distinct tasks to prevent context contamination and token waste.
