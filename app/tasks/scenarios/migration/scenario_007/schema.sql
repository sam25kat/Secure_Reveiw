-- Telemetry ingestion (current schema — chosen by prev team)
CREATE TABLE telemetry_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL,
    metric_name VARCHAR(80) NOT NULL,
    metric_value DOUBLE PRECISION,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tags JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_telemetry_device ON telemetry_records(device_id);
CREATE INDEX idx_telemetry_metric ON telemetry_records(metric_name);
CREATE INDEX idx_telemetry_time ON telemetry_records(recorded_at);

CREATE TABLE devices (
    id UUID PRIMARY KEY,
    serial VARCHAR(60) UNIQUE,
    customer_account_id BIGINT,
    firmware_version VARCHAR(20),
    last_seen TIMESTAMPTZ
);

CREATE TABLE alert_rules (
    id BIGSERIAL PRIMARY KEY,
    metric VARCHAR(80) NOT NULL,
    threshold DOUBLE PRECISION,
    operator VARCHAR(8),
    enabled BOOLEAN DEFAULT TRUE
);

CREATE TABLE customer_accounts (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120),
    plan VARCHAR(40)
);
