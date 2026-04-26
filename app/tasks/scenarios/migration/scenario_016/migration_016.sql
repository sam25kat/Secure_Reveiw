-- Migration: add 'currency' dimension to transactions and analytics
-- Ticket: ANALYTICS-4012

ALTER TABLE transactions ADD COLUMN currency CHAR(3) NOT NULL DEFAULT 'USD';

DROP MATERIALIZED VIEW merchant_daily_summary;

CREATE MATERIALIZED VIEW merchant_daily_summary AS
SELECT
    merchant_id,
    currency,
    DATE(occurred_at) AS day,
    COUNT(*) AS tx_count,
    SUM(amount_cents) AS gross_cents,
    SUM(fee_cents) AS fees_cents,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_count
FROM transactions
WHERE occurred_at > NOW() - INTERVAL '90 days'
GROUP BY merchant_id, currency, DATE(occurred_at);

REFRESH MATERIALIZED VIEW merchant_daily_summary;
