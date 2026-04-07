-- Migration 1: Drop legacy sessions table
-- Ticket: INFRA-456
-- Reason: Moving to JWT-based auth, sessions table no longer needed

DROP TABLE sessions;
