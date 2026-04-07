-- Migration 3: Add user preferences
-- Ticket: USER-321

ALTER TABLE users ADD COLUMN preferences JSONB NOT NULL;

ALTER TABLE users ALTER COLUMN email TYPE TEXT;
