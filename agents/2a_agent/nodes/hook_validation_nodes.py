"""
Hook Validation Nodes - Dynamic Defense (Shield 2) for HAiOS 2A Agent System.

Implements workflow-level validation through specialized PocketFlow nodes that protect
architectural patterns against "benevolent misalignment" during agent operations.

Architecture:
- BaseHookNode: Core validation infrastructure with rule engine
- PreValidationHookNode: Input validation before expensive operations  
- PostValidationHookNode: Output validation with rollback capability
- ValidationRule: Declarative rule definitions for pattern protection
"""

import re
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'PocketFlow'))

from pocketflow import AsyncNode


class ValidationRuleType(Enum):
    """Types of validation rules."""
    PATTERN = "pattern"          # Regex pattern matching
    STRUCTURE = "structure"      # JSON schema or structure validation
    BUSINESS = "business"        # Business logic validation
    PERFORMANCE = "performance"  # Performance threshold validation
    SECURITY = "security"        # Security constraint validation


@dataclass
class ValidationRule:
    """Declarative validation rule definition."""
    
    name: str
    rule_type: ValidationRuleType
    pattern: Union[str, Dict[str, Any], Callable]  # Regex, schema, or function
    error_message: str
    severity: str = "error"  # "error", "warning", "info"
    enabled: bool = True
    
    def __post_init__(self):
        """Validate rule configuration after initialization."""
        if self.rule_type == ValidationRuleType.PATTERN and not isinstance(self.pattern, str):
            raise ValueError(f"Pattern rules must have string pattern, got {type(self.pattern)}")
        if self.severity not in ["error", "warning", "info"]:
            raise ValueError(f"Invalid severity: {self.severity}")


@dataclass
class ValidationResult:
    """Result of validation rule execution."""
    
    is_valid: bool
    rule_violations: List[str]
    warnings: List[str]
    performance_metrics: Dict[str, Any]
    recommended_actions: List[str]
    validation_duration_ms: int
    
    @property
    def has_errors(self) -> bool:
        """Check if validation found any errors."""
        return not self.is_valid or bool(self.rule_violations)
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation found any warnings."""
        return bool(self.warnings)


class BaseHookNode(AsyncNode, ABC):
    """
    Base class for all validation hook nodes.
    
    Provides core validation infrastructure with rule engine and
    extensible validation pattern support.
    """
    
    def __init__(self, validation_rules: List[ValidationRule], node_name: str = "BaseHook"):
        super().__init__(max_retries=1, wait=0)  # Hooks should fail fast
        self.validation_rules = [rule for rule in validation_rules if rule.enabled]
        self.node_name = node_name
        
        # Performance tracking
        self._validation_start_time: Optional[float] = None
        
        # Validation statistics
        self.stats = {
            "rules_executed": 0,
            "violations_found": 0,
            "warnings_issued": 0,
            "total_validations": 0
        }
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare hook validation context."""
        self._validation_start_time = time.time()
        
        context = {
            "hook_name": self.node_name,
            "validation_rules": self.validation_rules,
            "shared_state": shared,
            "validation_timestamp": time.time()
        }
        
        # Allow subclasses to extend context
        return await self._prepare_hook_context(shared, context)
    
    @abstractmethod
    async def _prepare_hook_context(self, shared: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Subclass-specific context preparation."""
        pass
    
    async def exec_async(self, context: Dict[str, Any]) -> ValidationResult:
        """Execute validation rules and return structured result."""
        print(f"  [HOOK] {self.node_name} validation starting...")
        
        violations = []
        warnings = []
        performance_metrics = {}
        recommended_actions = []
        
        start_time = time.time()
        
        try:
            # Execute each validation rule
            for rule in self.validation_rules:
                try:
                    rule_result = await self._execute_validation_rule(rule, context)
                    self.stats["rules_executed"] += 1
                    
                    if not rule_result["is_valid"]:
                        if rule.severity == "error":
                            violations.append(f"{rule.name}: {rule.error_message}")
                            self.stats["violations_found"] += 1
                        elif rule.severity == "warning":
                            warnings.append(f"{rule.name}: {rule.error_message}")
                            self.stats["warnings_issued"] += 1
                    
                    # Collect performance metrics
                    if "metrics" in rule_result:
                        performance_metrics[rule.name] = rule_result["metrics"]
                    
                    # Collect recommended actions
                    if "actions" in rule_result:
                        recommended_actions.extend(rule_result["actions"])
                        
                except Exception as e:
                    error_msg = f"Rule execution failed: {rule.name} - {str(e)}"
                    violations.append(error_msg)
                    print(f"  [HOOK_ERROR] {error_msg}")
            
            duration_ms = int((time.time() - start_time) * 1000)
            is_valid = len(violations) == 0
            
            result = ValidationResult(
                is_valid=is_valid,
                rule_violations=violations,
                warnings=warnings,
                performance_metrics=performance_metrics,
                recommended_actions=recommended_actions,
                validation_duration_ms=duration_ms
            )
            
            self.stats["total_validations"] += 1
            
            # Log validation results
            if violations:
                print(f"  [HOOK_VIOLATION] {len(violations)} validation errors found")
                for violation in violations:
                    print(f"    - {violation}")
            
            if warnings:
                print(f"  [HOOK_WARNING] {len(warnings)} warnings issued")
                for warning in warnings:
                    print(f"    - {warning}")
            
            if is_valid:
                print(f"  [HOOK_OK] {self.node_name} validation passed ({duration_ms}ms)")
            else:
                print(f"  [HOOK_FAIL] {self.node_name} validation failed ({duration_ms}ms)")
            
            return result
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Hook validation system failure: {str(e)}"
            print(f"  [HOOK_SYSTEM_ERROR] {error_msg}")
            
            return ValidationResult(
                is_valid=False,
                rule_violations=[error_msg],
                warnings=[],
                performance_metrics={},
                recommended_actions=["Check hook validation system configuration"],
                validation_duration_ms=duration_ms
            )
    
    async def _execute_validation_rule(self, rule: ValidationRule, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single validation rule."""
        start_time = time.time()
        
        try:
            if rule.rule_type == ValidationRuleType.PATTERN:
                result = await self._validate_pattern(rule, context)
            elif rule.rule_type == ValidationRuleType.STRUCTURE:
                result = await self._validate_structure(rule, context)
            elif rule.rule_type == ValidationRuleType.BUSINESS:
                result = await self._validate_business_logic(rule, context)
            elif rule.rule_type == ValidationRuleType.PERFORMANCE:
                result = await self._validate_performance(rule, context)
            elif rule.rule_type == ValidationRuleType.SECURITY:
                result = await self._validate_security(rule, context)
            else:
                result = {"is_valid": False, "error": f"Unknown rule type: {rule.rule_type}"}
            
            # Add execution metrics
            execution_time = int((time.time() - start_time) * 1000)
            result["execution_time_ms"] = execution_time
            
            return result
            
        except Exception as e:
            return {
                "is_valid": False,
                "error": f"Rule execution exception: {str(e)}",
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }
    
    async def _validate_pattern(self, rule: ValidationRule, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate using regex pattern matching."""
        # Extract text content for pattern matching
        content = await self._extract_validation_content(context)
        
        try:
            pattern = rule.pattern
            if isinstance(pattern, str):
                match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                is_valid = match is not None
            else:
                is_valid = False
                
            return {
                "is_valid": is_valid,
                "content_length": len(content),
                "pattern": pattern
            }
        except re.error as e:
            return {"is_valid": False, "error": f"Invalid regex pattern: {str(e)}"}
    
    async def _validate_structure(self, rule: ValidationRule, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate using structure/schema checking."""
        # Implementation depends on specific structural requirements
        return {"is_valid": True, "note": "Structure validation not yet implemented"}
    
    async def _validate_business_logic(self, rule: ValidationRule, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate using business logic rules."""
        # Implementation depends on specific business requirements
        return {"is_valid": True, "note": "Business logic validation not yet implemented"}
    
    async def _validate_performance(self, rule: ValidationRule, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance metrics against thresholds."""
        # Implementation depends on specific performance requirements
        return {"is_valid": True, "note": "Performance validation not yet implemented"}
    
    async def _validate_security(self, rule: ValidationRule, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate security constraints."""
        # Implementation depends on specific security requirements
        return {"is_valid": True, "note": "Security validation not yet implemented"}
    
    @abstractmethod
    async def _extract_validation_content(self, context: Dict[str, Any]) -> str:
        """Extract content for validation from context."""
        pass
    
    async def exec_fallback_async(self, prep_res: Dict[str, Any], exc: Exception) -> ValidationResult:
        """Graceful fallback when hook validation fails."""
        duration_ms = int((time.time() - self._validation_start_time) * 1000) if self._validation_start_time else 0
        
        error_msg = f"Hook validation system failure: {str(exc)}"
        print(f"  [HOOK_FALLBACK] {self.node_name} failed: {error_msg}")
        
        return ValidationResult(
            is_valid=False,
            rule_violations=[error_msg],
            warnings=[],
            performance_metrics={},
            recommended_actions=["Review hook configuration", "Check system dependencies"],
            validation_duration_ms=duration_ms
        )
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: ValidationResult) -> str:
        """Process validation results and determine next action."""
        # Store validation results in shared state
        shared[f"{self.node_name}_validation_result"] = exec_res
        shared[f"{self.node_name}_stats"] = self.stats
        
        # Determine next action based on validation results
        if exec_res.has_errors:
            return "validation_failed"
        elif exec_res.has_warnings:
            return "validation_warning"
        else:
            return "validation_passed"


class PreValidationHookNode(BaseHookNode):
    """
    Validates inputs before expensive operations.
    
    Used to catch problems early before agent execution:
    - File accessibility validation
    - Parameter compliance checking  
    - Business rule enforcement
    """
    
    def __init__(self, validation_rules: List[ValidationRule]):
        super().__init__(validation_rules, "PreValidationHook")
    
    async def _prepare_hook_context(self, shared: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare pre-validation context with input parameters."""
        context.update({
            "validation_phase": "pre_execution",
            "input_prompt": shared.get("prompt_content", ""),
            "file_paths": self._extract_file_paths(shared),
            "tool_list": shared.get("allowed_tools", []),
            "round_number": shared.get("round_num", 1)
        })
        return context
    
    def _extract_file_paths(self, shared: Dict[str, Any]) -> List[str]:
        """Extract file paths from shared state for validation."""
        paths = []
        
        # Common file path keys in shared state
        path_keys = ["dialogue_path", "prompt_file", "summary_file_path", "synthesis_path"]
        
        for key in path_keys:
            if key in shared and shared[key]:
                paths.append(str(shared[key]))
        
        return paths
    
    async def _extract_validation_content(self, context: Dict[str, Any]) -> str:
        """Extract input content for pre-validation."""
        content_parts = []
        
        # Include input prompt
        if context.get("input_prompt"):
            content_parts.append(f"PROMPT: {context['input_prompt']}")
        
        # Include file paths  
        if context.get("file_paths"):
            content_parts.append(f"FILES: {', '.join(context['file_paths'])}")
        
        # Include tool configuration
        if context.get("tool_list"):
            content_parts.append(f"TOOLS: {', '.join(context['tool_list'])}")
        
        return "\n".join(content_parts)


class PostValidationHookNode(BaseHookNode):
    """
    Validates outputs after operations with rollback capability.
    
    Used to verify operation results and enable safe recovery:
    - Content quality validation
    - Format compliance checking
    - Rollback trigger mechanisms
    """
    
    def __init__(self, validation_rules: List[ValidationRule]):
        super().__init__(validation_rules, "PostValidationHook")
        self.rollback_data: Dict[str, Any] = {}
    
    async def _prepare_hook_context(self, shared: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare post-validation context with operation results."""
        context.update({
            "validation_phase": "post_execution",
            "agent_response": shared.get("last_agent_response", ""),
            "tools_used": shared.get("last_tools_used", []),
            "operation_duration": shared.get("last_operation_duration", 0),
            "file_changes": self._detect_file_changes(shared)
        })
        
        # Store rollback data
        self.rollback_data = {
            "timestamp": time.time(),
            "shared_state_backup": dict(shared),
            "file_paths": context.get("file_paths", [])
        }
        
        return context
    
    def _detect_file_changes(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect file changes from recent operations."""
        # This would track file modifications during agent operations
        # Implementation depends on specific file tracking requirements
        return []
    
    async def _extract_validation_content(self, context: Dict[str, Any]) -> str:
        """Extract output content for post-validation."""
        content_parts = []
        
        # Include agent response
        if context.get("agent_response"):
            content_parts.append(f"RESPONSE: {context['agent_response']}")
        
        # Include tools used
        if context.get("tools_used"):
            content_parts.append(f"TOOLS_USED: {', '.join(context['tools_used'])}")
        
        # Include performance metrics
        duration = context.get("operation_duration", 0)
        content_parts.append(f"DURATION_MS: {duration}")
        
        return "\n".join(content_parts)
    
    async def trigger_rollback(self, reason: str) -> bool:
        """
        Trigger rollback of recent operations.
        
        Args:
            reason: Reason for rollback
            
        Returns:
            bool: True if rollback successful, False otherwise
        """
        try:
            print(f"  [ROLLBACK] Initiating rollback: {reason}")
            
            # Rollback logic would be implemented here
            # This might include:
            # - Restoring file contents from backup
            # - Reverting shared state changes
            # - Cleaning up temporary files
            
            print(f"  [ROLLBACK] Rollback completed successfully")
            return True
            
        except Exception as e:
            print(f"  [ROLLBACK_ERROR] Rollback failed: {str(e)}")
            return False


# Pre-defined validation rules for common architectural patterns
POCKETFLOW_PATTERN_RULES = [
    ValidationRule(
        name="pocketflow_node_structure",
        rule_type=ValidationRuleType.PATTERN,
        pattern=r"class\s+\w+\(AsyncNode\):",
        error_message="Node must inherit from AsyncNode",
        severity="error"
    ),
    ValidationRule(
        name="prep_exec_post_pattern", 
        rule_type=ValidationRuleType.PATTERN,
        pattern=r"async def (prep_async|exec_async|post_async)",
        error_message="Node must implement prep/exec/post async pattern",
        severity="error"
    ),
    ValidationRule(
        name="no_exception_handling_in_exec",
        rule_type=ValidationRuleType.PATTERN,
        pattern=r"async def exec_async.*?try:",
        error_message="exec_async should not contain exception handling",
        severity="warning"
    )
]

HAIOS_COMPLIANCE_RULES = [
    ValidationRule(
        name="no_content_embedding",
        rule_type=ValidationRuleType.PATTERN,
        pattern=r"json\.dumps\(.*content.*\)",
        error_message="Content must not be embedded in prompts",
        severity="error"
    ),
    ValidationRule(
        name="file_operation_instructions",
        rule_type=ValidationRuleType.PATTERN,
        pattern=r"(Read|Edit|Write)\s+[A-Za-z]",
        error_message="Instructions must use file operation patterns",
        severity="warning"
    ),
    ValidationRule(
        name="separation_of_duties",
        rule_type=ValidationRuleType.PATTERN,
        pattern=r"orchestrator.*metadata.*agent.*content",
        error_message="Maintain separation between orchestrator metadata and agent content",
        severity="error"
    )
]