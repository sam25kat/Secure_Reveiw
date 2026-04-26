-- Migration: introduce soft-delete for compliance (GDPR right-to-restoration)
-- Ticket: COMPLIANCE-2240

ALTER TABLE accounts ADD COLUMN deleted_at TIMESTAMPTZ;
ALTER TABLE accounts ADD COLUMN deletion_reason VARCHAR(60);

ALTER TABLE accounts DROP CONSTRAINT accounts_workspace_id_email_key;
ALTER TABLE accounts ADD CONSTRAINT accounts_workspace_id_email_key UNIQUE (workspace_id, email);

CREATE INDEX idx_accounts_deleted_at ON accounts(deleted_at);

UPDATE accounts SET is_active = FALSE WHERE is_active IS NULL;
