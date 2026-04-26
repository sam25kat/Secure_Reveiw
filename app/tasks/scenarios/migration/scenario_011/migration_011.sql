-- Migration: enforce data integrity invariants
-- Ticket: BILLING-5567

ALTER TABLE subscriptions
    ADD CONSTRAINT chk_period_order CHECK (current_period_end > current_period_start);

ALTER TABLE subscriptions
    ADD CONSTRAINT chk_canceled_after_start CHECK (canceled_at IS NULL OR canceled_at >= current_period_start);

ALTER TABLE subscriptions
    ADD CONSTRAINT chk_status_values CHECK (status IN ('active','trialing','past_due','canceled','incomplete'));

CREATE INDEX idx_subs_active_customer ON subscriptions(customer_id) WHERE status = 'active';
