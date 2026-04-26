-- Migration: improve dequeue performance under load
-- Ticket: QUEUE-1801

CREATE INDEX idx_jobs_pending ON jobs(queue_name, created_at) WHERE state = 'pending';

ALTER TABLE jobs ALTER COLUMN payload SET STORAGE EXTENDED;

ALTER TABLE jobs SET (autovacuum_vacuum_scale_factor = 0.2);

ALTER TABLE jobs ADD COLUMN error_count INTEGER NOT NULL DEFAULT 0;
