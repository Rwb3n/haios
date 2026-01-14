# generated: 2025-11-26
# System Auto: last updated on: 2025-11-26 20:31:28
"""
Batch embedding generation for HAIOS Cognitive Memory System.

Generates embeddings for all artifacts that don't have them yet.
Uses Gemini text-embedding-004 model via the ExtractionManager.

Usage:
    python scripts/generate_embeddings.py [--limit N] [--dry-run]

Options:
    --limit N    Process at most N artifacts (default: all)
    --dry-run    Show what would be processed without making API calls
"""

import sys
import os
import time
import argparse
import logging

# Add project root to path
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
from haios_etl.database import DatabaseManager
from haios_etl.extraction import ExtractionManager, ExtractionError
from haios_etl.processing import read_file_safely

# Load environment variables
load_dotenv()

# Configuration
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSIONS = 768
RATE_LIMIT_DELAY = 0.1  # seconds between requests (10 req/sec)
BATCH_LOG_INTERVAL = 10  # Log progress every N artifacts


def get_artifacts_without_embeddings(db: DatabaseManager, limit: int = None):
    """Get artifacts that don't have embeddings yet."""
    conn = db.get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT a.id, a.file_path
        FROM artifacts a
        LEFT JOIN embeddings e ON a.id = e.artifact_id
        WHERE e.id IS NULL
        ORDER BY a.id
    """

    if limit:
        sql += f" LIMIT {limit}"

    cursor.execute(sql)
    return cursor.fetchall()


def truncate_for_embedding(text: str, max_chars: int = 25000) -> str:
    """
    Truncate text to fit within embedding model limits.
    text-embedding-004 has a token limit; ~25k chars is safe.
    """
    if len(text) <= max_chars:
        return text

    # Truncate and add indicator
    return text[:max_chars] + "\n\n[Content truncated for embedding]"


def generate_embeddings(
    db_path: str = "haios_memory.db",
    limit: int = None,
    dry_run: bool = False
):
    """Generate embeddings for artifacts without them."""

    # Setup
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in environment.")
        sys.exit(1)

    db = DatabaseManager(db_path)
    extractor = ExtractionManager(api_key=api_key)

    # Get artifacts to process
    artifacts = get_artifacts_without_embeddings(db, limit)
    total = len(artifacts)

    if total == 0:
        print("All artifacts already have embeddings. Nothing to do.")
        return

    print(f"Found {total} artifacts without embeddings.")

    if dry_run:
        print("\n[DRY RUN] Would process:")
        for artifact_id, file_path in artifacts[:10]:
            print(f"  - {artifact_id}: {file_path}")
        if total > 10:
            print(f"  ... and {total - 10} more")
        return

    # Process
    print(f"\nGenerating embeddings (rate: {1/RATE_LIMIT_DELAY:.1f} req/sec)...")
    print("-" * 60)

    success_count = 0
    error_count = 0
    skip_count = 0
    start_time = time.time()

    for i, (artifact_id, file_path) in enumerate(artifacts, 1):
        try:
            # Read file content
            content = read_file_safely(file_path)

            if content is None:
                logging.warning(f"Skipping {artifact_id}: Could not read file")
                skip_count += 1
                continue

            if len(content.strip()) < 50:
                logging.warning(f"Skipping {artifact_id}: Content too short")
                skip_count += 1
                continue

            # Truncate if needed
            content = truncate_for_embedding(content)

            # Generate embedding
            embedding = extractor.embed_content(content)

            # Store in database
            db.insert_embedding(
                artifact_id=artifact_id,
                vector=embedding,
                model=EMBEDDING_MODEL,
                dimensions=len(embedding)
            )

            success_count += 1

            # Progress logging
            if i % BATCH_LOG_INTERVAL == 0 or i == total:
                elapsed = time.time() - start_time
                rate = success_count / elapsed if elapsed > 0 else 0
                print(f"  [{i}/{total}] {success_count} success, {error_count} errors, {skip_count} skipped ({rate:.1f}/sec)")

            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)

        except ExtractionError as e:
            logging.error(f"Embedding failed for {artifact_id}: {e}")
            error_count += 1
            # Continue with next artifact

        except Exception as e:
            logging.error(f"Unexpected error for {artifact_id}: {e}")
            error_count += 1

    # Summary
    elapsed = time.time() - start_time
    print("-" * 60)
    print(f"COMPLETE in {elapsed:.1f}s")
    print(f"  Success: {success_count}")
    print(f"  Errors:  {error_count}")
    print(f"  Skipped: {skip_count}")
    print(f"  Rate:    {success_count/elapsed:.2f} embeddings/sec")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate embeddings for HAIOS artifacts")
    parser.add_argument("--limit", type=int, help="Process at most N artifacts")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s"
    )

    generate_embeddings(
        limit=args.limit,
        dry_run=args.dry_run
    )
