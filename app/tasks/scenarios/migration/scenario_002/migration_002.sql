-- Migration 2: Add verified badge and location
-- Depends on: migration_001
-- Ticket: PROFILE-568

ALTER TABLE profiles ADD COLUMN is_verified BOOLEAN NOT NULL;

ALTER TABLE profiles ADD COLUMN location VARCHAR(100);

CREATE INDEX idx_profiles_handle ON profiles(handle);
