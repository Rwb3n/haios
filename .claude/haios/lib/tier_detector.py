# generated: 2026-02-19
"""
Governance Tier Detection (WORK-167).

Pure function to compute governance tier from work item frontmatter.
Four tiers per REQ-LIFECYCLE-005 / REQ-CEREMONY-005:
  - trivial: effort=small, source_files<=2, no plan, no ADR, no type=design
  - small:   effort=small, source_files<=3, no ADR
  - standard: default (conservative safe default)
  - architectural: type=design OR ADR in traces_to

Pattern: session_end_actions.py (fail-permissive, _default_project_root).
All errors return "standard" (conservative safe default per REQ-LIFECYCLE-005 invariant:
"Absent data MUST NOT produce a more permissive classification").
"""
import yaml
from pathlib import Path
from typing import Optional


# Conservative safe default — returned on any error or missing data.
_DEFAULT_TIER = "standard"


def _default_project_root() -> Path:
    """Derive project root from this file's location.

    lib/ -> haios/ -> .claude/ -> project root.
    NOT Path.cwd() — hook subprocess cwd is not guaranteed.
    """
    return Path(__file__).parent.parent.parent.parent


def _parse_frontmatter(work_file: Path) -> Optional[dict]:
    """Parse YAML frontmatter from a WORK.md file.

    Uses the established pattern: content.split("---", 2) + yaml.safe_load.
    See epoch_validator.py:128 for the same pattern.

    Args:
        work_file: Path to the WORK.md file.

    Returns:
        Parsed frontmatter dict, or None on any error.
    """
    try:
        content = work_file.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None
        return yaml.safe_load(parts[1]) or {}
    except Exception:
        return None


def _has_adr_reference(traces_to: list) -> bool:
    """Check if any traces_to entry is an ADR reference.

    Matches entries starting with "ADR-" (case-sensitive, per HAIOS convention).

    Args:
        traces_to: List of requirement/ADR reference strings.

    Returns:
        True if any entry starts with "ADR-".
    """
    return any(ref.startswith("ADR-") for ref in traces_to)


def _plan_exists(work_id: str, root: Path) -> bool:
    """Check if a plan file exists for this work item.

    Uses filesystem check (not frontmatter field).
    Convention: docs/work/active/{id}/plans/PLAN.md

    Args:
        work_id: Work item ID (e.g., "WORK-167").
        root: Project root path.

    Returns:
        True if PLAN.md exists at the conventional path.
    """
    plan_path = root / "docs" / "work" / "active" / work_id / "plans" / "PLAN.md"
    return plan_path.exists()


def _log_tier_event(work_id: str, tier: str) -> None:
    """Log a TierDetected governance event. Fail-permissive.

    Uses the canonical log_tier_detected() from governance_events.py.

    Args:
        work_id: Work item ID.
        tier: Detected tier string.
    """
    try:
        from governance_events import log_tier_detected

        log_tier_detected(work_id, tier)
    except Exception:
        pass  # Fail-permissive: logging failure must not affect tier return


def detect_tier(work_id: str, project_root: Optional[Path] = None,
                work_state: Optional[object] = None) -> str:
    """Compute governance tier from work item frontmatter.

    Evaluates computable predicates from REQ-LIFECYCLE-005 to classify
    work items into governance tiers: trivial, small, standard, architectural.

    Evaluation order (matters):
    1. Architectural checked first (escalation always wins)
    2. Conservative defaults for missing/empty fields
    3. Trivial/small predicates (self-contained, not reliant on ordering)
    4. Default: standard

    Args:
        work_id: Work item ID (e.g., "WORK-167").
        project_root: Project root path. Defaults to derived path
                      (same pattern as session_end_actions.py).
        work_state: Optional WorkState object (WORK-174). When provided,
                    fields are extracted from it instead of raw YAML parsing.
                    Uses duck typing (Optional[object]) to avoid circular
                    import between lib/ and modules/.

    Returns:
        One of: "trivial", "small", "standard", "architectural".
        Returns "standard" on any error (conservative safe default).
    """
    try:
        root = project_root or _default_project_root()

        # Read and parse WORK.md frontmatter
        work_file = root / "docs" / "work" / "active" / work_id / "WORK.md"
        if not work_file.exists():
            _log_tier_event(work_id, _DEFAULT_TIER)
            return _DEFAULT_TIER

        # WORK-174: Extract fields from WorkState if provided, else raw YAML
        if work_state is not None:
            work_type = getattr(work_state, "type", None)
            effort = getattr(work_state, "effort", None) or None  # "" -> None
            source_files = getattr(work_state, "source_files", None) or None  # [] -> None
            traces_to = getattr(work_state, "traces_to", None) or []
        else:
            fm = _parse_frontmatter(work_file)
            if fm is None:
                _log_tier_event(work_id, _DEFAULT_TIER)
                return _DEFAULT_TIER

            # Extract fields
            work_type = fm.get("type")
            effort = fm.get("effort")
            source_files = fm.get("source_files")
            traces_to = fm.get("traces_to") or []

        # --- Architectural (checked first — escalation always wins) ---
        if work_type == "design" or _has_adr_reference(traces_to):
            _log_tier_event(work_id, "architectural")
            return "architectural"

        # --- Conservative defaults for missing/empty data ---
        # REQ-LIFECYCLE-005 invariant: "Absent data MUST NOT produce
        # a more permissive classification."
        if effort is None or effort != "small":
            _log_tier_event(work_id, _DEFAULT_TIER)
            return _DEFAULT_TIER

        # Empty list [] treated same as absent (REQ-LIFECYCLE-005 invariant)
        if source_files is None or len(source_files) == 0:
            _log_tier_event(work_id, _DEFAULT_TIER)
            return _DEFAULT_TIER

        sf_count = len(source_files)

        if sf_count > 3:
            _log_tier_event(work_id, _DEFAULT_TIER)
            return _DEFAULT_TIER

        # --- Trivial (self-contained predicate, not reliant on eval order) ---
        has_plan = _plan_exists(work_id, root)
        has_adr = _has_adr_reference(traces_to)

        if (
            sf_count <= 2
            and not has_plan
            and not has_adr
            and work_type != "design"
        ):
            _log_tier_event(work_id, "trivial")
            return "trivial"

        # --- Small ---
        if sf_count <= 3 and not has_adr:
            _log_tier_event(work_id, "small")
            return "small"

        # --- Default: standard ---
        _log_tier_event(work_id, _DEFAULT_TIER)
        return _DEFAULT_TIER

    except Exception:
        # Fail-permissive: any unexpected error returns conservative default
        try:
            _log_tier_event(work_id, _DEFAULT_TIER)
        except Exception:
            pass
        return _DEFAULT_TIER
