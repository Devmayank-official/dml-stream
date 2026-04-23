-- Migration 001: Initial Schema
-- Creates core tables for history, download queue, and configuration

-- Download History Table
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL DEFAULT 0,
    download_date TEXT NOT NULL,
    download_type TEXT NOT NULL DEFAULT 'video',
    status TEXT NOT NULL DEFAULT 'success',
    duration INTEGER,
    format TEXT
);

-- Download Queue Table
CREATE TABLE IF NOT EXISTS download_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    download_type TEXT NOT NULL DEFAULT 'video',
    output_folder TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3
);

-- Configuration Table
CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_history_download_date ON history(download_date DESC);
CREATE INDEX IF NOT EXISTS idx_history_status ON history(status);
CREATE INDEX IF NOT EXISTS idx_history_download_type ON history(download_type);

CREATE INDEX IF NOT EXISTS idx_queue_status ON download_queue(status);
CREATE INDEX IF NOT EXISTS idx_queue_priority ON download_queue(priority DESC, created_at ASC);
