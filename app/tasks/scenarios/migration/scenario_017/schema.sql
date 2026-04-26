-- Job queue (dequeue-heavy, UPDATEs every row 5-10 times before completion)
CREATE TABLE jobs (
    id BIGSERIAL PRIMARY KEY,
    queue_name VARCHAR(60) NOT NULL,
    payload JSONB NOT NULL,
    state VARCHAR(20) NOT NULL DEFAULT 'pending',
    attempts SMALLINT NOT NULL DEFAULT 0,
    locked_by VARCHAR(80),
    locked_until TIMESTAMPTZ,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_jobs_queue_state ON jobs(queue_name, state);
CREATE INDEX idx_jobs_locked_until ON jobs(locked_until);

-- Throughput observed: 6000 jobs/sec
-- Each job updated 5-10x: state changes, attempts++, lock acquire/release, error append
-- Table is "small" (50K active rows) but bloats to 80GB without aggressive vacuum

CREATE TABLE job_history (
    id BIGSERIAL PRIMARY KEY,
    job_id BIGINT,
    transitioned_to VARCHAR(20),
    occurred_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE workers (
    id VARCHAR(80) PRIMARY KEY,
    hostname VARCHAR(120),
    started_at TIMESTAMPTZ
);
