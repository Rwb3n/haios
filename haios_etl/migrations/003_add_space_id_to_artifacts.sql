-- Add space_id column to artifacts table
ALTER TABLE artifacts ADD COLUMN space_id TEXT;
CREATE INDEX idx_artifacts_space_id ON artifacts(space_id);
