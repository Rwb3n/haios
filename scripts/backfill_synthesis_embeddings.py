# generated: 2025-12-11
# System Auto: last updated on: 2025-12-11 00:23:46
"""
Backfill embeddings for SynthesizedInsight concepts.

E2-FIX-001: INV-005 found 2,263 synthesized concepts (99.91%) have no embeddings,
making them invisible to retrieval. This script backfills embeddings for all
SynthesizedInsight concepts that are missing them.

Usage:
    python scripts/backfill_synthesis_embeddings.py [--dry-run] [--batch-size N]

Options:
    --dry-run       Show what would be done without making changes
    --batch-size N  Number of concepts to process per batch (default: 50)
"""

import os
import sys
import struct
import logging
import argparse
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load .env file
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from haios_etl.database import DatabaseManager
from haios_etl.extraction import ExtractionManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_unembedded_concepts(db_path: str) -> list:
    """
    Find SynthesizedInsight concepts without embeddings.

    Returns:
        List of (id, content) tuples
    """
    db = DatabaseManager(db_path)
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.id, c.content
        FROM concepts c
        LEFT JOIN embeddings e ON e.concept_id = c.id
        WHERE c.type = 'SynthesizedInsight'
        AND e.id IS NULL
        ORDER BY c.id
    """)

    results = cursor.fetchall()
    return results


def backfill_embeddings(
    db_path: str,
    api_key: str,
    batch_size: int = 50,
    dry_run: bool = False
) -> dict:
    """
    Generate embeddings for all unembedded SynthesizedInsight concepts.

    Args:
        db_path: Path to the SQLite database
        api_key: Google API key for embedding generation
        batch_size: Number of concepts per batch
        dry_run: If True, don't make changes

    Returns:
        Dict with statistics
    """
    stats = {
        'total_unembedded': 0,
        'processed': 0,
        'success': 0,
        'failed': 0,
        'skipped': 0,
        'dry_run': dry_run
    }

    # Get unembedded concepts
    concepts = get_unembedded_concepts(db_path)
    stats['total_unembedded'] = len(concepts)

    if len(concepts) == 0:
        logger.info("No unembedded SynthesizedInsight concepts found. Nothing to do.")
        return stats

    logger.info(f"Found {len(concepts)} SynthesizedInsight concepts without embeddings")

    if dry_run:
        logger.info("[DRY RUN] Would process these concepts:")
        for cid, content in concepts[:10]:
            logger.info(f"  - ID {cid}: {content[:50]}...")
        if len(concepts) > 10:
            logger.info(f"  ... and {len(concepts) - 10} more")
        return stats

    # Initialize extractor
    extractor = ExtractionManager(api_key)
    db = DatabaseManager(db_path)
    conn = db.get_connection()
    cursor = conn.cursor()

    # Process in batches
    for i in range(0, len(concepts), batch_size):
        batch = concepts[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(concepts) + batch_size - 1) // batch_size

        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} concepts)")

        for concept_id, content in batch:
            stats['processed'] += 1

            try:
                # Generate embedding
                embedding = extractor.embed_content(content[:8000])

                if embedding:
                    # Store embedding
                    cursor.execute("""
                        INSERT INTO embeddings (concept_id, vector, model, dimensions)
                        VALUES (?, ?, ?, ?)
                    """, (
                        concept_id,
                        struct.pack(f'{len(embedding)}f', *embedding),
                        "text-embedding-004",
                        len(embedding)
                    ))
                    conn.commit()
                    stats['success'] += 1

                    if stats['success'] % 10 == 0:
                        logger.info(f"Progress: {stats['success']}/{stats['total_unembedded']} embedded")
                else:
                    logger.warning(f"No embedding returned for concept {concept_id}")
                    stats['failed'] += 1

            except Exception as e:
                logger.error(f"Failed to embed concept {concept_id}: {e}")
                stats['failed'] += 1

        # Rate limit between batches
        if i + batch_size < len(concepts):
            logger.info("Waiting 2s between batches (rate limiting)...")
            time.sleep(2)

    logger.info(f"\nBackfill complete:")
    logger.info(f"  Total unembedded: {stats['total_unembedded']}")
    logger.info(f"  Processed: {stats['processed']}")
    logger.info(f"  Success: {stats['success']}")
    logger.info(f"  Failed: {stats['failed']}")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Backfill embeddings for SynthesizedInsight concepts'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='Number of concepts to process per batch (default: 50)'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        default='haios_memory.db',
        help='Path to the SQLite database (default: haios_memory.db)'
    )

    args = parser.parse_args()

    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key and not args.dry_run:
        logger.error("GOOGLE_API_KEY environment variable not set")
        sys.exit(1)

    # Run backfill
    stats = backfill_embeddings(
        db_path=args.db_path,
        api_key=api_key or "dry-run",
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )

    # Exit with error if any failed
    if stats['failed'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
