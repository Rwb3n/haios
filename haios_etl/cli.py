# generated: 2025-11-29
# System Auto: last updated on: 2025-12-07 15:23:51
import argparse
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

from haios_etl.database import DatabaseManager
from haios_etl.extraction import ExtractionManager
from haios_etl.processing import BatchProcessor

# Configure logging for ETL pipeline visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Silence noisy loggers that might cause console overflow (Errno 22)
logging.getLogger("absl").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)

def get_db_path():
    # Default to a file in the current directory or project root
    return "haios_memory.db"

def cmd_status(args):
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    db = DatabaseManager(db_path)
    conn = db.get_connection()
    cursor = conn.cursor()
    
    
    print(f"Database: {db_path}")
    print()
    
    # Count artifacts
    cursor.execute("SELECT COUNT(*) FROM artifacts")
    artifacts_count = cursor.fetchone()[0]
    
    # Count entities
    cursor.execute("SELECT COUNT(*) FROM entities")
    entities_count = cursor.fetchone()[0]
    
    # Count concepts
    cursor.execute("SELECT COUNT(*) FROM concepts")
    concepts_count = cursor.fetchone()[0]
    
    print(f"Database Contents:")
    print(f"  Artifacts: {artifacts_count:,}")
    print(f"  Entities:  {entities_count:,}")
    print(f"  Concepts:  {concepts_count:,}")
    
    # Processing stats
    print("\nProcessing Log (All-Time):")
    cursor.execute("SELECT status, COUNT(*) FROM processing_log GROUP BY status")
    stats = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Show in consistent order with ASCII indicators
    print(f"  [SUCCESS] {stats.get('success', 0):,}")
    print(f"  [SKIPPED] {stats.get('skipped', 0):,}")
    print(f"  [ERROR]   {stats.get('error', 0):,}")
        
    # Show errors
    cursor.execute("SELECT file_path, error_message FROM processing_log WHERE status='error'")
    errors = cursor.fetchall()
    if errors:
        print("\nErrors:")
        for path, msg in errors:
            print(f"  {path}: {msg}")

def cmd_reset(args):
    db_path = get_db_path()
    if os.path.exists(db_path):
        confirm = input(f"Are you sure you want to delete {db_path}? (y/N): ")
        if confirm.lower() == 'y':
            os.remove(db_path)
            print("Database deleted.")
            # Re-initialize
            db = DatabaseManager(db_path)
            db.setup()
            print("Database re-initialized.")
        else:
            print("Cancelled.")
    else:
        print("Database does not exist. Initializing...")
        db = DatabaseManager(db_path)
        db.setup()
        print("Database initialized.")

def cmd_process(args):
    target_dir = Path(args.directory)
    if not target_dir.exists():
        print(f"Directory not found: {target_dir}")
        return

    # Load API Key
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment or .env file.")
        return

    db_path = get_db_path()
    db_manager = DatabaseManager(db_path)
    # Ensure DB exists
    if not os.path.exists(db_path):
        db_manager.setup()

    extraction_manager = ExtractionManager(api_key)
    processor = BatchProcessor(db_manager, extraction_manager)

    print(f"Processing directory: {target_dir}")
    
    count = 0
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # Filter for text files? Or try all?
            # Let's stick to .md and .txt for now to be safe, or just try everything.
            # The spec implies processing "content".
            if file.endswith(('.md', '.txt', '.py', '.json', '.yml', '.yaml')):
                # Logging now handled by processor (shows skip vs extract)
                processor.process_file(file_path)
                count += 1
    
    print(f"Batch complete. Processed {count} files.")

from haios_etl.refinement import RefinementManager
from haios_etl.synthesis import SynthesisManager
from haios_etl.agents.collaboration import Collaborator

def cmd_synthesis(args):
    """Handle synthesis pipeline commands."""
    db_path = get_db_path()

    # Load API Key for LLM calls
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if args.subcommand == "run":
        if not api_key:
            print("Error: GOOGLE_API_KEY not found. Required for synthesis.")
            return

        extractor = ExtractionManager(api_key)
        manager = SynthesisManager(db_path, extractor)

        print(f"Running synthesis pipeline...")
        print(f"  Limit: {args.limit}")
        print(f"  Dry Run: {args.dry_run}")
        print(f"  Concepts Only: {args.concepts_only}")
        print(f"  Traces Only: {args.traces_only}")
        print(f"  Skip Cross-Pollinate: {args.skip_cross}")
        print(f"  Cross Only: {args.cross_only}")
        print(f"  Max Bridges: {args.max_bridges}")
        print(f"  Concept Sample: {args.concept_sample} (0=ALL)")
        print(f"  Trace Sample: {args.trace_sample} (0=ALL)")
        print()

        results = manager.run_synthesis_pipeline(
            dry_run=args.dry_run,
            limit=args.limit,
            concepts_only=args.concepts_only,
            traces_only=args.traces_only,
            skip_cross_pollinate=args.skip_cross,
            cross_only=args.cross_only,
            max_bridges=args.max_bridges,
            concept_sample=args.concept_sample,
            trace_sample=args.trace_sample
        )

        print("\nResults:")
        print(f"  Concept Clusters: {results['concept_clusters']}")
        print(f"  Trace Clusters: {results['trace_clusters']}")
        print(f"  Synthesized: {results['synthesized']}")
        print(f"  Cross-pollination Pairs: {results['cross_pollination_pairs']}")
        print(f"  Bridge Insights: {results['bridge_insights']}")
        if results.get('skipped_existing', 0) > 0:
            print(f"  Skipped (existing): {results['skipped_existing']}")

        if results['errors']:
            print(f"\nErrors ({len(results['errors'])}):")
            for err in results['errors'][:5]:
                print(f"  - {err}")

    elif args.subcommand == "stats":
        manager = SynthesisManager(db_path)

        try:
            stats = manager.get_synthesis_stats()

            print("Synthesis Statistics:")
            print(f"  Total Concepts: {stats.total_concepts:,}")
            print(f"  Total Traces: {stats.total_traces:,}")
            print(f"  Synthesized Concepts: {stats.synthesized_concepts:,}")
            print(f"  Pending Clusters: {stats.pending_clusters:,}")
            print(f"  Completed Clusters: {stats.completed_clusters:,}")
            print(f"  Cross-pollination Links: {stats.cross_pollination_links:,}")
        except Exception as e:
            print(f"Error getting stats: {e}")
            print("(Migration 007 may not be applied yet)")

    elif args.subcommand == "inspect":
        manager = SynthesisManager(db_path)
        conn = manager.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT sc.id, sc.cluster_type, sc.member_count, sc.status,
                   c.content
            FROM synthesis_clusters sc
            LEFT JOIN concepts c ON sc.synthesized_concept_id = c.id
            WHERE sc.id = ?
        """, (args.cluster_id,))

        row = cursor.fetchone()
        if not row:
            print(f"Cluster {args.cluster_id} not found.")
            return

        print(f"Cluster {row[0]}:")
        print(f"  Type: {row[1]}")
        print(f"  Member Count: {row[2]}")
        print(f"  Status: {row[3]}")
        if row[4]:
            print(f"  Synthesized Content: {row[4][:200]}...")

        # Show members
        cursor.execute("""
            SELECT member_type, member_id
            FROM synthesis_cluster_members
            WHERE cluster_id = ?
        """, (args.cluster_id,))
        members = cursor.fetchall()
        if members:
            print(f"\n  Members ({len(members)}):")
            for mtype, mid in members[:10]:
                print(f"    - {mtype}:{mid}")
            if len(members) > 10:
                print(f"    ... and {len(members) - 10} more")

def cmd_refinement(args):
    db_path = get_db_path()
    manager = RefinementManager(db_path)
    
    if args.subcommand == "run":
        print(f"Running refinement (Limit: {args.limit}, Dry Run: {args.dry_run})...")
        memories = manager.scan_raw_memories(limit=args.limit)
        print(f"Found {len(memories)} raw memories.")
        
        for mem in memories:
            print(f"Refining Memory {mem['id']} (Type: {mem['type']})...")
            result = manager.refine_memory(mem['id'], mem['content'])
            
            print(f"  -> Type: {result.knowledge_type} (Conf: {result.confidence})")
            print(f"  -> Concepts: {result.concepts}")
            
            if not args.dry_run:
                manager.save_refinement(mem['id'], result)
                print("  -> Saved.")
            else:
                print("  -> [Dry Run] Not saved.")
                
    elif args.subcommand == "stats":
        conn = manager.db.get_connection()
        cursor = conn.cursor()
        
        print("Refinement Stats:")
        
        # Count by Knowledge Type
        cursor.execute("""
            SELECT value, COUNT(*) 
            FROM memory_metadata 
            WHERE key = 'knowledge_type' 
            GROUP BY value
        """)
        rows = cursor.fetchall()
        if rows:
            print("  Knowledge Types:")
            for r in rows:
                print(f"    {r[0]}: {r[1]}")
        else:
            print("  No refined memories found.")
            
        # Count by Status
        cursor.execute("""
            SELECT value, COUNT(*) 
            FROM memory_metadata 
            WHERE key = 'refinement_status' 
            GROUP BY value
        """)
        rows = cursor.fetchall()
        if rows:
            print("  Status:")
            for r in rows:
                print(f"    {r[0]}: {r[1]}")

def cmd_ingest(args):
    """Ingest files into memory using the Agent Ecosystem pipeline."""
    import glob

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment or .env file.")
        return

    db_path = get_db_path()
    db_manager = DatabaseManager(db_path)
    collaborator = Collaborator(db_manager=db_manager, api_key=api_key)

    # Collect files to process
    target = Path(args.path)
    if target.is_file():
        files = [str(target)]
    elif target.is_dir():
        pattern = "**/*.md" if args.recursive else "*.md"
        files = sorted(glob.glob(str(target / pattern), recursive=args.recursive))
        if args.include:
            for ext in args.include.split(","):
                ext = ext.strip()
                pattern = f"**/*{ext}" if args.recursive else f"*{ext}"
                files.extend(sorted(glob.glob(str(target / pattern), recursive=args.recursive)))
            files = sorted(set(files))
    else:
        print(f"Path not found: {target}")
        return

    if not files:
        print(f"No files found at: {target}")
        return

    print(f"=== BATCH INGESTION ===")
    print(f"Path: {target}")
    print(f"Files: {len(files)}")
    print(f"Dry Run: {args.dry_run}")
    print()

    success = 0
    fail = 0
    total_entities = 0
    total_concepts = 0

    for i, filepath in enumerate(files, 1):
        filename = os.path.basename(filepath)
        short = filename[:35] + "..." if len(filename) > 35 else filename

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Truncate if needed
            max_chars = args.max_chars or 4000
            content = content[:max_chars]

            if args.dry_run:
                print(f"[{i:02d}/{len(files)}] DRY {short}")
                success += 1
                continue

            result = collaborator.interpret_and_ingest(
                intent=f"Ingest {filename} as project documentation",
                content=content,
                source_path=filepath
            )

            if result.status.value == "success":
                success += 1
                e = len(result.result.get("entity_ids", []))
                c = len(result.result.get("concept_ids", []))
                total_entities += e
                total_concepts += c
                cls = result.result.get("classification", "?")[:3]
                print(f"[{i:02d}/{len(files)}] OK  {cls} E:{e:02d} C:{c:02d} {short}")
            else:
                fail += 1
                err = result.error.get("message", "unknown")[:40] if result.error else "unknown"
                print(f"[{i:02d}/{len(files)}] ERR {short}: {err}")

        except Exception as ex:
            fail += 1
            print(f"[{i:02d}/{len(files)}] EXC {short}: {str(ex)[:40]}")

    print()
    print(f"=== COMPLETE ===")
    print(f"Success: {success}/{len(files)}")
    print(f"Failed: {fail}")
    if not args.dry_run:
        print(f"Entities: {total_entities}")
        print(f"Concepts: {total_concepts}")


def main():
    parser = argparse.ArgumentParser(description="HAIOS ETL CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Status command
    subparsers.add_parser("status", help="Show system status")

    # Reset command
    subparsers.add_parser("reset", help="Reset the database")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process a directory")
    process_parser.add_argument("directory", help="Directory to process")

    # Ingest command (Agent Ecosystem pipeline)
    ingest_parser = subparsers.add_parser("ingest", help="Ingest files via Agent Ecosystem")
    ingest_parser.add_argument("path", help="File or directory to ingest")
    ingest_parser.add_argument("-r", "--recursive", action="store_true", help="Recursively process directories")
    ingest_parser.add_argument("--include", help="Additional extensions (comma-separated, e.g., '.txt,.json')")
    ingest_parser.add_argument("--max-chars", type=int, default=4000, help="Max chars per file (default: 4000)")
    ingest_parser.add_argument("--dry-run", action="store_true", help="Preview without ingesting")

    # Refinement command
    refine_parser = subparsers.add_parser("refinement", help="Knowledge Refinement Layer")
    refine_subs = refine_parser.add_subparsers(dest="subcommand", help="Refinement action")
    
    run_parser = refine_subs.add_parser("run", help="Run refinement loop")
    run_parser.add_argument("--limit", type=int, default=10, help="Max items to process")
    run_parser.add_argument("--dry-run", action="store_true", help="Do not save changes")
    
    refine_subs.add_parser("stats", help="Show refinement statistics")

    # Synthesis command
    synth_parser = subparsers.add_parser("synthesis", help="Memory Synthesis Pipeline")
    synth_subs = synth_parser.add_subparsers(dest="subcommand", help="Synthesis action")

    synth_run = synth_subs.add_parser("run", help="Run synthesis pipeline")
    synth_run.add_argument("--limit", type=int, default=1000, help="Max items to process")
    synth_run.add_argument("--dry-run", action="store_true", help="Preview without changes")
    synth_run.add_argument("--concepts-only", action="store_true", help="Only synthesize concepts")
    synth_run.add_argument("--traces-only", action="store_true", help="Only synthesize traces")
    synth_run.add_argument("--skip-cross", action="store_true", help="Skip cross-pollination")
    synth_run.add_argument("--cross-only", action="store_true", help="Run only cross-pollination (skip stages 1-3)")
    synth_run.add_argument("--max-bridges", type=int, default=100, help="Max bridge insights to create (default: 100)")
    synth_run.add_argument("--concept-sample", type=int, default=0, help="Max concepts to sample (0 = ALL)")
    synth_run.add_argument("--trace-sample", type=int, default=0, help="Max traces to sample (0 = ALL)")

    synth_subs.add_parser("stats", help="Show synthesis statistics")

    synth_inspect = synth_subs.add_parser("inspect", help="Inspect a synthesis cluster")
    synth_inspect.add_argument("cluster_id", type=int, help="Cluster ID to inspect")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status(args)
    elif args.command == "reset":
        cmd_reset(args)
    elif args.command == "process":
        cmd_process(args)
    elif args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "refinement":
        cmd_refinement(args)
    elif args.command == "synthesis":
        cmd_synthesis(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
