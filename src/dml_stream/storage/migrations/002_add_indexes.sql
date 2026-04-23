-- Migration 002: Add Performance Indexes
-- Adds additional indexes for common query patterns

-- Index for URL lookups in history
CREATE INDEX IF NOT EXISTS idx_history_url ON history(url);

-- Index for title search in history
CREATE INDEX IF NOT EXISTS idx_history_title ON history(title);

-- Index for queue created_at
CREATE INDEX IF NOT EXISTS idx_queue_created_at ON download_queue(created_at);

-- Composite index for history queries
CREATE INDEX IF NOT EXISTS idx_history_type_status ON history(download_type, status);
