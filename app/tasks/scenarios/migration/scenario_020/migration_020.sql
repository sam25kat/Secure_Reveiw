-- Migration: introduce native partitioning for documents to control table size
-- Ticket: SCALE-9921

CREATE TABLE documents_new (
    id BIGSERIAL,
    tenant_id BIGINT NOT NULL,
    title VARCHAR(300),
    body TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE documents_2024 PARTITION OF documents_new
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE documents_2025 PARTITION OF documents_new
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE documents_2026 PARTITION OF documents_new
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE INDEX idx_documents_new_tenant ON documents_new(tenant_id);
