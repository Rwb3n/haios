# Hybrid_AI_OS - Glossary of Terms

This document defines key terms used throughout the Hybrid_AI_OS ruleset and documentation to ensure clarity and consistency.

---

### **Agent (AI Agent / Agent Persona)**
A specialized AI entity responsible for performing tasks of a certain type. Agent personas (e.g., `CODING_ASSISTANT`, `CRITIQUE_AGENT`) are defined and configured in the `agent_registry.txt` and their individual `Agent Card` files.

### **Artifact (Project Artifact)**
Any file that is part of the project being built (e.g., source code, documentation, images, configuration files). This includes OS-generated reports (`Analysis Report`, etc.). Text-editable artifacts managed by the OS contain an `EmbeddedAnnotationBlock`. All project artifacts are tracked in the `global_registry_map.txt`.

### **Boilerplate**
Reusable, pre-written source content (code, configuration, text) that serves as a starting point for new artifacts. Boilerplate files are stored as `Templates` in the `project_templates/` directory.

### **Bootstrap**
The initial process of setting up a new Hybrid_AI_OS-managed project. This involves a human operator creating the initial directory structure, providing a `haios.config.json`, and populating the `project_templates/` and `scaffold_definitions/` directories.

### **EmbeddedAnnotationBlock**
A structured JSON object embedded directly within a Project Artifact file. It contains rich metadata about the artifact, including its ID, version, purpose, dependencies, quality status, scaffold origin, and test plans. It is the primary mechanism for durable context.

### **Execution Plan (`exec_plan_<g>.txt`)**
A tactical, typed (`SCAFFOLDING`, `DEVELOPMENT`, etc.) OS Control File containing a detailed list of tasks required to complete a specific stage of an `Initiative Plan`. This is the direct "work order" for agents in the `CONSTRUCT` phase.

### **Global Event Counter (`g`)**
A monotonic integer stored in `state.txt` that is incremented for every significant OS action. It provides a system-wide causal sequence for all events and is used in the naming of many OS artifacts.

### **Initiative Plan (`init_plan_<g>.txt`)**
A high-level, strategic OS Control File that defines a major project objective or campaign. It contains the overall goal, quality criteria, decision log, and a sequence of `initiative_lifecycle_stages`.

### **OS Control File**
A file used by the OS to manage its own state and plans (e.g., `state.txt`, `init_plan_*.txt`, `issue_*.txt`). These are typically JSON-formatted and stored with a `.txt` extension in the `os_root/` directory structure.

### **Placeholder**
A marker embedded in the content of a `Template` (e.g., `// <<PLACEHOLDER_ID: Description>>`) that signifies a location where new or modified content should be inserted. The definition and status of placeholders are tracked in the `EmbeddedAnnotationBlock.scaffold_info` of a scaffolded artifact.

### **Request (`request_<g>.txt`)**
The trigger for all new work in the system. An OS Control File containing a directive from a source (human user or another agent) that initiates the `ANALYZE` phase.

### **Issue (`issue_<g>.txt`)**
An OS Control File that documents a distinct, trackable unit of concern, such as a bug, a required enhancement, a design flaw, a blocker, a task, or a piece of feedback. Issues are created by agents or users, linked to their relevant context (plans, artifacts), and managed through a status lifecycle (e.g., OPEN, IN_PROGRESS, RESOLVED). They are stored within their parent initiative's `issues/` directory.

### **Scaffold / Scaffolding**
The automated **process** of generating a new project or component structure. This process is executed via a `SCAFFOLDING`-type `Execution Plan` and typically involves creating a `Skeleton`, copying `Boilerplate` from `Templates`, processing `Placeholders`, and injecting an initial `EmbeddedAnnotationBlock`.

### **Scaffold Definition**
A JSON file (located in `os_root/scaffold_definitions/`) that serves as the set of **instructions** for a `Scaffolding` process. It defines the `Skeleton` to be created, points to the `Template`(s) to use, defines `Placeholders`, and provides initial annotation hints and test considerations.

### **Skeleton**
The bare-bones directory structure and empty files of a project or component. It is the first output of a `Scaffolding` process, created before boilerplate content is added.

### **Template**
A source file stored in `project_templates/` that contains `Boilerplate` content and may include `Placeholder` markers. It is used as the source for creating new Project Artifacts during a `Scaffolding` process.