-- Migration: prevent integer overflow on activities.id
-- Ticket: SCALE-7700

ALTER TABLE activities ALTER COLUMN id TYPE BIGINT;

ALTER TABLE activity_reactions ALTER COLUMN activity_id TYPE BIGINT;
