-- Data Lake & Cognitive Analytics Schema for Myntra Wishlist Discovery Engine

CREATE TABLE IF NOT EXISTS ingestion_batches (
    batch_id VARCHAR(64) PRIMARY KEY,
    source_channel VARCHAR(32) NOT NULL,
    records_count INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(32) DEFAULT 'RUNNING'
);

CREATE TABLE IF NOT EXISTS raw_feedback (
    id VARCHAR(64) PRIMARY KEY,
    source_channel VARCHAR(32) NOT NULL,
    author_id_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    raw_text TEXT NOT NULL,
    clean_text TEXT NOT NULL,
    thread_url TEXT NOT NULL,
    raw_metadata JSON,
    ingestion_batch_id VARCHAR(64) REFERENCES ingestion_batches(batch_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Phase 2: Processed & Relevant Cognitive Friction Table (Zero Monetary Allowed)
CREATE TABLE IF NOT EXISTS classified_feedback (
    id VARCHAR(64) PRIMARY KEY,
    raw_feedback_id VARCHAR(64) REFERENCES raw_feedback(id),
    source_channel VARCHAR(32) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    clean_text TEXT NOT NULL,
    source_url TEXT NOT NULL,
    primary_category VARCHAR(64) NOT NULL,
    confidence_score FLOAT NOT NULL,
    verbatim_quote TEXT NOT NULL,
    decision_barrier_summary TEXT NOT NULL,
    user_intent VARCHAR(64),
    detected_off_platform_action VARCHAR(128),
    secondary_category VARCHAR(64),
    classification_batch_id VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Phase 2 Relevance Exclusion Log: Records excluded because they are irrelevant to wishlist/purchase non-conversion
CREATE TABLE IF NOT EXISTS relevance_exclusion_log (
    id VARCHAR(64) PRIMARY KEY,
    raw_feedback_id VARCHAR(64) REFERENCES raw_feedback(id),
    source_channel VARCHAR(32) NOT NULL,
    raw_text TEXT NOT NULL,
    source_url TEXT,
    exclusion_reason TEXT NOT NULL,
    classification_batch_id VARCHAR(64),
    excluded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Phase 2 Monetary Purge Log: Records dropped due to the Zero-Monetary rule
CREATE TABLE IF NOT EXISTS monetary_purge_log (
    id VARCHAR(64) PRIMARY KEY,
    raw_feedback_id VARCHAR(64) REFERENCES raw_feedback(id),
    source_channel VARCHAR(32) NOT NULL,
    raw_text TEXT NOT NULL,
    source_url TEXT,
    purge_reason TEXT NOT NULL,
    classification_batch_id VARCHAR(64),
    purged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_raw_channel ON raw_feedback(source_channel);
CREATE INDEX IF NOT EXISTS idx_raw_batch ON raw_feedback(ingestion_batch_id);
CREATE INDEX IF NOT EXISTS idx_classified_category ON classified_feedback(primary_category);
CREATE INDEX IF NOT EXISTS idx_classified_channel ON classified_feedback(source_channel);
