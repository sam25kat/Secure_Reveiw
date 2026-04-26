-- Event tracking schema for product analytics (~2B rows, growing 80M/day)
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    session_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_payload JSONB,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    schema_version SMALLINT DEFAULT 1
);

CREATE INDEX idx_events_user ON events(user_id);
CREATE INDEX idx_events_session ON events(session_id);

-- Other unrelated analytics tables
CREATE TABLE event_types (
    type VARCHAR(50) PRIMARY KEY,
    description TEXT,
    is_pii_sensitive BOOLEAN DEFAULT FALSE,
    retention_days INTEGER DEFAULT 365
);

CREATE TABLE feature_flags (
    flag_name VARCHAR(80) PRIMARY KEY,
    rollout_pct SMALLINT DEFAULT 0,
    last_modified TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE analytics_dashboards (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120),
    owner_email VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
