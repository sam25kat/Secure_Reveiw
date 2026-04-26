-- Migration: add a 'paused' status, remove 'incomplete' (legacy)
-- Ticket: BILLING-7791

ALTER TYPE subscription_status ADD VALUE 'paused';

ALTER TYPE subscription_status RENAME VALUE 'incomplete' TO 'pending_payment';

ALTER TYPE subscription_status DROP VALUE 'past_due';

UPDATE subscriptions SET status = 'paused' WHERE status = 'past_due';
