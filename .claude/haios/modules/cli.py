# generated: 2026-01-03
# System Auto: last updated on: 2026-01-29T21:29:01
"""
HAIOS Modules CLI Entry Point

Simple CLI wrapper for invoking Chariot modules from justfile recipes.
This is the integration point between just recipes and the module layer.

Usage:
    python .claude/haios/modules/cli.py transition E2-250 implement
    python .claude/haios/modules/cli.py archive E2-250
    python .claude/haios/modules/cli.py get-ready
"""
import sys
from pathlib import Path
from typing import Optional

# Ensure the modules directory is importable
_modules_path = Path(__file__).parent
if str(_modules_path) not in sys.path:
    sys.path.insert(0, str(_modules_path))

# WORK-006: Also add lib path for modules that import from lib
_lib_path = Path(__file__).parent.parent / "lib"  # .claude/haios/lib (sibling to modules/)
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))

from governance_layer import GovernanceLayer
from work_engine import WorkEngine, WorkNotFoundError, InvalidTransitionError


def get_engine() -> WorkEngine:
    """Create WorkEngine with GovernanceLayer."""
    governance = GovernanceLayer()
    return WorkEngine(governance=governance)


def cmd_transition(work_id: str, to_node: str) -> int:
    """Transition work item to new node."""
    engine = get_engine()
    try:
        work = engine.transition(work_id, to_node)
        print(f"Moved {work_id} to node: {to_node}")
        return 0
    except WorkNotFoundError:
        print(f"Not found: {work_id}")
        return 1
    except InvalidTransitionError as e:
        print(f"Invalid transition: {e}")
        return 1


def cmd_close(work_id: str) -> int:
    """Close work item (set complete, closed date). Per ADR-041: stays in active/."""
    engine = get_engine()
    try:
        path = engine.close(work_id)
        print(f"Closed: {work_id} -> {path}")
        return 0
    except WorkNotFoundError:
        print(f"Not found: {work_id}")
        return 1


def cmd_archive(work_id: str) -> int:
    """Archive work item (just move, no status change)."""
    engine = get_engine()
    try:
        path = engine.archive(work_id)
        print(f"Archived: {work_id} -> {path}")
        return 0
    except WorkNotFoundError:
        print(f"Not found: {work_id}")
        return 1


def cmd_get_ready() -> int:
    """List ready (unblocked) work items."""
    engine = get_engine()
    ready = engine.get_ready()
    for work in ready:
        print(f"  {work.id}: {work.title}")
    if not ready:
        print("No unblocked work items")
    return 0


def cmd_get_work(work_id: str) -> int:
    """Get work item details."""
    engine = get_engine()
    work = engine.get_work(work_id)
    if work:
        print(f"ID: {work.id}")
        print(f"Title: {work.title}")
        print(f"Status: {work.status}")
        print(f"Node: {work.current_node}")
        print(f"Blocked by: {work.blocked_by}")
        return 0
    else:
        print(f"Not found: {work_id}")
        return 1


def cmd_link(work_id: str, doc_type: str, doc_path: str) -> int:
    """Link a document to a work item."""
    engine = get_engine()
    try:
        engine.add_document_link(work_id, doc_type, doc_path)
        print(f"Linked {doc_type} to {work_id}: {doc_path}")
        return 0
    except WorkNotFoundError:
        print(f"Not found: {work_id}")
        return 1


def cmd_link_spawn(parent: str, milestone: str, ids: list) -> int:
    """Link spawned items to parent with milestone."""
    engine = get_engine()
    result = engine.link_spawned_items(parent, ids, milestone if milestone != "none" else None)
    print(f"Updated: {result['updated']}")
    if result['failed']:
        print(f"Failed: {result['failed']}")
    return 0 if not result['failed'] else 1


# =============================================================================
# E2-251: Cascade, Spawn Tree, Backfill Commands
# =============================================================================


def cmd_cascade(work_id: str, new_status: str) -> int:
    """Run cascade for completed item."""
    engine = get_engine()
    result = engine.cascade(work_id, new_status)
    print(result.message)
    return 0


def cmd_spawn_tree(root_id: str) -> int:
    """Build and display spawn tree."""
    engine = get_engine()
    tree = engine.spawn_tree(root_id)
    print(WorkEngine.format_tree(tree, use_ascii=True))
    return 0


def cmd_backfill(work_id: str) -> int:
    """Backfill work file from backlog."""
    engine = get_engine()
    success = engine.backfill(work_id)
    print("Backfilled" if success else "Not found or no changes")
    return 0


def cmd_backfill_all(force: bool = False) -> int:
    """Backfill all active work items."""
    engine = get_engine()
    results = engine.backfill_all(force=force)
    print(f"Success: {len(results['success'])} | Not found: {len(results['not_found'])} | Already filled: {len(results['no_changes'])}")
    return 0


# =============================================================================
# E2-253: MemoryBridge Commands
# =============================================================================


def cmd_memory_query(query: str, mode: str = "semantic") -> int:
    """Query memory using MemoryBridge."""
    from memory_bridge import MemoryBridge

    bridge = MemoryBridge(enable_rewriting=True)
    result = bridge.query(query, mode=mode)

    if result.concepts:
        print(f"Found {len(result.concepts)} concepts:")
        for c in result.concepts[:5]:  # Show top 5
            content = str(c.get("content", ""))[:80]
            score = c.get("score", 0)
            print(f"  [{score:.2f}] {content}...")
    else:
        print("No results found")

    if result.reasoning:
        strategy = result.reasoning.get("strategy_used", "unknown")
        learned_from = result.reasoning.get("learned_from", 0)
        print(f"\nStrategy: {strategy} | Learned from: {learned_from} traces")

    return 0


# =============================================================================
# E2-254: ContextLoader Commands
# =============================================================================


def cmd_context_load(project_root: Path = None, role: str = "main") -> int:
    """
    Load context based on role and output loaded content.

    WORK-009: Outputs identity content for coldstart injection.
    Previously output char counts only.

    Args:
        project_root: Project root path (default: auto-detect)
        role: Role defining which loaders to use (default: "main")

    Returns:
        0 on success
    """
    import sys
    import io
    from context_loader import ContextLoader

    # WORK-009: Ensure UTF-8 output on Windows (fix Unicode arrows in identity content)
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    loader = ContextLoader(project_root=project_root)
    ctx = loader.load_context(role=role)

    # Output loaded_context from role-based loaders (WORK-009)
    for loader_name, content in ctx.loaded_context.items():
        if content:
            print(content)

    # Session info
    print(f"\n[SESSION]")
    print(f"Number: {ctx.session_number}")
    print(f"Prior: {ctx.prior_session or 'None'}")

    # Ready work summary
    if ctx.ready_work:
        print(f"\n[READY WORK]")
        for work_id in ctx.ready_work[:5]:
            print(f"- {work_id}")

    return 0


# =============================================================================
# WORK-011: Coldstart Orchestrator Command
# =============================================================================


def cmd_coldstart() -> int:
    """
    Run coldstart orchestrator - unified context loading with breathing room.

    WORK-011 (CH-007): Wires IdentityLoader, SessionLoader, WorkLoader into
    unified coldstart with [BREATHE] markers between phases.

    Returns:
        0 on success
    """
    import sys
    import io
    from coldstart_orchestrator import ColdstartOrchestrator

    # Ensure UTF-8 output on Windows (same pattern as cmd_context_load)
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )

    orch = ColdstartOrchestrator()
    print(orch.run())
    return 0


# =============================================================================
# E2-255: CycleRunner Commands
# =============================================================================


def cmd_cycle_phases(cycle_id: str) -> int:
    """Get phases for a cycle."""
    from cycle_runner import CycleRunner

    runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
    phases = runner.get_cycle_phases(cycle_id)

    if phases:
        print(phases)
    else:
        print(f"Unknown cycle: {cycle_id}")
        return 1
    return 0


# =============================================================================
# WORK-015: RequirementExtractor Commands
# =============================================================================


def cmd_corpus_list(corpus_config: str) -> int:
    """List files discovered by a corpus configuration.

    Args:
        corpus_config: Path to corpus YAML configuration file.

    Returns:
        0 on success, 1 on error.
    """
    from corpus_loader import CorpusLoader

    try:
        loader = CorpusLoader(Path(corpus_config))
        files = loader.discover()

        print(f"Corpus: {loader._parsed.name}")
        print(f"Files discovered: {len(files)}")
        print("---")
        for f in sorted(files):
            print(f"  {f}")
        return 0
    except FileNotFoundError:
        print(f"Config not found: {corpus_config}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_plan(requirements_path: Optional[str], corpus_config: Optional[str] = None) -> int:
    """Generate a work plan from requirements.

    Args:
        requirements_path: Path to requirements file or corpus directory.
        corpus_config: Optional path to corpus YAML configuration file.

    Returns:
        0 on success, 1 on error.
    """
    import json
    from requirement_extractor import RequirementExtractor
    from planner_agent import PlannerAgent

    try:
        # Extract requirements first
        if corpus_config:
            from corpus_loader import CorpusLoader
            loader = CorpusLoader(Path(corpus_config))
            extractor = RequirementExtractor(loader)
        elif requirements_path:
            extractor = RequirementExtractor(Path(requirements_path))
        else:
            print("Error: Either requirements_path or corpus_config required")
            return 1

        requirement_set = extractor.extract()

        # Generate work plan
        planner = PlannerAgent(requirement_set)
        work_plan = planner.plan()

        # Output as JSON for pipeline consumption
        output = {
            "planner_version": work_plan.planner_version,
            "created_at": work_plan.created_at.isoformat(),
            "source_corpus": work_plan.source_requirements.source_corpus,
            "work_item_count": len(work_plan.work_items),
            "work_items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "type": item.type,
                    "requirement_refs": item.requirement_refs,
                    "dependencies": item.dependencies,
                    "estimated_effort": item.estimated_effort,
                    "priority": item.priority,
                }
                for item in work_plan.work_items
            ],
            "execution_order": work_plan.execution_order,
        }
        print(json.dumps(output, indent=2))
        return 0
    except FileNotFoundError as e:
        print(f"Path not found: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_extract_requirements(corpus_path: str, corpus_config: Optional[str] = None) -> int:
    """Extract requirements from a corpus of documents.

    Args:
        corpus_path: Path to corpus root directory or single file.
        corpus_config: Optional path to corpus YAML configuration file.

    Returns:
        0 on success, 1 on error.
    """
    import json
    from requirement_extractor import RequirementExtractor

    try:
        # Use CorpusLoader if config provided (WORK-031)
        if corpus_config:
            from corpus_loader import CorpusLoader
            loader = CorpusLoader(Path(corpus_config))
            extractor = RequirementExtractor(loader)
        else:
            extractor = RequirementExtractor(Path(corpus_path))
        result = extractor.extract()

        # Output as JSON for pipeline consumption
        output = {
            "source_corpus": result.source_corpus,
            "extracted_at": result.extracted_at.isoformat(),
            "extractor_version": result.extractor_version,
            "requirement_count": len(result.requirements),
            "requirements": [
                {
                    "id": r.id,
                    "description": r.description,
                    "strength": r.strength.value,
                    "type": r.type.value,
                    "confidence": r.confidence,
                    "source": {
                        "file": r.source.file,
                        "line_range": r.source.line_range,
                        "document_type": r.source.document_type.value
                    }
                }
                for r in result.requirements
            ]
        }
        print(json.dumps(output, indent=2))
        return 0
    except FileNotFoundError:
        print(f"Path not found: {corpus_path}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


# =============================================================================
# E2-252: Validate and Scaffold Commands
# =============================================================================


def cmd_validate(file_path: str) -> int:
    """Validate a template file."""
    layer = GovernanceLayer()
    result = layer.validate_template(file_path)
    if result["is_valid"]:
        print(f"Passed | Type: {result['template_type']} | Refs: {result['reference_count']}")
    else:
        print(f"Failed | {'; '.join(result['errors'])}")
    return 0 if result["is_valid"] else 1


def cmd_scaffold(template: str, backlog_id: str, title: str, output_path: str = None, variables: dict = None) -> int:
    """Scaffold a new document from template.

    E2-179: Added variables parameter for optional frontmatter args like spawned_by.
    """
    layer = GovernanceLayer()
    try:
        path = layer.scaffold_template(
            template=template,
            backlog_id=backlog_id,
            title=title,
            output_path=output_path,
            variables=variables,
        )
        print(f"Created: {path}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def main():
    if len(sys.argv) < 2:
        print("Usage: cli.py <command> [args...]")
        print("Commands: transition, close, archive, get-ready, get-work, link, link-spawn,")
        print("          cascade, spawn-tree, backfill, backfill-all, memory-query,")
        print("          validate, scaffold, context-load, coldstart, cycle-phases")
        return 1

    cmd = sys.argv[1]

    if cmd == "transition":
        if len(sys.argv) != 4:
            print("Usage: cli.py transition <work_id> <to_node>")
            return 1
        return cmd_transition(sys.argv[2], sys.argv[3])

    elif cmd == "close":
        if len(sys.argv) != 3:
            print("Usage: cli.py close <work_id>")
            return 1
        return cmd_close(sys.argv[2])

    elif cmd == "archive":
        if len(sys.argv) != 3:
            print("Usage: cli.py archive <work_id>")
            return 1
        return cmd_archive(sys.argv[2])

    elif cmd == "get-ready":
        return cmd_get_ready()

    elif cmd == "get-work":
        if len(sys.argv) != 3:
            print("Usage: cli.py get-work <work_id>")
            return 1
        return cmd_get_work(sys.argv[2])

    elif cmd == "link":
        if len(sys.argv) != 5:
            print("Usage: cli.py link <work_id> <doc_type> <doc_path>")
            return 1
        return cmd_link(sys.argv[2], sys.argv[3], sys.argv[4])

    elif cmd == "link-spawn":
        if len(sys.argv) < 5:
            print("Usage: cli.py link-spawn <parent> <milestone> <id1> [id2 ...]")
            return 1
        return cmd_link_spawn(sys.argv[2], sys.argv[3], sys.argv[4:])

    # E2-251: Cascade, Spawn Tree, Backfill
    elif cmd == "cascade":
        if len(sys.argv) != 4:
            print("Usage: cli.py cascade <work_id> <new_status>")
            return 1
        return cmd_cascade(sys.argv[2], sys.argv[3])

    elif cmd == "spawn-tree":
        if len(sys.argv) != 3:
            print("Usage: cli.py spawn-tree <root_id>")
            return 1
        return cmd_spawn_tree(sys.argv[2])

    elif cmd == "backfill":
        if len(sys.argv) != 3:
            print("Usage: cli.py backfill <work_id>")
            return 1
        return cmd_backfill(sys.argv[2])

    elif cmd == "backfill-all":
        force = "--force" in sys.argv
        return cmd_backfill_all(force=force)

    # E2-253: Memory Query
    elif cmd == "memory-query":
        if len(sys.argv) < 3:
            print("Usage: cli.py memory-query <query> [--mode <mode>]")
            return 1
        mode = "semantic"
        if "--mode" in sys.argv:
            mode_idx = sys.argv.index("--mode")
            mode = sys.argv[mode_idx + 1]
            query = " ".join([a for i, a in enumerate(sys.argv[2:], 2) if i != mode_idx and i != mode_idx + 1])
        else:
            query = " ".join(sys.argv[2:])
        return cmd_memory_query(query, mode)

    # E2-252: Validate, Scaffold
    elif cmd == "validate":
        if len(sys.argv) != 3:
            print("Usage: cli.py validate <file_path>")
            return 1
        return cmd_validate(sys.argv[2])

    elif cmd == "scaffold":
        # Handle optional flags (E2-179: added --spawned-by)
        output_path = None
        variables = {}
        args = list(sys.argv)  # Copy to avoid modifying original

        # Extract --output flag
        if "--output" in args:
            output_idx = args.index("--output")
            output_path = args[output_idx + 1]
            args = [a for i, a in enumerate(args) if i not in (output_idx, output_idx + 1)]

        # E2-179: Extract --spawned-by flag
        if "--spawned-by" in args:
            idx = args.index("--spawned-by")
            variables["SPAWNED_BY"] = args[idx + 1]
            args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]

        if len(args) < 5:
            print("Usage: cli.py scaffold <template> <backlog_id> <title> [--output <path>] [--spawned-by <id>]")
            return 1
        template = args[2]
        backlog_id = args[3]
        title = " ".join(args[4:])
        return cmd_scaffold(template, backlog_id, title, output_path, variables if variables else None)

    # E2-254: Context Load
    elif cmd == "context-load":
        return cmd_context_load()

    # WORK-011: Coldstart Orchestrator
    elif cmd == "coldstart":
        return cmd_coldstart()

    # E2-255: Cycle Phases
    elif cmd == "cycle-phases":
        if len(sys.argv) != 3:
            print("Usage: cli.py cycle-phases <cycle_id>")
            return 1
        return cmd_cycle_phases(sys.argv[2])

    # WORK-031: Corpus List
    elif cmd == "corpus-list":
        if len(sys.argv) != 3:
            print("Usage: cli.py corpus-list <corpus_config>")
            return 1
        return cmd_corpus_list(sys.argv[2])

    # WORK-015: Extract Requirements (with WORK-031 --corpus option)
    elif cmd == "extract-requirements":
        args = sys.argv[2:]
        corpus_config = None
        corpus_path = None

        # Parse --corpus flag
        if "--corpus" in args:
            idx = args.index("--corpus")
            corpus_config = args[idx + 1]
            args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]

        if args:
            corpus_path = args[0]

        if not corpus_path and not corpus_config:
            print("Usage: cli.py extract-requirements <corpus_path> [--corpus <config>]")
            return 1

        return cmd_extract_requirements(corpus_path or ".", corpus_config)

    # WORK-032: Plan from Requirements
    elif cmd == "plan":
        args = sys.argv[2:]
        corpus_config = None
        requirements_path = None

        # Parse --from-corpus flag (pattern-based, not line-number per A10)
        if "--from-corpus" in args:
            idx = args.index("--from-corpus")
            corpus_config = args[idx + 1]
            args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]

        if args:
            requirements_path = args[0]

        if not requirements_path and not corpus_config:
            print("Usage: cli.py plan <requirements_path>")
            print("       cli.py plan --from-corpus <corpus_config>")
            return 1

        return cmd_plan(requirements_path, corpus_config)

    else:
        print(f"Unknown command: {cmd}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
