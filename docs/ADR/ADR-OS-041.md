# ADR-OS-041: Rhiza Agent - Research Ingestion and Analysis Protocol

**Status**: Proposed  
**Date**: 2025-07-11  
**Deciders**: Founding Operator, Genesis Architect  
**Reviewed By**: [To be determined]

## Context

The HAiOS system's effectiveness is directly proportional to its awareness of state-of-the-art developments in AI research, systems architecture, and distributed computing. The rapid pace of innovation in these fields creates a fundamental challenge: how to systematically track, analyze, and integrate cutting-edge research insights into our architectural evolution.

The Rhiza agent represents our solution to this challenge - an automated research ingestion and analysis system designed to:
1. Continuously monitor research sources (initially arXiv)
2. Extract architecturally-relevant insights
3. Transform raw research into actionable architectural patterns
4. Feed insights back into HAiOS's "Roadmap Alignment" strategy

This ADR formalizes the Rhiza protocol and establishes critical architectural decisions for its implementation, particularly around data persistence and integrity guarantees.

## Assumptions

1. **Research Velocity**: The volume of relevant AI research exceeds human capacity to manually track and analyze
2. **Structural Value**: Structured ingestion of research papers enables superior strategic decision-making compared to ad-hoc discovery
3. **Query Performance**: Native JSON field types in databases provide significantly better queryability and indexing capabilities than text blob storage
4. **Evidence Immutability**: The integrity of original research artifacts is critical for maintaining audit trails and trust chains
5. **Incremental Enhancement**: Research insights compound over time, making systematic tracking increasingly valuable
6. **Provider Agnosticism**: Research sources will expand beyond arXiv to include other repositories and proprietary sources

## Models and Frameworks Applied

### Evidence-Based Development
- **Application**: Every research artifact includes SHA-256 integrity hashing
- **Proof**: Raw_Research_Artifact schema includes mandatory `payload_hash` field
- **Rationale**: Ensures tamper-proof evidence chains from source to architectural decision

### Certainty Ratchet
- **Application**: Three-stage pipeline progressively refines uncertainty into actionable insights
- **Proof**: Stage transitions require schema validation (Raw → Analyzed → Integrated)
- **Rationale**: Prevents regression from verified insights back to speculation

### KISS Principle
- **Application**: Each pipeline stage has a single, well-defined purpose
- **Proof**: Stage 1 focuses exclusively on ingestion, Stage 2 on analysis, Stage 3 on integration
- **Rationale**: Simplicity enables reliability and maintainability

### Distributed Systems Principles
- **Application**: All operations designed for idempotency and eventual consistency
- **Proof**: Duplicate detection via `arxiv_id` uniqueness constraints
- **Rationale**: Enables reliable operation in unreliable network conditions

## Decision

### Primary Decision
**Adopt the Rhiza protocol as HAiOS's systematic research ingestion and analysis framework.**

### Architectural Decisions

1. **Persistence Layer Architecture**
   - The persistence layer for structured JSON artifacts (e.g., Raw_Research_Artifact) will utilize native JSON field types in the underlying SQLite/NocoDB database
   - Confidence: High (0.9)
   - Self-critique: Assumes database JSON performance meets scalability needs

2. **Integrity Preservation Mechanism**
   - To ensure the integrity of the original artifact, the application layer (the n8n Load Node) must compute a SHA-256 hash of the serialized JSON string before insertion and store this hash in a separate `payload_hash` column
   - Confidence: Very High (0.95)
   - Self-critique: SHA-256 may eventually need upgrading as cryptographic standards evolve

3. **Pipeline Architecture**
   - Implement a three-stage pipeline architecture:
     - **Stage 1**: Ingestion (arXiv polling → Raw_Research_Artifact)
     - **Stage 2**: Analysis (LLM-powered concept extraction)
     - **Stage 3**: Integration (Architectural pattern synthesis)
   - Confidence: High (0.85)
   - Self-critique: Three stages may prove insufficient for complex analysis chains

4. **Schema-First Design**
   - All artifacts must conform to pre-defined JSON schemas with strict validation
   - Raw_Research_Artifact schema serves as the foundational contract
   - Confidence: Very High (0.95)
   - Self-critique: Schema evolution will require careful migration strategies

### Confidence Indicators
- Overall Architectural Confidence: **High (0.88)**
- Technical Implementation Confidence: **High (0.90)**
- Integration Confidence: **Medium (0.75)** - depends on broader HAiOS evolution

## Rationale

### Why Native JSON Fields Over Text Blobs
1. **Direct Queryability**: Enables SQL queries on nested fields (e.g., `SELECT * WHERE json_extract(data, '$.concepts[0].name') = 'transformer'`)
2. **Indexing Support**: Modern databases can index JSON paths for performance
3. **Type Safety**: JSON schemas provide validation at the database layer
4. **Analytics Ready**: Direct integration with BI tools and dashboards

*Self-critique: This assumes our database choice (SQLite/NocoDB) maintains good JSON performance at scale. May need to revisit for TB-scale datasets.*

### Why SHA-256 Integrity Hashing
1. **Tamper Detection**: Any modification to the artifact is immediately detectable
2. **Audit Compliance**: Provides cryptographic proof of data integrity
3. **Legal Protection**: Establishes chain of custody for research artifacts
4. **Distributed Trust**: Enables verification without trusting intermediate systems

*Self-critique: SHA-256 is currently secure but not quantum-resistant. Migration path needed for post-quantum cryptography.*

### Why Stage-Based Pipeline Architecture
1. **Separation of Concerns**: Each stage has clear boundaries and responsibilities
2. **Failure Isolation**: Failures in one stage don't cascade to others
3. **Incremental Progress**: Partial completion provides value
4. **Horizontal Scaling**: Each stage can scale independently

*Self-critique: Stage boundaries may create artificial constraints on complex analysis workflows. May need dynamic stage composition in future.*

## Alternatives Considered

### Alternative 1: Text Blob Storage
- **Description**: Store entire artifacts as serialized text in VARCHAR fields
- **Pros**: Simple implementation, no JSON parsing overhead
- **Cons**: Poor queryability, no indexing, requires application-layer parsing
- **Rejection Reason**: Violates our need for efficient research analytics

### Alternative 2: Manual Research Tracking
- **Description**: Human operators manually review and catalog research
- **Pros**: High-quality curation, nuanced understanding
- **Cons**: Doesn't scale, expensive, inconsistent
- **Rejection Reason**: Volume of research exceeds human capacity

### Alternative 3: Third-Party Research APIs Only
- **Description**: Rely entirely on external research aggregation services
- **Pros**: No infrastructure overhead, immediate access
- **Cons**: Vendor lock-in, no control over processing, limited customization
- **Rejection Reason**: Conflicts with our sovereignty and evidence-based principles

### Alternative 4: Full-Text Search Engine
- **Description**: Use Elasticsearch or similar for research storage
- **Pros**: Powerful search capabilities, built for text analysis
- **Cons**: Additional infrastructure complexity, overkill for structured data
- **Rejection Reason**: JSON fields in SQLite/NocoDB provide sufficient capability with less complexity

## Consequences

### Positive Consequences
1. **Systematic Knowledge Accumulation**: Builds a queryable knowledge base of research insights
2. **Audit Trail Integrity**: Cryptographic proofs ensure research provenance
3. **Automated Insight Generation**: Reduces human cognitive load for research tracking
4. **Strategic Advantage**: Faster awareness of breakthrough techniques
5. **Integration Ready**: Clean APIs for feeding insights into HAiOS decision-making
6. **Scalable Architecture**: Can handle exponential growth in research volume

### Negative Consequences
1. **Storage Overhead**: JSON storage requires more space than compressed formats
2. **Pipeline Complexity**: Three-stage architecture requires careful orchestration
3. **Maintenance Burden**: Schema evolution requires migration strategies
4. **Initial Development Cost**: Significant upfront investment in pipeline infrastructure
5. **LLM Dependency**: Analysis quality limited by LLM capabilities

### Risk Mitigation Strategies
1. **Storage**: Implement periodic archival of old artifacts to cold storage
2. **Complexity**: Comprehensive monitoring and alerting for each pipeline stage
3. **Maintenance**: Version all schemas with backward compatibility requirements
4. **Development**: Leverage existing n8n/NocoDB infrastructure to reduce custom code
5. **LLM Quality**: Implement human-in-the-loop validation for critical insights

## Clarifying Questions

### Q1: How will Rhiza handle research sources beyond arXiv?
*Context: arXiv is just one source of research. What about ACM, IEEE, proprietary sources?*

### Q2: What specific analyses will Stage 2 perform beyond concept extraction?
*Context: Concept extraction is mentioned, but what other analytical transformations are planned?*

### Q3: How will Rhiza insights integrate with the Vertical MCP architecture from ADR-OS-042?
*Context: Both systems deal with knowledge synthesis - how do they interact?*

### Q4: What are the performance targets for the ingestion pipeline?
*Context: How many papers per day? What latency requirements?*

### Q5: How will Rhiza handle versioning of research papers?
*Context: arXiv papers often have multiple versions - how do we track evolution?*

### Q6: What governance controls will prevent research bias or manipulation?
*Context: How do we ensure diverse perspectives and prevent echo chambers?*

## References

- ADR-OS-040: Market Positioning and Segmentation Strategy
- ADR-OS-042: Vertical MCP Architecture [Forthcoming]
- Raw_Research_Artifact Schema: `/docs/schema/raw_research_artifact_schema.md`
- Rhiza Agent Implementation: `/agents/rhiza_agent/`
- Evidence-Based Development (ADR-OS-001)
- Distributed Systems Principles (ADR-OS-023 through ADR-OS-029)