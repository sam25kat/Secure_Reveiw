-- Migration 1: Rename username to handle, expand display_name
-- Ticket: PROFILE-567

ALTER TABLE profiles RENAME COLUMN username TO handle;

ALTER TABLE profiles ALTER COLUMN display_name TYPE VARCHAR(255);
