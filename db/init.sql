CREATE EXTENSION IF NOT EXISTS pgcrypto;


CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    filename TEXT NOT NULL,
    original_path TEXT NOT NULL UNIQUE,

    file_type VARCHAR(20) NOT NULL,
    mime_type TEXT,

    size_bytes BIGINT NOT NULL,
    sha256 CHAR(64) NOT NULL,

    width INTEGER,
    height INTEGER,

    duration_seconds DOUBLE PRECISION,
    frame_rate DOUBLE PRECISION,

    page_count INTEGER,

    description TEXT,
    extracted_text TEXT,

    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    error_message TEXT,

    file_modified_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS indexing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    total_files INTEGER NOT NULL DEFAULT 0,
    processed_files INTEGER NOT NULL DEFAULT 0,
    successful_files INTEGER NOT NULL DEFAULT 0,
    failed_files INTEGER NOT NULL DEFAULT 0,
    skipped_files INTEGER NOT NULL DEFAULT 0,

    status VARCHAR(30) NOT NULL DEFAULT 'pending',

    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_assets_sha256
    ON assets(sha256);

CREATE INDEX IF NOT EXISTS idx_assets_file_type
    ON assets(file_type);

CREATE INDEX IF NOT EXISTS idx_assets_status
    ON assets(status);

CREATE INDEX IF NOT EXISTS idx_assets_created_at
    ON assets(created_at);