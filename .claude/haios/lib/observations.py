# generated: 2025-12-28
# System Auto: last updated on: 2026-01-21T22:19:10
"""Observation capture, triage, and retro-triage module for HAIOS.

Provides validation and surfacing for the observation capture gate
in close-work-cycle. Prevents "Ceremonial completion" anti-pattern.

Capture Functions (E2-217):
1. validate_observations() - Check if observations gate is crossed
2. scaffold_observations() - Create observations.md for work item
3. scan_uncaptured_observations() - Find work items with pending observations

Triage Functions (E2-218):
4. parse_observations() - Parse observations.md into structured list
5. triage_observation() - Apply triage dimensions (category/action/priority)
6. scan_archived_observations() - Find archived items with untriaged observations
7. promote_observation() - Execute triage action (spawn, memory, discuss, dismiss)

Threshold Functions (E2-224):
8. get_pending_observation_count() - Count pending observations across archive
9. should_trigger_triage() - Check if count exceeds threshold

Retro-Triage Functions (WORK-143):
10. query_retro_kss() - Query memory for K/S/S directive entries
11. query_retro_bugs() - Query memory for bug candidate entries
12. query_retro_features() - Query memory for feature candidate entries
13. aggregate_kss_frequency() - Aggregate K/S/S directives by frequency
14. surface_bug_candidates() - Parse bug entries with confidence sorting
15. surface_feature_candidates() - Parse feature entries with confidence sorting
"""

import re
from pathlib import Path
from typing import Optional

from config import ConfigLoader

# Project root is 4 levels up from .claude/haios/lib/
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def validate_observations(work_id: str) -> dict:
    """Validate that observations gate is properly crossed for a work item.

    The gate is "crossed" if EITHER:
    1. All three "None observed" checkboxes are checked ([x]), OR
    2. At least one actual observation is added (beyond the None observed items)

    The gate is "skipped" if:
    1. observations.md doesn't exist, OR
    2. "None observed" items are unchecked AND no actual observations added

    Args:
        work_id: The work item ID (e.g., E2-215, INV-046)

    Returns:
        dict with:
        - valid: bool - True if gate is properly crossed
        - exists: bool - True if observations.md exists
        - none_observed_count: int - Number of "None observed" items checked
        - observation_count: int - Number of actual observations added
        - message: str - Human-readable status or error message
    """
    # Find observations file
    obs_path = _find_observations_file(work_id)

    if not obs_path:
        return {
            "valid": False,
            "exists": False,
            "none_observed_count": 0,
            "observation_count": 0,
            "message": f"observations.md not found for {work_id}. Create via scaffold."
        }

    # Read content
    content = obs_path.read_text(encoding="utf-8")

    # Count checked "None observed" items
    # Pattern: [x] **None observed** (case insensitive for x/X)
    none_observed_checked = len(re.findall(
        r'\[x\]\s*\*\*None observed\*\*',
        content,
        re.IGNORECASE
    ))

    # Count unchecked "None observed" items
    none_observed_unchecked = len(re.findall(
        r'\[ \]\s*\*\*None observed\*\*',
        content
    ))

    # Count actual observations (checked items that aren't "None observed")
    # These are: [x] followed by text that doesn't contain "**None observed**"
    all_checked = re.findall(r'\[x\]\s*([^\n]+)', content, re.IGNORECASE)
    actual_observations = [
        item for item in all_checked
        if '**None observed**' not in item
    ]

    # Validation logic
    total_sections = 3  # Unexpected Behaviors, Gaps Noticed, Future Considerations

    if none_observed_checked == total_sections:
        # All "None observed" checked - gate crossed explicitly
        return {
            "valid": True,
            "exists": True,
            "none_observed_count": none_observed_checked,
            "observation_count": len(actual_observations),
            "message": "Observation gate crossed: All sections marked 'None observed'."
        }

    if len(actual_observations) > 0:
        # Actual observations added - gate crossed implicitly
        return {
            "valid": True,
            "exists": True,
            "none_observed_count": none_observed_checked,
            "observation_count": len(actual_observations),
            "message": f"Observation gate crossed: {len(actual_observations)} observation(s) captured."
        }

    # Gate not crossed
    unchecked = total_sections - none_observed_checked
    return {
        "valid": False,
        "exists": True,
        "none_observed_count": none_observed_checked,
        "observation_count": 0,
        "message": (
            f"BLOCKED: Observation gate not crossed. "
            f"{unchecked} section(s) have unchecked 'None observed'. "
            "Either add observations or check 'None observed' in each section."
        )
    }


def scaffold_observations(work_id: str) -> Optional[Path]:
    """Create observations.md for a work item if it doesn't exist.

    Args:
        work_id: The work item ID (e.g., E2-215)

    Returns:
        Path to created/existing observations file, or None if work dir doesn't exist.
    """
    from scaffold import scaffold_template

    # Check if work directory exists
    work_dir = PROJECT_ROOT / ConfigLoader.get().get_path("work_active") / work_id
    if not work_dir.exists():
        # Try archive
        work_dir = PROJECT_ROOT / ConfigLoader.get().get_path("work_archive") / work_id
        if not work_dir.exists():
            return None

    obs_path = work_dir / "observations.md"
    if obs_path.exists():
        return obs_path

    # Create via scaffold
    result = scaffold_template("observations", backlog_id=work_id)
    return Path(result)


def scan_uncaptured_observations() -> list[dict]:
    """Scan all active work items for uncaptured observations.

    Used by /audit to surface work items that need observation capture.

    Returns:
        List of dicts with work_id, status, and message for items needing attention.
    """
    results = []
    active_dir = PROJECT_ROOT / ConfigLoader.get().get_path("work_active")

    if not active_dir.exists():
        return results

    for work_dir in active_dir.iterdir():
        if not work_dir.is_dir():
            continue

        work_id = work_dir.name
        obs_path = work_dir / "observations.md"

        if not obs_path.exists():
            results.append({
                "work_id": work_id,
                "status": "missing",
                "message": "observations.md not created"
            })
            continue

        # Check if pending (status: pending in frontmatter)
        content = obs_path.read_text(encoding="utf-8")
        if "status: pending" in content:
            validation = validate_observations(work_id)
            if not validation["valid"]:
                results.append({
                    "work_id": work_id,
                    "status": "pending",
                    "message": validation["message"]
                })

    return results


def _find_observations_file(work_id: str) -> Optional[Path]:
    """Find observations.md for a work item.

    Checks both active and archive directories.

    Args:
        work_id: The work item ID

    Returns:
        Path to observations.md or None if not found.
    """
    # Try active first
    active_path = PROJECT_ROOT / ConfigLoader.get().get_path("work_active") / work_id / "observations.md"
    if active_path.exists():
        return active_path

    # Try archive
    archive_path = PROJECT_ROOT / ConfigLoader.get().get_path("work_archive") / work_id / "observations.md"
    if archive_path.exists():
        return archive_path

    return None


# =============================================================================
# TRIAGE FUNCTIONS (E2-218)
# =============================================================================

# Valid dimension values for observation triage
VALID_CATEGORIES = {"bug", "gap", "debt", "insight", "question", "noise"}
VALID_ACTIONS = {"spawn:INV", "spawn:WORK", "spawn:FIX", "memory", "discuss", "dismiss"}
VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}


def parse_observations(content: str) -> list[dict]:
    """Parse observations.md into structured list.

    Args:
        content: Raw markdown content

    Returns:
        List of dicts with text, section for each checked observation.
    """
    results = []
    current_section = None

    for line in content.split("\n"):
        # Track section headers
        if line.startswith("## "):
            current_section = line[3:].strip()
            continue

        # Find checked items (not "None observed")
        # Match: - [x] or - [X] at start of line (with optional leading whitespace)
        match = re.match(r'^-?\s*\[x\]\s*(.+)', line, re.IGNORECASE)
        if match and current_section:
            text = match.group(1).strip()
            # Skip "None observed" entries
            if "**None observed**" in text:
                continue
            results.append({
                "text": text,
                "section": current_section
            })

    return results


def triage_observation(obs: dict, category: str, action: str, priority: str) -> dict:
    """Apply triage dimensions to an observation.

    Args:
        obs: Observation dict with text and section
        category: bug|gap|debt|insight|question|noise
        action: spawn:INV|spawn:WORK|spawn:FIX|memory|discuss|dismiss
        priority: P0|P1|P2|P3

    Returns:
        Observation dict with triage fields added

    Raises:
        ValueError: If any dimension is invalid
    """
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category: {category}. Valid: {VALID_CATEGORIES}")
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid action: {action}. Valid: {VALID_ACTIONS}")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority: {priority}. Valid: {VALID_PRIORITIES}")

    return {
        **obs,
        "category": category,
        "action": action,
        "priority": priority
    }


def scan_archived_observations(base_path: Optional[Path] = None) -> list[dict]:
    """Scan archived work items for untriaged observations.

    Args:
        base_path: Override project root (for testing)

    Returns:
        List of dicts with work_id, path, observations for pending items.
    """
    root = base_path or PROJECT_ROOT
    archive_dir = root / "docs" / "work" / "archive"

    if not archive_dir.exists():
        return []

    results = []
    for work_dir in archive_dir.iterdir():
        if not work_dir.is_dir():
            continue

        obs_path = work_dir / "observations.md"
        if not obs_path.exists():
            continue

        content = obs_path.read_text(encoding="utf-8")
        # Check triage_status in frontmatter
        # Include if: triage_status: pending OR triage_status field is missing (legacy)
        if "triage_status: triaged" in content:
            continue  # Skip already triaged

        observations = parse_observations(content)
        if observations:
            results.append({
                "work_id": work_dir.name,
                "path": obs_path,
                "observations": observations
            })

    return results


def promote_observation(obs: dict) -> dict:
    """Execute the action for a triaged observation.

    Args:
        obs: Triaged observation with category, action, priority

    Returns:
        Dict with result of promotion (spawned_id, memory_id, or status)
    """
    action = obs.get("action", "")

    if action == "dismiss":
        return {"status": "dismissed", "message": "No action needed"}

    if action == "discuss":
        return {"status": "flagged", "message": "Flagged for operator discussion"}

    if action == "memory":
        # Would call ingester_ingest in real implementation
        return {"status": "stored", "message": "Stored to memory"}

    if action.startswith("spawn:"):
        spawn_type = action.split(":")[1]
        # Would call scaffold in real implementation
        return {"status": "spawned", "type": spawn_type, "message": f"Would spawn {spawn_type}"}

    return {"status": "unknown", "message": f"Unknown action: {action}"}


def mark_triaged(work_id: str, session: str) -> str:
    """Mark an observation file as triaged.

    Adds triage_status: triaged and triage_session fields to frontmatter.

    Args:
        work_id: The work item ID (e.g., E2-303)
        session: Session number that performed triage

    Returns:
        Status message (triaged, already_triaged, not_found)
    """
    obs_path = _find_observations_file(work_id)

    if not obs_path:
        return "not_found"

    content = obs_path.read_text(encoding="utf-8")

    # Check if already triaged
    if "triage_status: triaged" in content:
        return "already_triaged"

    # Add triage fields after captured_session line
    new_content = re.sub(
        r"(captured_session: '[^']*')\n",
        rf"\1\ntriage_status: triaged\ntriage_session: '{session}'\n",
        content
    )

    # If no captured_session found, add after work_id
    if new_content == content:
        new_content = re.sub(
            r"(work_id: '[^']*')\n",
            rf"\1\ntriage_status: triaged\ntriage_session: '{session}'\n",
            content
        )

    obs_path.write_text(new_content, encoding="utf-8")
    return "triaged"


# =============================================================================
# THRESHOLD FUNCTIONS (E2-224, E2-222)
# =============================================================================

# Default threshold - used as fallback when config not present
DEFAULT_OBSERVATION_THRESHOLD = 10


def load_threshold_config() -> dict:
    """Load threshold configuration from unified config (E2-246).

    Returns:
        Parsed config dict, or empty dict if config missing.
    """
    try:
        from config import ConfigLoader
        return {"thresholds": ConfigLoader.get().thresholds}
    except Exception:
        pass  # Fall through to return empty dict
    return {}


def get_observation_threshold() -> int:
    """Get observation pending threshold from config or default.

    Reads from unified config (.claude/haios/config/haios.yaml) if present,
    otherwise returns DEFAULT_OBSERVATION_THRESHOLD.

    Returns:
        Threshold value (default: 10)
    """
    config = load_threshold_config()
    try:
        return config.get("thresholds", {}).get("observation_pending", {}).get("max_count", DEFAULT_OBSERVATION_THRESHOLD)
    except (KeyError, TypeError, AttributeError):
        return DEFAULT_OBSERVATION_THRESHOLD


def get_pending_observation_count(base_path: Optional[Path] = None) -> int:
    """Count total pending observations across all archived work items.

    Args:
        base_path: Override project root (for testing)

    Returns:
        Total count of pending observations across all archived items.
    """
    pending_items = scan_archived_observations(base_path)
    return sum(len(item["observations"]) for item in pending_items)


def should_trigger_triage(count: int, threshold: int = DEFAULT_OBSERVATION_THRESHOLD) -> bool:
    """Check if pending observation count exceeds threshold.

    Uses strict greater-than (not >=) to avoid triggering at exactly threshold.

    Args:
        count: Current pending observation count
        threshold: Threshold to trigger triage (default: 10)

    Returns:
        True if count > threshold, False otherwise.
    """
    return count > threshold


# =============================================================================
# RETRO-TRIAGE FUNCTIONS (WORK-143)
# =============================================================================
# Query retro-cycle outputs from memory by content patterns.
# ingester_ingest stores retro outputs as:
#   - type=Directive, content="KEEP-N: ..." / "STOP-N: ..." / "START-N: ..."
#   - type=Critique, content="BUG (confidence): ..." / "FEATURE (confidence): ..."
# source_adr does NOT contain provenance tags (A1 critique finding).
# Follow-up: fix producer pipeline for proper provenance tags.

import json as _json


def _ensure_parsed(result) -> dict:
    """Ensure db_query result is a parsed dict, not a JSON string (A7)."""
    if isinstance(result, str):
        try:
            return _json.loads(result)
        except (ValueError, TypeError):
            return {"error": result}
    return result


def _rows_to_dicts(rows: list, columns: list) -> list[dict]:
    """Convert DB rows + columns into list of dicts."""
    return [dict(zip(columns, row)) for row in rows]


def query_retro_kss(db_query_fn=None) -> list[dict]:
    """Query memory for K/S/S directive entries (retro-cycle DERIVE output).

    Queries concepts table for type=Directive with KEEP-/STOP-/START- content
    prefixes, which is how ingester_ingest stores retro-kss output after
    LLM extraction.

    Args:
        db_query_fn: Callable(sql) -> {columns, rows} or JSON string.
                     If None, returns empty list.

    Returns:
        List of dicts with id, content keys.
    """
    if db_query_fn is None:
        return []
    result = _ensure_parsed(db_query_fn(
        "SELECT id, content FROM concepts WHERE type = 'Directive' "
        "AND (content LIKE 'KEEP-%' OR content LIKE 'STOP-%' OR content LIKE 'START-%') "
        "ORDER BY id"
    ))
    if "error" in result:
        return []
    return _rows_to_dicts(result["rows"], result["columns"])


def query_retro_bugs(db_query_fn=None) -> list[dict]:
    """Query memory for bug candidate entries (retro-cycle EXTRACT output).

    Queries concepts table for type=Critique with BUG prefix in content.

    Args:
        db_query_fn: Callable(sql) -> {columns, rows} or JSON string.

    Returns:
        List of dicts with id, content keys.
    """
    if db_query_fn is None:
        return []
    result = _ensure_parsed(db_query_fn(
        "SELECT id, content FROM concepts WHERE type = 'Critique' "
        "AND content LIKE 'BUG %' ORDER BY id DESC"
    ))
    if "error" in result:
        return []
    return _rows_to_dicts(result["rows"], result["columns"])


def query_retro_features(db_query_fn=None) -> list[dict]:
    """Query memory for feature candidate entries (retro-cycle EXTRACT output).

    Queries concepts table for type=Critique with FEATURE prefix in content.

    Args:
        db_query_fn: Callable(sql) -> {columns, rows} or JSON string.

    Returns:
        List of dicts with id, content keys.
    """
    if db_query_fn is None:
        return []
    result = _ensure_parsed(db_query_fn(
        "SELECT id, content FROM concepts WHERE type = 'Critique' "
        "AND content LIKE 'FEATURE %' ORDER BY id DESC"
    ))
    if "error" in result:
        return []
    return _rows_to_dicts(result["rows"], result["columns"])


def _normalize_directive(text: str) -> str:
    """Normalize a K/S/S directive for frequency comparison."""
    return re.sub(r'\s+', ' ', text.strip().lower())


def _parse_kss_content(content: str) -> tuple:
    """Parse a KSS directive content like 'KEEP-1: TDD RED-GREEN...' into (category, directive).

    Handles formats:
      - 'KEEP-1: directive text'  (numbered, from retro-cycle)
      - 'Keep: directive text'     (unnumbered)
      - '- KEEP-1: directive text' (list-prefixed, A3 fix)

    Returns:
        (category, directive) tuple where category is 'keep'/'stop'/'start',
        or ('', '') if not parseable.
    """
    line = content.strip()
    # Strip list prefix (A3)
    if line.startswith("- "):
        line = line[2:]
    # Match KEEP-N: or Keep: patterns
    match = re.match(r'^(KEEP|STOP|START)(?:-\d+)?:\s*(.+)', line, re.IGNORECASE)
    if match:
        return (match.group(1).lower(), match.group(2).strip())
    return ('', '')


def aggregate_kss_frequency(kss_entries: list) -> dict:
    """Aggregate K/S/S directives by frequency across entries.

    Each entry is a DB row with 'content' like 'KEEP-1: TDD RED-GREEN'.
    Counts frequency of convergent directives (normalized for comparison),
    returns ranked by count descending.

    Args:
        kss_entries: List from query_retro_kss(). Each has 'id' and 'content'.

    Returns:
        {"keep": [...], "stop": [...], "start": [...]}
        Each item: {"directive": str, "count": int, "memory_ids": list[int]}
    """
    buckets = {"keep": {}, "stop": {}, "start": {}}

    for entry in kss_entries:
        content = entry.get("content", "")
        memory_id = entry.get("id")

        category, directive = _parse_kss_content(content)
        if not category:
            continue

        key = _normalize_directive(directive)
        if key not in buckets[category]:
            buckets[category][key] = {
                "directive": directive,  # preserve first occurrence casing
                "count": 0,
                "memory_ids": []
            }
        buckets[category][key]["count"] += 1
        if memory_id is not None:
            buckets[category][key]["memory_ids"].append(memory_id)

    # Sort each bucket by count descending
    result = {}
    for category, items in buckets.items():
        sorted_items = sorted(items.values(), key=lambda x: x["count"], reverse=True)
        result[category] = sorted_items

    return result


def _parse_bug_feature_content(content: str) -> dict:
    """Parse 'BUG (confidence): description' or 'FEATURE (confidence): description'.

    Real examples from memory:
      - 'BUG (medium): spawn-work-ceremony missing stub: true in frontmatter.'
      - 'FEATURE (high): WORK-143 -- triage consumer update needed.'

    Returns:
        {"type": "bug"|"feature", "confidence": str, "description": str}
        or empty dict if not parseable.
    """
    match = re.match(r'^(BUG|FEATURE)\s*\((\w+)\):\s*(.+)', content.strip(), re.IGNORECASE)
    if match:
        return {
            "type": match.group(1).lower(),
            "confidence": match.group(2).lower(),
            "description": match.group(3).strip()
        }
    return {}


def surface_bug_candidates(bug_entries: list) -> list:
    """Parse bug entries into structured candidates sorted by confidence.

    Args:
        bug_entries: List from query_retro_bugs(). Each has 'id' and 'content'.

    Returns:
        List of dicts with type, confidence, description, memory_id.
        Sorted by confidence (high > medium > low).
    """
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    bugs = []
    for entry in bug_entries:
        parsed = _parse_bug_feature_content(entry.get("content", ""))
        if parsed.get("type") == "bug":
            parsed["memory_id"] = entry.get("id")
            bugs.append(parsed)
    bugs.sort(key=lambda x: confidence_order.get(x.get("confidence", "low"), 3))
    return bugs


def surface_feature_candidates(feature_entries: list) -> list:
    """Parse feature entries into structured candidates sorted by confidence.

    Args:
        feature_entries: List from query_retro_features(). Each has 'id' and 'content'.

    Returns:
        List of dicts with type, confidence, description, memory_id.
        Sorted by confidence (high > medium > low).
    """
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    features = []
    for entry in feature_entries:
        parsed = _parse_bug_feature_content(entry.get("content", ""))
        if parsed.get("type") == "feature":
            parsed["memory_id"] = entry.get("id")
            features.append(parsed)
    features.sort(key=lambda x: confidence_order.get(x.get("confidence", "low"), 3))
    return features


# CLI entry point for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python observations.py <command> [args]")
        print("Commands:")
        print("  validate <work_id>  - Validate observations gate")
        print("  scaffold <work_id>  - Create observations.md")
        print("  scan                - Scan for uncaptured observations (active)")
        print("  triage              - Scan for untriaged observations (archive)")
        print("  retro-kss           - Query and aggregate K/S/S directives from memory")
        print("  retro-bugs          - Query and surface bug candidates from memory")
        print("  retro-features      - Query and surface feature candidates from memory")
        sys.exit(1)

    command = sys.argv[1]

    # Shared DB query helper for retro-* CLI commands (WORK-153: deduplicated)
    def _db_query(sql):
        try:
            from haios_etl.database import DatabaseManager
            db = DatabaseManager()
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return {"columns": columns, "rows": [list(r) for r in rows]}
        except Exception as e:
            return {"error": str(e)}

    if command == "validate" and len(sys.argv) >= 3:
        result = validate_observations(sys.argv[2])
        print(f"Valid: {result['valid']}")
        print(f"Message: {result['message']}")
        sys.exit(0 if result["valid"] else 1)

    elif command == "scaffold" and len(sys.argv) >= 3:
        result = scaffold_observations(sys.argv[2])
        if result:
            print(f"Created: {result}")
        else:
            print("Failed: Work directory not found")
            sys.exit(1)

    elif command == "scan":
        results = scan_uncaptured_observations()
        if not results:
            print("All observations captured.")
        else:
            for item in results:
                print(f"{item['work_id']}: {item['status']} - {item['message']}")

    elif command == "triage":
        results = scan_archived_observations()
        if not results:
            print("No untriaged observations found.")
        else:
            print(f"Found {len(results)} archived items with untriaged observations:")
            for item in results:
                print(f"  {item['work_id']}: {len(item['observations'])} observations")
                for obs in item['observations']:
                    print(f"    - [{obs['section']}] {obs['text'][:60]}...")

    elif command == "retro-kss":
        entries = query_retro_kss(db_query_fn=_db_query)
        if not entries:
            print("No K/S/S directives found in memory.")
        else:
            agg = aggregate_kss_frequency(entries)
            for cat in ("keep", "stop", "start"):
                if agg[cat]:
                    print(f"\n{cat.upper()}:")
                    for item in agg[cat]:
                        print(f"  [{item['count']}x] {item['directive']}")

    elif command == "retro-bugs":
        entries = query_retro_bugs(db_query_fn=_db_query)
        bugs = surface_bug_candidates(entries)
        if not bugs:
            print("No bug candidates found in memory.")
        else:
            print(f"Bug candidates ({len(bugs)}):")
            for bug in bugs:
                print(f"  [{bug['confidence']}] {bug['description']}")

    elif command == "retro-features":
        entries = query_retro_features(db_query_fn=_db_query)
        features = surface_feature_candidates(entries)
        if not features:
            print("No feature candidates found in memory.")
        else:
            print(f"Feature candidates ({len(features)}):")
            for feat in features:
                print(f"  [{feat['confidence']}] {feat['description']}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
