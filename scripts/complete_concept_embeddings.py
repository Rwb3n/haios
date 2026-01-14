# generated: 2025-12-05
# System Auto: last updated on: 2025-12-05 18:34:03
"""
Complete missing concept embeddings.

Generates embeddings for concepts that don't have them yet.
Uses a lower threshold (10 chars) to catch short but meaningful concepts.

Usage:
    python scripts/complete_concept_embeddings.py [--limit N] [--dry-run]
"""

import sys
import os
import time
import argparse
import logging

sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
from haios_etl.database import DatabaseManager
from haios_etl.extraction import ExtractionManager

load_dotenv()

EMBEDDING_MODEL = "text-embedding-004"
MIN_CONTENT_LENGTH = 10  # Skip obvious junk but keep short meaningful concepts
RATE_LIMIT_DELAY = 0.5  # Slower rate to avoid quota issues
BATCH_LOG_INTERVAL = 50


def get_concepts_without_embeddings(db: DatabaseManager, limit: int = None):
    """Get concepts that don't have embeddings yet."""
    conn = db.get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT c.id, c.type, c.content
        FROM concepts c
        LEFT JOIN embeddings e ON c.id = e.concept_id
        WHERE e.id IS NULL
        AND LENGTH(c.content) >= ?
        ORDER BY c.id
    """

    params = [MIN_CONTENT_LENGTH]

    if limit:
        sql += f" LIMIT {limit}"

    cursor.execute(sql, params)
    return cursor.fetchall()


def generate_concept_embeddings(
    db_path: str = "haios_memory.db",
    limit: int = None,
    dry_run: bool = False
):
    """Generate embeddings for concepts without them."""

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in environment.")
        sys.exit(1)

    db = DatabaseManager(db_path)
    extractor = ExtractionManager(api_key=api_key)

    concepts = get_concepts_without_embeddings(db, limit)
    total = len(concepts)

    if total == 0:
        print(f"All concepts with >={MIN_CONTENT_LENGTH} chars have embeddings.")
        return

    print(f"Found {total} concepts without embeddings (>={MIN_CONTENT_LENGTH} chars).")

    if dry_run:
        print("\n[DRY RUN] Would process:")
        for cid, ctype, content in concepts[:15]:
            preview = content[:40] + "..." if len(content) > 40 else content
            print(f"  [{cid}] {ctype}: {preview}")
        if total > 15:
            print(f"  ... and {total - 15} more")
        return

    print(f"\nGenerating embeddings (rate: {1/RATE_LIMIT_DELAY:.1f} req/sec)...")
    print("-" * 60)

    success_count = 0
    error_count = 0
    start_time = time.time()

    conn = db.get_connection()
    cursor = conn.cursor()

    for i, (concept_id, ctype, content) in enumerate(concepts, 1):
        try:
            # Generate embedding
            embedding = extractor.embed_content(content)

            # Serialize vector (sqlite-vec expects float32 bytes)
            import struct
            vector_bytes = struct.pack(f'{len(embedding)}f', *embedding)

            # Store in database
            cursor.execute(
                """INSERT INTO embeddings (concept_id, vector, model, dimensions, created_at)
                   VALUES (?, ?, ?, ?, datetime('now'))""",
                (concept_id, vector_bytes, EMBEDDING_MODEL, len(embedding))
            )

            success_count += 1

            # Commit periodically
            if success_count % 10 == 0:
                conn.commit()

            # Progress logging
            if i % BATCH_LOG_INTERVAL == 0 or i == total:
                elapsed = time.time() - start_time
                rate = success_count / elapsed if elapsed > 0 else 0
                print(f"  [{i}/{total}] {success_count} success, {error_count} errors ({rate:.2f}/sec)")

            time.sleep(RATE_LIMIT_DELAY)

        except Exception as e:
            logging.error(f"Embedding failed for concept {concept_id}: {e}")
            error_count += 1
            if error_count > 10:
                print("Too many errors, stopping.")
                break

    conn.commit()

    elapsed = time.time() - start_time
    print("-" * 60)
    print(f"COMPLETE in {elapsed:.1f}s")
    print(f"  Success: {success_count}")
    print(f"  Errors:  {error_count}")
    if elapsed > 0:
        print(f"  Rate:    {success_count/elapsed:.2f} embeddings/sec")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Complete missing concept embeddings")
    parser.add_argument("--limit", type=int, help="Process at most N concepts")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    generate_concept_embeddings(limit=args.limit, dry_run=args.dry_run)
