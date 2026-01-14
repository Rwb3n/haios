import os
import hashlib
import time
import logging
from typing import Optional
from pathlib import Path
from haios_etl.database import DatabaseManager
from haios_etl.extraction import ExtractionManager, ExtractionError

# Binary file extensions to skip
BINARY_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',
    '.zip', '.tar', '.gz', '.rar', '.7z',
    '.exe', '.dll', '.so', '.dylib',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
}

def read_file_safely(file_path: str, max_size_mb: int = 10) -> Optional[str]:
    """
    Safely read file content with encoding fallback and binary detection.
    
    Args:
        file_path: Path to file
        max_size_mb: Maximum file size in MB (default: 10MB)
    
    Returns:
        File content as string, or None if binary/unreadable
    """
    try:
        # Check file extension
        extension = Path(file_path).suffix.lower()
        if extension in BINARY_EXTENSIONS:
            logging.info(f"Skipping binary file: {file_path}")
            return None
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > max_size_mb * 1024 * 1024:
            logging.warning(f"Large file ({file_size / 1024 / 1024:.1f}MB): {file_path}")
        
        # Try multiple encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    
                    # Check for null bytes (binary content)
                    if '\x00' in content:
                        logging.info(f"Null bytes detected (binary): {file_path}")
                        return None
                    
                    # Check for empty content
                    if not content.strip():
                        logging.info(f"Skipping empty file: {file_path}")
                        return None

                    if encoding != 'utf-8':
                        logging.info(f"Read {file_path} with fallback encoding: {encoding}")
                    
                    return content
                    
            except UnicodeDecodeError:
                if encoding == encodings[-1]:
                    # Last encoding failed, use errors='replace'
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                        logging.warning(f"Read {file_path} with errors replaced")
                        return content
                continue
                
    except PermissionError as e:
        logging.error(f"Permission denied: {file_path} - {e}")
        return None
    except FileNotFoundError as e:
        logging.error(f"File not found: {file_path} - {e}")
        return None
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        return None

def compute_file_hash(file_path: str) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

class BatchProcessor:
    def __init__(self, db_manager: DatabaseManager, extraction_manager: ExtractionManager):
        self.db_manager = db_manager
        self.extraction_manager = extraction_manager

    def process_file(self, file_path: str):
        """
        Process a single file:
        1. Check if processed and unchanged (skip).
        2. Extract content.
        3. Store results.
        4. Update status.
        """
        try:
            start_time = time.perf_counter()
            
            # 1. Compute hash
            current_hash = compute_file_hash(file_path)
            
            # 2. Check status and hash
            last_status = self.db_manager.get_processing_status(file_path)
            last_hash = self.db_manager.get_artifact_hash(file_path) # We added this to DB manager
            
            if last_status in ("success", "skipped") and last_hash == current_hash:
                # Skipped - file unchanged
                logging.info(f"[SKIP] {file_path}")
                self.db_manager.update_processing_status(file_path, "skipped")
                return

            # File is new or changed - proceed with extraction
            logging.info(f"[PROCESS] {file_path}")

            # 3. Read content safely
            content = read_file_safely(file_path)
            if content is None:
                # Binary file or unreadable
                self.db_manager.update_processing_status(file_path, "skipped", "Binary or unreadable file")
                return
                
            # 4. Extract
            result = self.extraction_manager.extract_from_file(file_path, content)
            
            # 5. Store
            file_size = os.path.getsize(file_path)
            artifact_id = self.db_manager.insert_artifact(file_path, current_hash, file_size)
            
            for entity in result.entities:
                ent_id = self.db_manager.insert_entity(entity.type, entity.value)
                self.db_manager.record_entity_occurrence(ent_id, artifact_id, None)

            for concept in result.concepts:
                con_id = self.db_manager.insert_concept(concept.type, concept.content, concept.source_adr)
                self.db_manager.record_concept_occurrence(con_id, artifact_id, None)

            # 6. Metrics
            end_time = time.perf_counter()
            processing_time = end_time - start_time
            
            # Assuming 0 tokens for now as we don't have it in result yet
            tokens_used = 0 
            
            self.db_manager.insert_quality_metrics(
                artifact_id=artifact_id,
                entities_extracted=len(result.entities),
                concepts_extracted=len(result.concepts),
                processing_time=processing_time,
                tokens_used=tokens_used
            )

            # 7. Update status
            self.db_manager.update_processing_status(file_path, "success")

        except Exception as e:
            # Log error
            self.db_manager.update_processing_status(file_path, "error", str(e))
            pass
