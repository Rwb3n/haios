# Third-Party Research Agent Evaluation for Rhiza

## Summary

The recommendations.txt suggests adopting third-party research agent patterns (researchleadagent.txt, researchsubagent.txt, basicworkflow.txt) for the Rhiza implementation. After thorough analysis, these patterns require **significant architectural transformation** to align with HAIOS principles.

## Key Findings

### 1. Fundamental Conflicts

**Trust Model**
- ❌ Third-party: Relies on LLM judgment for critical decisions
- ✅ HAIOS: Requires deterministic trust and evidence artifacts

**Agent Autonomy**
- ❌ Third-party: Autonomous agents with self-directed research
- ✅ HAIOS: Strictly bounded agents with role-based permissions

**Evidence Generation**
- ❌ Third-party: Produces narrative reports
- ✅ HAIOS: Requires structured artifacts with EmbeddedAnnotationBlocks

### 2. Security Vulnerabilities

1. **No input validation** - Prompt injection risks
2. **No sandboxing** - Unrestricted tool access
3. **No audit trails** - Cannot trace decision lineage
4. **Self-validation** - Violates separation of duties

### 3. Architectural Gaps

- Missing idempotency guarantees
- No distributed systems support (async, partitioning)
- Lacks structured error handling
- No schema validation for outputs

## Adaptation Strategy

### Phase 1: Transform Core Patterns

```python
# Instead of autonomous LLM routing:
class DeterministicResearchRouter:
    def route_request(self, request: ResearchRequest) -> ResearchPlan:
        # Rule-based routing, not LLM-based
        if request.scope == "single_paper":
            return ChainWorkflowPlan()
        elif request.scope == "topic_survey":
            return ParallelWorkflowPlan()
        else:
            return TriageWorkflowPlan()
```

### Phase 2: Implement Trust Boundaries

1. **Builder Persona**: Execute research tasks
2. **Validator Persona**: Verify outputs (separate agent)
3. **Evidence Store**: Cryptographically signed artifacts
4. **Audit Logger**: Complete trace with trace_id

### Phase 3: Secure Integration Points

**Safe to Adopt (with modifications):**
- Workflow patterns (chain, parallel, route) as state machines
- Task decomposition structure (but deterministic, not LLM-based)
- OODA loop concept (but with evidence generation)

**Must Replace:**
- LLM-based routing → Rule-based system
- Narrative outputs → Structured schemas
- Autonomous execution → Bounded, monitored tasks
- Self-validation → Separate validator persona

## Implementation Recommendations

### Immediate Actions
1. Create JSON schemas for all Rhiza inputs/outputs
2. Design rule-based routing system for research requests
3. Implement evidence artifact generator
4. Build separate validator agent

### Architecture Requirements
```yaml
rhiza_agent:
  core_components:
    - deterministic_router
    - evidence_generator
    - schema_validator
    - security_sandbox
  
  workflow_patterns:
    - chain: State machine with checkpoints
    - parallel: Message queue with idempotent workers
    - route: Rule-based decision tree
  
  trust_mechanisms:
    - separate_builder_validator
    - cryptographic_evidence_chain
    - comprehensive_audit_trail
    - input_sanitization
```

### Risk Mitigation

**Critical Safeguards:**
1. **Execution Budget**: Hard limits on time/resources
2. **Input Validation**: Schema enforcement at entry
3. **Output Verification**: Independent validation step
4. **Monitoring**: Real-time anomaly detection

## Conclusion

While the third-party patterns offer sophisticated orchestration ideas, they cannot be directly integrated into HAIOS. The Rhiza implementation must:

1. **Replace** LLM judgment with deterministic logic
2. **Add** comprehensive trust and security layers
3. **Transform** outputs into verifiable evidence artifacts
4. **Enforce** strict separation of duties

The workflow patterns (chain, parallel, route) can inspire our design, but implementation must be rebuilt from first principles to maintain HAIOS's trust guarantees.

## Next Steps

1. Review and approve this evaluation
2. Update RHIZA_BLUEPRINT.md with security requirements
3. Create deterministic routing rules
4. Design evidence artifact schemas
5. Implement builder/validator separation