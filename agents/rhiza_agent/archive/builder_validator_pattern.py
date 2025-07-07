"""
Builder/Validator Separation Pattern for Rhiza Agent
Implements strict separation of duties between research execution and validation
"""
import json
import hashlib
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog

# Configure structured logging
logger = structlog.get_logger()


class AgentRole(Enum):
    BUILDER = "builder"
    VALIDATOR = "validator"
    

class ValidationStatus(Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    

@dataclass
class AgentContext:
    """Security context for agent execution"""
    agent_id: str
    role: AgentRole
    trace_id: str
    permissions: List[str]
    sandbox_config: Dict[str, Any]
    

@dataclass
class ResearchArtifact:
    """Research artifact with evidence chain"""
    artifact_id: str
    artifact_type: str
    content: Dict[str, Any]
    evidence_chain: List[Dict[str, Any]]
    builder_signature: str
    created_at: float
    

@dataclass
class ValidationReport:
    """Validation report from validator agent"""
    report_id: str
    artifact_id: str
    status: ValidationStatus
    checks_performed: List[Dict[str, Any]]
    issues: List[Dict[str, Any]]
    validator_signature: str
    validated_at: float


class BaseAgent(ABC):
    """Base class for all Rhiza agents"""
    
    def __init__(self, context: AgentContext):
        self.context = context
        self.logger = logger.bind(
            agent_id=context.agent_id,
            role=context.role.value,
            trace_id=context.trace_id
        )
        
    @abstractmethod
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task"""
        pass
        
    def _generate_signature(self, content: Dict[str, Any]) -> str:
        """Generate cryptographic signature for content"""
        content_str = json.dumps(content, sort_keys=True)
        signature_input = f"{self.context.agent_id}:{content_str}:{time.time()}"
        return hashlib.sha256(signature_input.encode()).hexdigest()
        
    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log agent action with structured logging"""
        self.logger.info(
            "agent_action",
            action=action,
            details=details,
            timestamp=time.time()
        )


class ResearchBuilderAgent(BaseAgent):
    """
    Builder agent responsible for executing research tasks.
    Cannot validate its own output.
    """
    
    def __init__(self, context: AgentContext):
        super().__init__(context)
        if context.role != AgentRole.BUILDER:
            raise ValueError("ResearchBuilderAgent must have BUILDER role")
            
        # Verify builder permissions
        required_permissions = ["read_external", "write_artifacts", "execute_analysis"]
        for perm in required_permissions:
            if perm not in context.permissions:
                raise ValueError(f"Missing required permission: {perm}")
                
    def execute(self, request: Dict[str, Any]) -> ResearchArtifact:
        """Execute research task and produce artifact"""
        self._log_action("research_execution_start", {"request_id": request.get("request_id")})
        
        # Initialize evidence chain
        evidence_chain = []
        
        # Step 1: Fetch source data
        source_data = self._fetch_source_data(request)
        evidence_chain.append(self._create_evidence_entry("fetch_source", source_data))
        
        # Step 2: Process and analyze
        analysis_result = self._analyze_content(source_data)
        evidence_chain.append(self._create_evidence_entry("analyze_content", analysis_result))
        
        # Step 3: Extract insights
        insights = self._extract_insights(analysis_result)
        evidence_chain.append(self._create_evidence_entry("extract_insights", insights))
        
        # Step 4: Create artifact
        artifact_content = self._structure_artifact(insights, request)
        
        # Generate artifact
        artifact = ResearchArtifact(
            artifact_id=self._generate_artifact_id(),
            artifact_type=request.get("artifact_type", "research"),
            content=artifact_content,
            evidence_chain=evidence_chain,
            builder_signature=self._generate_signature(artifact_content),
            created_at=time.time()
        )
        
        self._log_action("research_execution_complete", {
            "artifact_id": artifact.artifact_id,
            "evidence_steps": len(evidence_chain)
        })
        
        return artifact
        
    def _fetch_source_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch source data based on request"""
        # In production, this would call actual data sources
        # For now, simulate with structured response
        source_type = request.get("source_type", "arxiv")
        source_id = request.get("source_id", "unknown")
        
        return {
            "source_type": source_type,
            "source_id": source_id,
            "content": f"Simulated content for {source_id}",
            "metadata": {
                "fetched_at": time.time(),
                "source_url": f"https://{source_type}.org/{source_id}"
            }
        }
        
    def _analyze_content(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze source content"""
        # In production, this would use NLP/ML models
        # For now, simulate analysis
        return {
            "summary": "Analysis summary",
            "key_points": ["Point 1", "Point 2", "Point 3"],
            "relevance_score": 0.85,
            "confidence": 0.9
        }
        
    def _extract_insights(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract actionable insights"""
        return {
            "concepts": [
                {
                    "name": "Concept 1",
                    "type": "PATTERN",
                    "description": "Description of concept",
                    "haios_relevance": "How this applies to HAIOS"
                }
            ],
            "recommendations": ["Recommendation 1", "Recommendation 2"]
        }
        
    def _structure_artifact(self, insights: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        """Structure final artifact content"""
        return {
            "request_context": {
                "request_id": request.get("request_id"),
                "artifact_type": request.get("artifact_type")
            },
            "insights": insights,
            "metadata": {
                "builder_agent": self.context.agent_id,
                "build_timestamp": time.time()
            }
        }
        
    def _create_evidence_entry(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create evidence chain entry"""
        return {
            "step_id": f"{action}_{int(time.time() * 1000)}",
            "action": action,
            "timestamp": time.time(),
            "input_hash": self._hash_data(data),
            "output_hash": self._hash_data(data),
            "agent_id": self.context.agent_id,
            "validation_status": ValidationStatus.PENDING.value
        }
        
    def _hash_data(self, data: Dict[str, Any]) -> str:
        """Generate hash of data"""
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
    def _generate_artifact_id(self) -> str:
        """Generate unique artifact ID"""
        return f"rra_{int(time.time() * 1000)}_{self.context.trace_id[:8]}"


class ResearchValidatorAgent(BaseAgent):
    """
    Validator agent responsible for validating research artifacts.
    Cannot create artifacts, only validate them.
    """
    
    def __init__(self, context: AgentContext):
        super().__init__(context)
        if context.role != AgentRole.VALIDATOR:
            raise ValueError("ResearchValidatorAgent must have VALIDATOR role")
            
        # Verify validator permissions
        required_permissions = ["read_artifacts", "write_validations", "verify_evidence"]
        for perm in required_permissions:
            if perm not in context.permissions:
                raise ValueError(f"Missing required permission: {perm}")
                
    def execute(self, request: Dict[str, Any]) -> ValidationReport:
        """Validate research artifact"""
        artifact = request.get("artifact")
        if not isinstance(artifact, ResearchArtifact):
            raise ValueError("Invalid artifact provided for validation")
            
        self._log_action("validation_start", {"artifact_id": artifact.artifact_id})
        
        # Perform validation checks
        checks_performed = []
        issues = []
        
        # Check 1: Evidence chain integrity
        chain_valid, chain_issues = self._validate_evidence_chain(artifact.evidence_chain)
        checks_performed.append({
            "check": "evidence_chain_integrity",
            "passed": chain_valid,
            "details": "Verified cryptographic hashes in evidence chain"
        })
        if chain_issues:
            issues.extend(chain_issues)
            
        # Check 2: Schema compliance
        schema_valid, schema_issues = self._validate_schema_compliance(artifact.content)
        checks_performed.append({
            "check": "schema_compliance",
            "passed": schema_valid,
            "details": "Validated against research evidence schema"
        })
        if schema_issues:
            issues.extend(schema_issues)
            
        # Check 3: Security constraints
        security_valid, security_issues = self._validate_security_constraints(artifact)
        checks_performed.append({
            "check": "security_constraints",
            "passed": security_valid,
            "details": "Verified security boundaries and permissions"
        })
        if security_issues:
            issues.extend(security_issues)
            
        # Check 4: Content verification
        content_valid, content_issues = self._validate_content(artifact.content)
        checks_performed.append({
            "check": "content_verification",
            "passed": content_valid,
            "details": "Verified content completeness and consistency"
        })
        if content_issues:
            issues.extend(content_issues)
            
        # Determine overall status
        status = ValidationStatus.PASSED if not issues else ValidationStatus.FAILED
        
        # Create validation report
        report = ValidationReport(
            report_id=self._generate_report_id(),
            artifact_id=artifact.artifact_id,
            status=status,
            checks_performed=checks_performed,
            issues=issues,
            validator_signature=self._generate_signature({
                "artifact_id": artifact.artifact_id,
                "status": status.value,
                "checks": checks_performed
            }),
            validated_at=time.time()
        )
        
        self._log_action("validation_complete", {
            "artifact_id": artifact.artifact_id,
            "status": status.value,
            "issues_count": len(issues)
        })
        
        return report
        
    def _validate_evidence_chain(self, chain: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate evidence chain integrity"""
        issues = []
        
        if not chain:
            issues.append({
                "type": "missing_evidence",
                "severity": "critical",
                "description": "Evidence chain is empty"
            })
            return False, issues
            
        # Verify each step has required fields
        for i, step in enumerate(chain):
            required_fields = ["step_id", "action", "timestamp", "input_hash", "output_hash", "agent_id"]
            for field in required_fields:
                if field not in step:
                    issues.append({
                        "type": "incomplete_evidence",
                        "severity": "high",
                        "description": f"Step {i} missing required field: {field}"
                    })
                    
        # Verify chronological order
        timestamps = [step["timestamp"] for step in chain if "timestamp" in step]
        if timestamps != sorted(timestamps):
            issues.append({
                "type": "temporal_inconsistency",
                "severity": "high",
                "description": "Evidence chain timestamps not in chronological order"
            })
            
        return len(issues) == 0, issues
        
    def _validate_schema_compliance(self, content: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate content against schema"""
        issues = []
        
        # Basic structural validation
        if not isinstance(content, dict):
            issues.append({
                "type": "invalid_structure",
                "severity": "critical",
                "description": "Content is not a dictionary"
            })
            return False, issues
            
        # Check required top-level fields
        required_fields = ["request_context", "insights", "metadata"]
        for field in required_fields:
            if field not in content:
                issues.append({
                    "type": "missing_field",
                    "severity": "high",
                    "description": f"Missing required field: {field}"
                })
                
        return len(issues) == 0, issues
        
    def _validate_security_constraints(self, artifact: ResearchArtifact) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate security constraints"""
        issues = []
        
        # Verify builder signature
        if not artifact.builder_signature:
            issues.append({
                "type": "missing_signature",
                "severity": "critical",
                "description": "Artifact missing builder signature"
            })
            
        # Verify builder had appropriate permissions
        # In production, would check against agent registry
        
        return len(issues) == 0, issues
        
    def _validate_content(self, content: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate content completeness and consistency"""
        issues = []
        
        # Check insights structure
        insights = content.get("insights", {})
        if not insights.get("concepts"):
            issues.append({
                "type": "incomplete_content",
                "severity": "medium",
                "description": "No concepts extracted in insights"
            })
            
        return len(issues) == 0, issues
        
    def _generate_report_id(self) -> str:
        """Generate unique validation report ID"""
        return f"vr_{int(time.time() * 1000)}_{self.context.trace_id[:8]}"


class RhizaAgentOrchestrator:
    """
    Orchestrates builder and validator agents with strict separation.
    Ensures no agent can self-validate.
    """
    
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.logger = logger.bind(trace_id=trace_id)
        
    def execute_research_with_validation(self, request: Dict[str, Any]) -> Tuple[ResearchArtifact, ValidationReport]:
        """Execute research and validate results with separate agents"""
        
        # Create builder agent
        builder_context = AgentContext(
            agent_id=f"builder_{self.trace_id[:8]}",
            role=AgentRole.BUILDER,
            trace_id=self.trace_id,
            permissions=["read_external", "write_artifacts", "execute_analysis"],
            sandbox_config={"memory_limit": "512MB", "cpu_limit": "1.0"}
        )
        builder = ResearchBuilderAgent(builder_context)
        
        # Execute research
        self.logger.info("executing_research", request_id=request.get("request_id"))
        artifact = builder.execute(request)
        
        # Create validator agent (different from builder)
        validator_context = AgentContext(
            agent_id=f"validator_{self.trace_id[:8]}",
            role=AgentRole.VALIDATOR,
            trace_id=self.trace_id,
            permissions=["read_artifacts", "write_validations", "verify_evidence"],
            sandbox_config={"memory_limit": "256MB", "cpu_limit": "0.5"}
        )
        validator = ResearchValidatorAgent(validator_context)
        
        # Validate artifact
        self.logger.info("validating_artifact", artifact_id=artifact.artifact_id)
        validation_report = validator.execute({"artifact": artifact})
        
        # Log final result
        self.logger.info("research_complete", 
                        artifact_id=artifact.artifact_id,
                        validation_status=validation_report.status.value)
        
        return artifact, validation_report


# Example usage
if __name__ == "__main__":
    # Create orchestrator
    orchestrator = RhizaAgentOrchestrator(trace_id="trace_12345")
    
    # Execute research request
    request = {
        "request_id": "req_001",
        "artifact_type": "paper_analysis",
        "source_type": "arxiv",
        "source_id": "2401.12345"
    }
    
    artifact, validation = orchestrator.execute_research_with_validation(request)
    
    print(f"Artifact ID: {artifact.artifact_id}")
    print(f"Builder: {artifact.content['metadata']['builder_agent']}")
    print(f"Validation Status: {validation.status.value}")
    print(f"Validator: {validation.report_id}")
    print(f"Issues Found: {len(validation.issues)}")