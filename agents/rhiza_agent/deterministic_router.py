"""
Deterministic Research Router for Rhiza Agent
Replaces LLM-based routing with rule-based decision system
"""
import json
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import hashlib


class WorkflowType(Enum):
    CHAIN = "chain"  # Sequential, depth-first processing
    PARALLEL = "parallel"  # Concurrent, breadth-first processing  
    TRIAGE = "triage"  # Categorization and prioritization
    

class ResearchScope(Enum):
    SINGLE_PAPER = "single_paper"
    TOPIC_SURVEY = "topic_survey"
    STRATEGIC_SCAN = "strategic_scan"
    CRYSTAL_EXTRACTION = "crystal_extraction"


@dataclass
class ResearchRequest:
    """Validated research request with deterministic routing metadata"""
    request_id: str
    trace_id: str
    scope: ResearchScope
    parameters: Dict[str, Any]
    constraints: Dict[str, Any]
    security_context: Dict[str, Any]
    

@dataclass
class ResearchPlan:
    """Deterministic execution plan for research request"""
    plan_id: str
    workflow_type: WorkflowType
    steps: List[Dict[str, Any]]
    evidence_requirements: List[str]
    validation_criteria: Dict[str, Any]
    execution_budget: Dict[str, int]  # time_seconds, max_papers, etc.


class DeterministicResearchRouter:
    """
    Rule-based routing system for Rhiza research requests.
    No LLM involvement - all decisions based on explicit rules.
    """
    
    def __init__(self, config_path: str = "router_config.json"):
        self.config = self._load_config(config_path)
        self.routing_rules = self._initialize_routing_rules()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load router configuration with validation"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            # Validate required fields
            required = ["execution_budgets", "security_levels", "validation_rules"]
            for field in required:
                if field not in config:
                    raise ValueError(f"Missing required config field: {field}")
            return config
        except FileNotFoundError:
            # Return default config if file doesn't exist
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for router"""
        return {
            "execution_budgets": {
                "single_paper": {"time_seconds": 60, "max_tokens": 10000},
                "topic_survey": {"time_seconds": 300, "max_papers": 50},
                "strategic_scan": {"time_seconds": 600, "max_categories": 10},
                "crystal_extraction": {"time_seconds": 120, "max_concepts": 20}
            },
            "security_levels": {
                "single_paper": "standard",
                "topic_survey": "standard", 
                "strategic_scan": "elevated",
                "crystal_extraction": "elevated"
            },
            "validation_rules": {
                "require_schema_validation": True,
                "require_evidence_chain": True,
                "require_separate_validator": True
            }
        }
        
    def _initialize_routing_rules(self) -> Dict[ResearchScope, WorkflowType]:
        """Initialize deterministic routing rules"""
        return {
            ResearchScope.SINGLE_PAPER: WorkflowType.CHAIN,
            ResearchScope.TOPIC_SURVEY: WorkflowType.PARALLEL,
            ResearchScope.STRATEGIC_SCAN: WorkflowType.TRIAGE,
            ResearchScope.CRYSTAL_EXTRACTION: WorkflowType.CHAIN
        }
        
    def route_request(self, request: ResearchRequest) -> ResearchPlan:
        """
        Deterministically route research request to appropriate workflow.
        All decisions based on explicit rules, no LLM involvement.
        """
        # Validate request
        self._validate_request(request)
        
        # Determine workflow type based on scope
        workflow_type = self.routing_rules[request.scope]
        
        # Build execution plan
        plan = self._build_execution_plan(request, workflow_type)
        
        # Apply security constraints
        plan = self._apply_security_constraints(plan, request)
        
        # Set execution budget
        plan.execution_budget = self._get_execution_budget(request.scope)
        
        return plan
        
    def _validate_request(self, request: ResearchRequest) -> None:
        """Validate request against security and business rules"""
        # Check request has required fields
        if not request.trace_id:
            raise ValueError("Request missing trace_id")
            
        # Validate scope-specific parameters
        if request.scope == ResearchScope.SINGLE_PAPER:
            if "paper_id" not in request.parameters:
                raise ValueError("Single paper request missing paper_id")
                
        elif request.scope == ResearchScope.TOPIC_SURVEY:
            if "topic" not in request.parameters:
                raise ValueError("Topic survey request missing topic")
                
        # Validate security context
        if "user_id" not in request.security_context:
            raise ValueError("Request missing user_id in security context")
            
    def _build_execution_plan(self, 
                            request: ResearchRequest, 
                            workflow_type: WorkflowType) -> ResearchPlan:
        """Build concrete execution plan based on workflow type"""
        plan_id = self._generate_plan_id(request)
        
        if workflow_type == WorkflowType.CHAIN:
            steps = self._build_chain_steps(request)
        elif workflow_type == WorkflowType.PARALLEL:
            steps = self._build_parallel_steps(request)
        elif workflow_type == WorkflowType.TRIAGE:
            steps = self._build_triage_steps(request)
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
            
        # Define evidence requirements based on scope
        evidence_requirements = self._get_evidence_requirements(request.scope)
        
        # Define validation criteria
        validation_criteria = self._get_validation_criteria(request.scope)
        
        return ResearchPlan(
            plan_id=plan_id,
            workflow_type=workflow_type,
            steps=steps,
            evidence_requirements=evidence_requirements,
            validation_criteria=validation_criteria,
            execution_budget={}  # Set later
        )
        
    def _build_chain_steps(self, request: ResearchRequest) -> List[Dict[str, Any]]:
        """Build sequential processing steps"""
        if request.scope == ResearchScope.SINGLE_PAPER:
            return [
                {
                    "step_id": "fetch_paper",
                    "action": "fetch_arxiv_paper",
                    "params": {"paper_id": request.parameters["paper_id"]},
                    "timeout": 30
                },
                {
                    "step_id": "extract_content", 
                    "action": "extract_paper_content",
                    "depends_on": ["fetch_paper"],
                    "timeout": 30
                },
                {
                    "step_id": "analyze_relevance",
                    "action": "analyze_paper_relevance",
                    "depends_on": ["extract_content"],
                    "timeout": 60
                },
                {
                    "step_id": "generate_artifact",
                    "action": "create_research_artifact",
                    "depends_on": ["analyze_relevance"],
                    "timeout": 30
                }
            ]
        elif request.scope == ResearchScope.CRYSTAL_EXTRACTION:
            return [
                {
                    "step_id": "load_paper",
                    "action": "load_paper_artifact",
                    "params": {"artifact_id": request.parameters["artifact_id"]},
                    "timeout": 10
                },
                {
                    "step_id": "extract_concepts",
                    "action": "extract_key_concepts",
                    "depends_on": ["load_paper"],
                    "timeout": 60
                },
                {
                    "step_id": "map_to_haios",
                    "action": "map_concepts_to_architecture", 
                    "depends_on": ["extract_concepts"],
                    "timeout": 60
                },
                {
                    "step_id": "generate_proposal",
                    "action": "create_crystal_seed_proposal",
                    "depends_on": ["map_to_haios"],
                    "timeout": 30
                }
            ]
        else:
            raise ValueError(f"No chain steps defined for scope: {request.scope}")
            
    def _build_parallel_steps(self, request: ResearchRequest) -> List[Dict[str, Any]]:
        """Build parallel processing steps for topic surveys"""
        return [
            {
                "step_id": "fetch_papers",
                "action": "fetch_topic_papers",
                "params": {
                    "topic": request.parameters["topic"],
                    "max_papers": request.parameters.get("max_papers", 20)
                },
                "timeout": 60
            },
            {
                "step_id": "parallel_analysis",
                "action": "parallel_paper_analysis",
                "depends_on": ["fetch_papers"],
                "parallel": True,
                "max_workers": 5,
                "timeout": 300
            },
            {
                "step_id": "aggregate_results",
                "action": "aggregate_analysis_results",
                "depends_on": ["parallel_analysis"],
                "timeout": 60
            },
            {
                "step_id": "generate_report",
                "action": "create_survey_report",
                "depends_on": ["aggregate_results"],
                "timeout": 30
            }
        ]
        
    def _build_triage_steps(self, request: ResearchRequest) -> List[Dict[str, Any]]:
        """Build triage workflow steps for strategic scanning"""
        return [
            {
                "step_id": "scan_landscape",
                "action": "scan_research_landscape",
                "params": {
                    "categories": request.parameters.get("categories", ["cs.AI"]),
                    "time_window": request.parameters.get("time_window", "7d")
                },
                "timeout": 120
            },
            {
                "step_id": "categorize_papers",
                "action": "categorize_by_relevance",
                "depends_on": ["scan_landscape"],
                "routing_rules": {
                    "tier_1": {"action": "deep_analysis"},
                    "tier_2": {"action": "standard_analysis"},
                    "tier_3": {"action": "archive_only"}
                },
                "timeout": 180
            },
            {
                "step_id": "process_tiers",
                "action": "process_by_tier",
                "depends_on": ["categorize_papers"],
                "timeout": 300
            },
            {
                "step_id": "generate_priorities",
                "action": "create_priority_report",
                "depends_on": ["process_tiers"],
                "timeout": 60
            }
        ]
        
    def _get_evidence_requirements(self, scope: ResearchScope) -> List[str]:
        """Define evidence requirements for each research scope"""
        base_requirements = [
            "source_url_verification",
            "content_hash_validation",
            "timestamp_authentication"
        ]
        
        scope_specific = {
            ResearchScope.SINGLE_PAPER: [
                "paper_metadata_complete",
                "full_text_extracted"
            ],
            ResearchScope.TOPIC_SURVEY: [
                "paper_count_verification",
                "relevance_scoring_audit"
            ],
            ResearchScope.STRATEGIC_SCAN: [
                "category_coverage_proof",
                "triage_criteria_documentation"
            ],
            ResearchScope.CRYSTAL_EXTRACTION: [
                "concept_extraction_trace",
                "haios_mapping_validation"
            ]
        }
        
        return base_requirements + scope_specific.get(scope, [])
        
    def _get_validation_criteria(self, scope: ResearchScope) -> Dict[str, Any]:
        """Define validation criteria for research outputs"""
        return {
            "schema_validation": {
                "required": True,
                "schema_version": "1.0",
                "strict_mode": True
            },
            "evidence_validation": {
                "require_source_links": True,
                "require_content_hash": True,
                "require_extraction_trace": True
            },
            "security_validation": {
                "require_sanitized_inputs": True,
                "require_sandboxed_execution": True,
                "max_execution_time": self.config["execution_budgets"][scope.value]["time_seconds"]
            }
        }
        
    def _apply_security_constraints(self, 
                                  plan: ResearchPlan, 
                                  request: ResearchRequest) -> ResearchPlan:
        """Apply security constraints to execution plan"""
        security_level = self.config["security_levels"][request.scope.value]
        
        if security_level == "elevated":
            # Add additional validation steps
            plan.steps.append({
                "step_id": "security_scan",
                "action": "run_security_validation",
                "params": {"scan_level": "comprehensive"},
                "timeout": 30
            })
            
            # Reduce parallelism for better monitoring
            for step in plan.steps:
                if step.get("parallel"):
                    step["max_workers"] = min(step["max_workers"], 3)
                    
        # Add audit logging to all steps
        for step in plan.steps:
            step["audit"] = {
                "log_inputs": True,
                "log_outputs": True,
                "trace_id": request.trace_id
            }
            
        return plan
        
    def _get_execution_budget(self, scope: ResearchScope) -> Dict[str, int]:
        """Get execution budget for research scope"""
        return self.config["execution_budgets"][scope.value]
        
    def _generate_plan_id(self, request: ResearchRequest) -> str:
        """Generate deterministic plan ID"""
        content = f"{request.request_id}_{request.scope.value}_{request.trace_id}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


# Example usage
if __name__ == "__main__":
    # Initialize router
    router = DeterministicResearchRouter()
    
    # Example: Route a single paper analysis request
    request = ResearchRequest(
        request_id="req_001",
        trace_id="trace_12345",
        scope=ResearchScope.SINGLE_PAPER,
        parameters={"paper_id": "2401.12345"},
        constraints={"max_time": 120},
        security_context={"user_id": "user_001", "role": "researcher"}
    )
    
    plan = router.route_request(request)
    
    print(f"Generated Plan: {plan.plan_id}")
    print(f"Workflow Type: {plan.workflow_type.value}")
    print(f"Steps: {len(plan.steps)}")
    print(f"Evidence Requirements: {plan.evidence_requirements}")
    print(f"Execution Budget: {plan.execution_budget}")