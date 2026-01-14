-- Migration 009: Fix synthesis_cluster_members CHECK constraint
-- generated: 2025-12-06
-- Reason: Bridge insights (cross-pollination) attempt to insert member_type='cross'.
-- Previous constraint only allowed 'concept' or 'trace'.

BEGIN TRANSACTION;

-- 1. Create temporary table with old schema (but no constraint prevents us copying if we wanted, 
-- though table is likely empty or has valid data)
CREATE TABLE synthesis_cluster_members_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_id INTEGER NOT NULL,
    member_type TEXT NOT NULL CHECK(member_type IN ('concept', 'trace', 'cross')), -- Added 'cross'
    member_id INTEGER NOT NULL,
    similarity_to_centroid REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cluster_id) REFERENCES synthesis_clusters(id) ON DELETE CASCADE
);

-- 2. Copy data (if any)
INSERT INTO synthesis_cluster_members_new (id, cluster_id, member_type, member_id, similarity_to_centroid, created_at)
SELECT id, cluster_id, member_type, member_id, similarity_to_centroid, created_at
FROM synthesis_cluster_members;

-- 3. Drop old table
DROP TABLE synthesis_cluster_members;

-- 4. Rename new table
ALTER TABLE synthesis_cluster_members_new RENAME TO synthesis_cluster_members;

-- 5. Recreate indexes
CREATE INDEX idx_cluster_members_cluster ON synthesis_cluster_members(cluster_id);
CREATE INDEX idx_cluster_members_type ON synthesis_cluster_members(member_type, member_id);

COMMIT;
