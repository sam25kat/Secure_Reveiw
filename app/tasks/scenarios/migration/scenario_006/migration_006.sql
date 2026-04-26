-- Migration: support time-range analytical queries on events
-- Ticket: ANALYTICS-7212

CREATE INDEX idx_events_occurred_at ON events(occurred_at);

CREATE INDEX idx_events_type_time ON events(event_type, occurred_at);

ALTER TABLE events ADD COLUMN cohort_bucket INTEGER NOT NULL DEFAULT (EXTRACT(epoch FROM occurred_at)::INTEGER / 86400);

VACUUM ANALYZE events;
