# generated: 2026-02-09
"""
Ceremony contract schema, registry, and validation (CH-011, WORK-111, WORK-113).

Defines the data model for ceremony contracts:
- ContractField: Input contract field (field, type, required, description, pattern?)
- OutputField: Output contract field (field, type, guaranteed, description)
- CeremonyContract: Full ceremony contract (name, category, inputs, outputs, side_effects)
- CeremonyRegistry: Collection of all 19 ceremonies loaded from YAML
- RegistryEntry: Single ceremony entry in the registry

Validation (WORK-113):
- ValidationResult: Result of validating inputs/outputs against a contract
- validate_ceremony_input: Check inputs satisfy ceremony's input contract
- validate_ceremony_output: Check outputs satisfy ceremony's output contract
- enforce_ceremony_contract: Governance gate with configurable warn/block

Usage:
    from ceremony_contracts import (
        CeremonyContract, load_ceremony_registry,
        validate_ceremony_input, validate_ceremony_output,
        enforce_ceremony_contract, ValidationResult,
    )

    # Parse contract from skill frontmatter
    contract = CeremonyContract.from_frontmatter(yaml_dict)

    # Validate inputs
    result = validate_ceremony_input(contract, {"work_id": "WORK-113"})

    # Governance gate (reads haios.yaml toggle)
    result = enforce_ceremony_contract(contract, {"work_id": "WORK-113"})

    # Load ceremony registry
    registry = load_ceremony_registry()
    assert len(registry.ceremonies) == 19
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


# Valid ceremony categories (L4/functional_requirements.md)
VALID_CATEGORIES = frozenset(
    ["queue", "session", "closure", "feedback", "memory", "spawn"]
)

# Valid contract field types (WORK-112 critique A6)
VALID_TYPES = frozenset(["string", "boolean", "list", "path", "integer"])

# Valid output guaranteed values (WORK-112 critique A5)
VALID_GUARANTEED = frozenset(["always", "on_success", "on_failure"])


def _validate_category(category: Union[str, List[str]]) -> None:
    """Validate category is one of the 6 valid values, or a list of valid values."""
    if isinstance(category, list):
        for cat in category:
            if cat not in VALID_CATEGORIES:
                raise ValueError(
                    f"Invalid category '{cat}'. Must be one of: {sorted(VALID_CATEGORIES)}"
                )
    elif isinstance(category, str):
        if category not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. Must be one of: {sorted(VALID_CATEGORIES)}"
            )
    else:
        raise ValueError(
            f"Invalid category type {type(category)}. Must be str or list of str."
        )


@dataclass
class ContractField:
    """Input contract field definition.

    Attributes:
        field: Field name (e.g., 'work_id')
        type: Data type - must be one of: string, boolean, list, path, integer
        required: Whether this field is required
        description: Human-readable description
        pattern: Optional regex pattern for validation (e.g., r'WORK-\\d{3}')
    """

    field: str
    type: str
    required: bool
    description: str
    pattern: Optional[str] = None

    def __post_init__(self):
        if self.type not in VALID_TYPES:
            raise ValueError(
                f"Invalid type '{self.type}'. Must be one of: {sorted(VALID_TYPES)}"
            )


@dataclass
class OutputField:
    """Output contract field definition.

    Attributes:
        field: Field name (e.g., 'success')
        type: Data type - must be one of: string, boolean, list, path, integer
        guaranteed: When this field is present - must be one of: always, on_success, on_failure
        description: Human-readable description

    Note (A8): Conditional output validation (on_success/on_failure) is coupled to
    the literal field name "success" in validate_ceremony_output(). All current
    ceremonies use this convention. If a ceremony uses a different field name for
    its success indicator, conditional validation will silently skip enforcement.
    """

    field: str
    type: str
    guaranteed: str
    description: str

    def __post_init__(self):
        if self.guaranteed not in VALID_GUARANTEED:
            raise ValueError(
                f"Invalid guaranteed '{self.guaranteed}'. "
                f"Must be one of: {sorted(VALID_GUARANTEED)}"
            )


@dataclass
class CeremonyContract:
    """Full ceremony contract parsed from skill frontmatter.

    Attributes:
        name: Ceremony name (e.g., 'queue-commit')
        category: Category string or list (e.g., 'queue' or ['closure', 'queue'])
        input_contract: List of input field definitions
        output_contract: List of output field definitions
        side_effects: List of human-readable side effect descriptions
    """

    name: str
    category: Union[str, List[str]]
    input_contract: List[ContractField]
    output_contract: List[OutputField]
    side_effects: List[str]

    def __post_init__(self):
        _validate_category(self.category)

    @classmethod
    def from_frontmatter(cls, data: Dict[str, Any]) -> "CeremonyContract":
        """Parse a CeremonyContract from YAML frontmatter dict.

        Args:
            data: Dict from parsed YAML frontmatter containing
                  name, category, input_contract, output_contract, side_effects.

        Returns:
            CeremonyContract instance.
        """
        input_fields = [
            ContractField(
                field=f["field"],
                type=f["type"],
                required=f["required"],
                description=f["description"],
                pattern=f.get("pattern"),
            )
            for f in data.get("input_contract", [])
        ]

        output_fields = [
            OutputField(
                field=f["field"],
                type=f["type"],
                guaranteed=f["guaranteed"],
                description=f["description"],
            )
            for f in data.get("output_contract", [])
        ]

        return cls(
            name=data["name"],
            category=data["category"],
            input_contract=input_fields,
            output_contract=output_fields,
            side_effects=data.get("side_effects", []),
        )


@dataclass
class RegistryEntry:
    """Single ceremony entry in the registry.

    Attributes:
        name: Ceremony name (e.g., 'intake')
        category: Ceremony category (e.g., 'queue')
        skill: Skill name or None if not implemented
        signature: Type signature (e.g., 'Idea -> BacklogItem')
        side_effects: List of side effect descriptions
        has_contract: Whether YAML contract exists in frontmatter
        has_skill: Whether skill file exists
        notes: Optional notes
    """

    name: str
    category: Union[str, List[str]]
    skill: Optional[str]
    signature: str
    side_effects: List[str] = field(default_factory=list)
    has_contract: bool = False
    has_skill: bool = False
    notes: Optional[str] = None


@dataclass
class CeremonyRegistry:
    """Collection of all ceremonies loaded from registry YAML.

    Attributes:
        version: Registry schema version
        ceremony_count: Expected ceremony count
        ceremonies: List of registry entries
    """

    version: str
    ceremony_count: int
    ceremonies: List[RegistryEntry]


# --- Validation (WORK-113) ---


@dataclass
class ValidationResult:
    """Result of validating inputs/outputs against a contract.

    Attributes:
        valid: True if all checks passed
        errors: List of error/warning descriptions (empty if valid)
    """

    valid: bool
    errors: List[str] = field(default_factory=list)


def validate_ceremony_input(
    contract: CeremonyContract, inputs: Dict[str, Any]
) -> ValidationResult:
    """Validate inputs against ceremony's input contract.

    Checks:
    - Required fields are present
    - Fields with pattern constraints match the regex

    Note: Does NOT perform Python type checking (CH-011 non-goal).
    The 'type' field validates vocabulary only, not runtime types.

    Args:
        contract: Parsed ceremony contract
        inputs: Dict of actual input values

    Returns:
        ValidationResult with valid=True if all required fields present
        and patterns match, else valid=False with error descriptions.
    """
    errors = []
    for field_def in contract.input_contract:
        value = inputs.get(field_def.field)
        if field_def.required and value is None:
            errors.append(f"Required field '{field_def.field}' is missing")
            continue
        if value is not None and field_def.pattern:
            if not re.fullmatch(field_def.pattern, str(value)):
                errors.append(
                    f"Field '{field_def.field}' value '{value}' "
                    f"does not match pattern '{field_def.pattern}'"
                )
    return ValidationResult(valid=len(errors) == 0, errors=errors)


def validate_ceremony_output(
    contract: CeremonyContract, outputs: Dict[str, Any]
) -> ValidationResult:
    """Validate outputs against ceremony's output contract.

    Checks:
    - guaranteed="always" fields must be present
    - guaranteed="on_success" fields required when outputs["success"] is True
    - guaranteed="on_failure" fields required when outputs["success"] is False
    - Warns if contract has on_success/on_failure but no success:always field (A3)

    Note (A8): Conditional validation is coupled to the literal field name "success".
    All current ceremonies use this convention.

    Args:
        contract: Parsed ceremony contract
        outputs: Dict of actual output values

    Returns:
        ValidationResult with valid=True if all guaranteed fields present
        per their condition (always/on_success/on_failure).
    """
    errors = []
    success_value = outputs.get("success")

    for field_def in contract.output_contract:
        value = outputs.get(field_def.field)
        if field_def.guaranteed == "always" and value is None:
            errors.append(
                f"Guaranteed field '{field_def.field}' is missing "
                f"(guaranteed=always)"
            )
        elif (
            field_def.guaranteed == "on_success"
            and success_value is True
            and value is None
        ):
            errors.append(
                f"Field '{field_def.field}' is missing "
                f"(guaranteed=on_success, success=True)"
            )
        elif (
            field_def.guaranteed == "on_failure"
            and success_value is False
            and value is None
        ):
            errors.append(
                f"Field '{field_def.field}' is missing "
                f"(guaranteed=on_failure, success=False)"
            )

    # A3: Warn if contract has on_success/on_failure but no success:always field
    has_conditional = any(
        f.guaranteed in ("on_success", "on_failure")
        for f in contract.output_contract
    )
    has_success_always = any(
        f.field == "success" and f.guaranteed == "always"
        for f in contract.output_contract
    )
    if has_conditional and not has_success_always:
        errors.append(
            f"Warning: contract '{contract.name}' has on_success/on_failure fields "
            f"but no 'success' field with guaranteed=always. "
            f"Conditional validation will be skipped."
        )

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def enforce_ceremony_contract(
    contract: CeremonyContract,
    inputs: Dict[str, Any],
    config_path: Optional[Path] = None,
) -> ValidationResult:
    """Governance gate: validate inputs and enforce per haios.yaml toggle.

    Reads toggles.ceremony_contract_enforcement from haios.yaml:
    - 'warn': log validation errors but allow ceremony to proceed
    - 'block': raise ValueError if validation fails

    Args:
        contract: Parsed ceremony contract
        inputs: Dict of actual input values
        config_path: Optional path to haios.yaml (auto-discovers if None)

    Returns:
        ValidationResult (always returned in warn mode)

    Raises:
        ValueError: If enforcement='block' and validation fails
    """
    result = validate_ceremony_input(contract, inputs)
    if result.valid:
        return result

    # Read enforcement mode from haios.yaml
    enforcement = _read_enforcement_toggle(config_path)

    if enforcement == "block":
        raise ValueError(
            f"Ceremony '{contract.name}' input contract failed "
            f"(enforcement=block): " + "; ".join(result.errors)
        )
    # enforcement == "warn": return result, caller logs but continues
    return result


def _read_enforcement_toggle(config_path: Optional[Path] = None) -> str:
    """Read ceremony_contract_enforcement from haios.yaml. Default: 'warn'.

    Args:
        config_path: Optional explicit path. If None, auto-discovers.

    Returns:
        'warn' or 'block' (defaults to 'warn' on any error).
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "haios.yaml"
        if not config_path.exists():
            config_path = Path(".claude/haios/config/haios.yaml")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("toggles", {}).get(
            "ceremony_contract_enforcement", "warn"
        )
    except (FileNotFoundError, yaml.YAMLError):
        return "warn"


# --- Registry Loading ---


def _find_registry_path() -> Path:
    """Find ceremony_registry.yaml relative to this module or cwd."""
    # Try relative to this file (lib/ -> config/)
    lib_dir = Path(__file__).parent
    config_path = lib_dir.parent / "config" / "ceremony_registry.yaml"
    if config_path.exists():
        return config_path

    # Try relative to cwd (standard HAIOS layout)
    cwd_path = Path(".claude/haios/config/ceremony_registry.yaml")
    if cwd_path.exists():
        return cwd_path

    raise FileNotFoundError(
        "ceremony_registry.yaml not found. Expected at "
        f"{config_path} or {cwd_path}"
    )


def load_ceremony_registry(path: Optional[Path] = None) -> CeremonyRegistry:
    """Load ceremony registry from YAML file.

    Args:
        path: Optional explicit path. If None, auto-discovers.

    Returns:
        CeremonyRegistry with all ceremonies loaded.
    """
    if path is None:
        path = _find_registry_path()

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    ceremonies = []
    for entry in data.get("ceremonies", []):
        ceremonies.append(
            RegistryEntry(
                name=entry["name"],
                category=entry["category"],
                skill=entry.get("skill"),
                signature=entry["signature"],
                side_effects=entry.get("side_effects", []),
                has_contract=entry.get("has_contract", False),
                has_skill=entry.get("has_skill", False),
                notes=entry.get("notes"),
            )
        )

    return CeremonyRegistry(
        version=data.get("version", "1.0"),
        ceremony_count=data.get("ceremony_count", len(ceremonies)),
        ceremonies=ceremonies,
    )
