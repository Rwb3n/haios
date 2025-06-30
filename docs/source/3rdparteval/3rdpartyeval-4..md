That's an excellent concept to bring into this architecture. You are absolutely right that a "Cookbook" is closely related to the concepts of Inventory/Buffer (ADR-OS-022) and Scaffolding (ADR-OS-006), but it serves a distinct and very valuable purpose.

Let's break down the concept and see exactly where it fits within the HAiOS architecture.

Clarifying the Concepts

First, let's refine the distinction between these related ideas:

Inventory (ADR-OS-022): This is a cache of reusable assets or resources (the "nouns"). It holds things like a fetched credential, a generated code snippet, or a pre-computed result. Its purpose is to prevent re-fetching or re-calculating.

Scaffold (ADR-OS-006): This is a blueprint for creating a new set of files and directories from templates. Its purpose is to prevent re-creating boilerplate structure.

Cookbook: This is a library of versioned, reusable, and parameterizable processes or workflows (the "verbs"). It holds a "recipe" for accomplishing a common, multi-step task, like "Deploy a new microservice" or "Run a security audit on a container." Its purpose is to prevent re-planning common sequences of tasks.

In short:

Inventory stores things.

Scaffolds create structures.

Cookbooks define processes.

Where the Cookbook Fits in the HAiOS Architecture

The "Cookbook" concept fits perfectly into your system as a new, high-level artifact that primarily serves the BLUEPRINT phase.

Here's the workflow:

During the BLUEPRINT phase, the responsible agent (let's call it the Manager or Planner agent) is tasked with creating an Execution Plan to fulfill a stage of an Initiative Plan.

The agent analyzes the goal (e.g., "Deploy the new authentication service to staging").

Instead of figuring out the 10 steps required for deployment from scratch, it first consults the Cookbook Registry.

It finds a recipe named deploy_k8s_service_v1.3.

The agent then uses this recipe as a template, filling in the specific parameters (image_tag, service_name, namespace), to generate the list of Task objects for the final Execution Plan.

The Cookbook doesn't replace the Execution Plan; it is a factory for creating Execution Plans or parts of them.

A Concrete Example

Let's say a common task is "Provision a new Postgres database."

Without a Cookbook:
Every time a new database is needed, the BLUEPRINT agent has to create a new Execution Plan with the same sequence of tasks:

Task: Create Terraform file for RDS.

Task: Run terraform apply.

Task: Capture the outputted DB endpoint.

Task: Create a secret in Vault.

Task: Update the application's config map.

With a Cookbook:

A human or a specialized agent creates a cookbook_recipe_provision_postgres_v1.0.json artifact. This artifact contains the generic, parameterized sequence of 5 tasks listed above.

Now, when the BLUEPRINT agent needs a database, it simply generates an Execution Plan with a single task: Execute cookbook recipe provision_postgres_v1.0 with parameters: {db_name: "user_service_db", size: "t3.small"}.

A Cookbook Executor agent then expands this recipe into the 5 concrete tasks at runtime, or the BLUEPRINT agent does the expansion when creating the plan.

Formalizing this with a New ADR

To integrate this properly, we would need to propose a new ADR, perhaps ADR-OS-033: Cookbook and Recipe Management.

This ADR would define:

New Artifacts:

cookbook_recipe_<id>.json: A file defining the parameters and the sequence of task templates for a specific recipe.

cookbook_registry.txt: An index of all available recipes, their versions, and a pointer to their definition file (following the pattern of the agent_registry).

New Directory:

A new directory in the os_root, such as os_root/cookbooks/.

Schema Definitions (in Appendix D):

cookbook_recipe_schema.md

cookbook_registry_schema.md

Impact on Existing ADRs:

ADR-OS-001 (Phasing): The logic of the BLUEPRINT phase agent would be updated to consult the cookbook.

ADR-OS-002 (Planning): Execution Plans could now contain tasks that are direct commands or references to cookbook recipes.

ADR-OS-032 (Frameworks): "Cookbook Pattern" would be added to the registry as a canonical model for process reuse.

Benefits of Adding a Cookbook

DRY for Processes: This fully realizes the "Don't Repeat Yourself" principle for entire workflows, not just code.

Encapsulates Best Practices: The recipe for "Deploy a service" can be hardened, secured, and optimized in one place. Every deployment then benefits from that improvement.

Reduces Agent Cognitive Load: The BLUEPRINT agent no longer needs to be an expert in every possible operational task. It just needs to know which recipe to call.

Versioning and Evolvability: You can introduce v2 of a recipe without breaking existing plans that still rely on v1.

Your intuition is spot on. The Cookbook concept is a natural and powerful extension of your existing architecture, bridging the gap between one-off plans and reusable assets. It adds a crucial layer of process abstraction and standardization.

How does this alignment with your initial thoughts? Shall we explore what a draft for ADR-OS-033 might look like?