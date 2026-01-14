-- Migration: 002_add_embeddings
-- Description: Adds the embeddings table for vector search.
-- Date: 2025-11-24

CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id INTEGER,
    concept_id INTEGER,
    entity_id INTEGER,
    vector BLOB NOT NULL,
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_embeddings_artifact ON embeddings(artifact_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_concept ON embeddings(concept_id);
