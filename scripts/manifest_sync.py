# generated: 2026-02-16
# System Auto: last updated on: 2026-02-16
"""Manifest auto-sync: regenerate components section from disk (WORK-135).

Scans .claude/skills/, .claude/commands/, .claude/agents/ and compares
against .claude/haios/manifest.yaml components. Adds missing entries,
removes stale entries, sorts by id.

Usage:
    python scripts/manifest_sync.py              # sync manifest
    python scripts/manifest_sync.py --dry-run    # show diff without writing

Note: Hooks are excluded from sync — they have a fixed structure
(4 event handlers) with a different format (event+handler, not id+source).
"""

from pathlib import Path

from ruamel.yaml import YAML


def compute_manifest_diff(
    manifest: dict,
    *,
    skills_dir: Path,
    commands_dir: Path,
    agents_dir: Path,
) -> dict:
    """Compare disk state to manifest components.

    Args:
        manifest: Parsed manifest.yaml dict.
        skills_dir: Path to skills directory (.claude/skills/).
        commands_dir: Path to commands directory (.claude/commands/).
        agents_dir: Path to agents directory (.claude/agents/).

    Returns:
        Dict with keys 'skills', 'commands', 'agents', each containing
        'missing_from_manifest' (sorted list) and 'extra_in_manifest' (sorted list).
    """
    result = {}

    # Skills: directories containing SKILL.md
    disk_skills = {d.parent.name for d in skills_dir.glob("*/SKILL.md")}
    manifest_skills = {
        s["id"] for s in manifest.get("components", {}).get("skills", [])
    }
    result["skills"] = {
        "missing_from_manifest": sorted(disk_skills - manifest_skills),
        "extra_in_manifest": sorted(manifest_skills - disk_skills),
    }

    # Commands: .md files excluding README.md
    disk_cmds = {
        f.stem for f in commands_dir.glob("*.md") if f.name != "README.md"
    }
    manifest_cmds = {
        c["id"] for c in manifest.get("components", {}).get("commands", [])
    }
    result["commands"] = {
        "missing_from_manifest": sorted(disk_cmds - manifest_cmds),
        "extra_in_manifest": sorted(manifest_cmds - disk_cmds),
    }

    # Agents: .md files excluding README.md
    disk_agents = {
        f.stem for f in agents_dir.glob("*.md") if f.name != "README.md"
    }
    manifest_agents = {
        a["id"] for a in manifest.get("components", {}).get("agents", [])
    }
    result["agents"] = {
        "missing_from_manifest": sorted(disk_agents - manifest_agents),
        "extra_in_manifest": sorted(manifest_agents - disk_agents),
    }

    return result


def sync_manifest(manifest_path: Path, *, dry_run: bool = False) -> dict:
    """Sync manifest.yaml components with disk state.

    Reads the manifest, computes diff against disk, then adds missing entries
    and removes stale entries. Sorts each component section by id.

    Args:
        manifest_path: Path to manifest.yaml (expected at .claude/haios/manifest.yaml).
        dry_run: If True, compute and return diff but don't write changes.

    Returns:
        The diff that was (or would be) applied.
    """
    yml = YAML()
    yml.preserve_quotes = True
    with open(manifest_path) as f:
        manifest = yml.load(f)

    # Resolve component dirs: manifest is at .claude/haios/manifest.yaml
    # so parent.parent gives .claude/
    claude_dir = manifest_path.parent.parent
    diff = compute_manifest_diff(
        manifest,
        skills_dir=claude_dir / "skills",
        commands_dir=claude_dir / "commands",
        agents_dir=claude_dir / "agents",
    )

    has_changes = any(
        diff[ct]["missing_from_manifest"] or diff[ct]["extra_in_manifest"]
        for ct in ["skills", "commands", "agents"]
    )

    if dry_run or not has_changes:
        return diff

    # Add missing items
    for skill_id in diff["skills"]["missing_from_manifest"]:
        manifest["components"]["skills"].append(
            {
                "id": skill_id,
                "source": f"skills/{skill_id}/",
                "category": "utility",  # safe default, operator can refine
            }
        )
    for cmd_id in diff["commands"]["missing_from_manifest"]:
        manifest["components"]["commands"].append(
            {"id": cmd_id, "source": f"commands/{cmd_id}/"}
        )
    for agent_id in diff["agents"]["missing_from_manifest"]:
        manifest["components"]["agents"].append(
            {
                "id": agent_id,
                "source": f"agents/{agent_id}/",
                "required": False,
            }
        )

    # Remove extra items (deleted from disk but still in manifest)
    for component_type in ["skills", "commands", "agents"]:
        extra = set(diff[component_type]["extra_in_manifest"])
        if extra:
            manifest["components"][component_type] = [
                item
                for item in manifest["components"][component_type]
                if item["id"] not in extra
            ]

    # Sort each section by id for stable, diff-friendly output
    for component_type in ["skills", "commands", "agents"]:
        manifest["components"][component_type].sort(key=lambda x: x["id"])

    # Note: Header comment counts (e.g. "# Skills (34 total)") are NOT updated.
    # They are unreliable metadata — the manifest entries ARE the truth.

    with open(manifest_path, "w") as f:
        yml.dump(manifest, f)

    return diff


if __name__ == "__main__":
    import sys

    dry_run = "--dry-run" in sys.argv
    manifest_path = Path(".claude/haios/manifest.yaml")

    if not manifest_path.exists():
        print(f"Error: {manifest_path} not found. Run from repo root.", file=sys.stderr)
        sys.exit(1)

    diff = sync_manifest(manifest_path, dry_run=dry_run)
    has_changes = any(
        diff[ct]["missing_from_manifest"] or diff[ct]["extra_in_manifest"]
        for ct in ["skills", "commands", "agents"]
    )

    if not has_changes:
        print("Manifest is in sync.")
    else:
        for ct in ["skills", "commands", "agents"]:
            for item in diff[ct]["missing_from_manifest"]:
                action = "(would add)" if dry_run else "(added)"
                print(f"  + {ct}: {item} {action}")
            for item in diff[ct]["extra_in_manifest"]:
                action = "(would remove)" if dry_run else "(removed)"
                print(f"  - {ct}: {item} {action}")
