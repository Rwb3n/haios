# Architecture Decision Records (ADR) Index

This directory contains all Architecture Decision Records for the Hybrid AI Operating System (HAiOS). ADRs document important architectural decisions, their context, rationale, and consequences.

## Quick Navigation

### 📋 **Core System Architecture**
- [**ADR-OS-001**](ADR-OS-001.md) - **Embedded Annotation Blocks** - Metadata and versioning system for all project artifacts
- [**ADR-OS-002**](ADR-OS-002.md) - **Hierarchical Planning Model** - Multi-tiered planning from Request → Analysis → Initiative → Execution
- [**ADR-OS-003**](ADR-OS-003.md) - **OS Control File Schemas** - Structured data formats for state management and planning
- [**ADR-OS-004**](ADR-OS-004.md) - **Global Event Tracking & Versioning** - `g` counter and `v` versioning for event sequencing and optimistic locking
- [**ADR-OS-005**](ADR-OS-005.md) - **Directory Structure & File Naming** - Configuration-driven project layout and naming conventions

### 🔄 **Operational Framework**
- [**ADR-OS-006**](ADR-OS-006.md) - **Phase-Based Operational Model** - ANALYZE → BLUEPRINT → CONSTRUCT → VALIDATE → IDLE cycle
- [**ADR-OS-010**](ADR-OS-010.md) - **Atomic File Operations** - Safe, concurrent file operations with locking and conflict resolution
- [**ADR-OS-011**](ADR-OS-011.md) - **Task Failure Handling & Remediation** - Structured approach to handling and recovering from failures
- [**ADR-OS-016**](ADR-OS-016.md) - **Dependency Management & Topological Sorting** - Task ordering and dependency cycle detection

### 🧪 **Quality Assurance**
- [**ADR-OS-007**](ADR-OS-007.md) - **Integrated Testing Lifecycle** - Evidence-based testing with separation of duties
- [**ADR-OS-008**](ADR-OS-008.md) - **OS-Generated Reporting Strategy** - Analysis, Validation, and Progress reports
- [**ADR-OS-014**](ADR-OS-014.md) - **Project Guidelines Artifact** - Durable project standards and bias prevention checklists

### 🤖 **Agent Management**
- [**ADR-OS-012**](ADR-OS-012.md) - **Dynamic Agent Management** - Runtime agent registration and configuration
- [**ADR-OS-015**](ADR-OS-015.md) - **Precision Context Loading** - Efficient, targeted context loading for LLM agents
- [**ADR-OS-018**](ADR-OS-018.md) - **MCP Tool Integration** - Model Context Protocol for external tool access

### 📊 **Monitoring & Operations**
- [**ADR-OS-009**](ADR-OS-009.md) - **Issue Management & Summarization** - Structured issue tracking with tiered summaries
- [**ADR-OS-013**](ADR-OS-013.md) - **Artifact Registry & Linking** - Global artifact registry for dependency tracking
- [**ADR-OS-019**](ADR-OS-019.md) - **Observability & Budget Governance** - Prometheus metrics, cost tracking, and budget enforcement
- [**ADR-OS-020**](ADR-OS-020.md) - **Runtime Modes & Developer Experience** - STRICT vs DEV_FAST modes for different use cases

### 🚀 **Implementation Phases**
- [**ADR-OS-017**](ADR-OS-017.md) - **Phase 1 - MVP Engine & Tooling** - Minimum viable product scope and deliverables

---

## ADR Status Legend

| Status | Description |
|--------|-------------|
| **Proposed** | Under consideration, not yet implemented |
| **Accepted** | Approved and being implemented |
| **Superseded** | Replaced by a newer ADR |
| **Deprecated** | No longer recommended |

## ADR Categories

### 🏗️ **Foundation (001-005)**
Core architectural decisions that establish the fundamental structure and data model of HAiOS.

### ⚙️ **Operations (006-011, 016)**
Decisions about how the system operates, including phases, file operations, and error handling.

### 🔍 **Quality & Testing (007-008, 014)**
Decisions about ensuring system quality, testing strategies, and reporting mechanisms.

### 🤖 **Agent Integration (012, 015, 018)**
Decisions about how AI agents are managed, configured, and interact with external tools.

### 📈 **Monitoring & Management (009, 013, 019-020)**
Decisions about system observability, artifact management, and operational modes.

### 🎯 **Implementation (017)**
Decisions about implementation phases and delivery strategy.

---

## Quick Reference

### Most Critical ADRs for New Contributors
1. **ADR-OS-001** - Understanding the annotation system
2. **ADR-OS-002** - Understanding the planning hierarchy  
3. **ADR-OS-006** - Understanding the operational phases
4. **ADR-OS-005** - Understanding the directory structure

### Most Critical ADRs for Operators
1. **ADR-OS-019** - Observability and budgets
2. **ADR-OS-020** - Runtime modes
3. **ADR-OS-011** - Failure handling
4. **ADR-OS-009** - Issue management

### Most Critical ADRs for Agent Developers
1. **ADR-OS-012** - Agent management
2. **ADR-OS-015** - Context loading
3. **ADR-OS-018** - MCP tool integration
4. **ADR-OS-007** - Testing lifecycle

---

## Contributing to ADRs

When proposing a new ADR:
1. Use the next available ADR-OS-XXX number
2. Follow the established template format
3. Include proper status, date, and context
4. Update this index with the new ADR
5. Ensure the ADR includes an `EmbeddedAnnotationBlock`

For questions about existing ADRs or to propose changes, please create an issue in the project repository. 