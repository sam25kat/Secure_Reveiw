-- Migration: enforce statement timeouts and isolation per migration script
-- Ticket: PLATFORM-3320

BEGIN;

SET LOCAL statement_timeout = '30s';
SET LOCAL lock_timeout = '5s';
SET LOCAL idle_in_transaction_session_timeout = '60s';

CREATE INDEX idx_fu_feature ON feature_users(feature_key);

ALTER TABLE feature_users ADD COLUMN granted_by BIGINT;

UPDATE feature_users SET granted_by = 0 WHERE granted_by IS NULL;

COMMIT;
