-- Migration: improve telemetry query performance
-- Ticket: PERF-3401

CREATE INDEX idx_telemetry_device_metric_time
    ON telemetry_records(device_id, metric_name, recorded_at);

ALTER TABLE telemetry_records SET (fillfactor = 100);

CLUSTER telemetry_records USING idx_telemetry_device_metric_time;

CREATE INDEX idx_telemetry_payload_gin ON telemetry_records USING gin(tags);
