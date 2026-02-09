# generated: 2026-02-09
"""
Ceremony contract schema and registry (CH-011, WORK-111).

Defines the data model for ceremony contracts:
- ContractField: Input contract field (field, type, required, description, pattern?)
- OutputField: Output contract field (field, type, guaranteed, description)
- CeremonyContract: Full ceremony contract (name, category, inputs, outputs, side_effects)
- CeremonyRegistry: Collection of all 19 ceremonies loaded from YAML
- RegistryEntry: Single ceremony entry in the registry

Usage:
    from ceremony_contracts import CeremonyContract, load_ceremony_registry

    # Parse contract from skill frontmatter
    contract = CeremonyContract.from_frontmatter(yaml_dict)

    # Load ceremony registry
    registry = load_ceremony_registry()
    assert len(registry.ceremonies) == 19
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


# Valid ceremony categories (L4/functional_requirements.md)
VALID_CATEGORIES = frozenset(
    ["queue", "session", "closure", "feedback", "memory", "spawn"]
)


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
        type: Data type (string, boolean, list, path, integer)
        required: Whether this field is required
        description: Human-readable description
        pattern: Optional regex pattern for validation (e.g., r'WORK-\\d{3}')
    """

    field: str
    type: str
    required: bool
    description: str
    pattern: Optional[str] = None


@dataclass
class OutputField:
    """Output contract field definition.

    Attributes:
        field: Field name (e.g., 'success')
        type: Data type (string, boolean, list, path, integer)
        guaranteed: When this field is present (always, on_success, on_failure)
        description: Human-readable description
    """

    field: str
    type: str
    guaranteed: str
    description: str


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
