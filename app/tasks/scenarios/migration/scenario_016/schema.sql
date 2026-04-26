-- Analytics dashboard fed by a materialized view on hot OLTP tables
CREATE TABLE merchants (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    merchant_id BIGINT NOT NULL REFERENCES merchants(id),
    amount_cents BIGINT NOT NULL,
    fee_cents BIGINT NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    settled_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_tx_merchant_occurred ON transactions(merchant_id, occurred_at);

CREATE MATERIALIZED VIEW merchant_daily_summary AS
SELECT
    merchant_id,
    DATE(occurred_at) AS day,
    COUNT(*) AS tx_count,
    SUM(amount_cents) AS gross_cents,
    SUM(fee_cents) AS fees_cents,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_count
FROM transactions
WHERE occurred_at > NOW() - INTERVAL '90 days'
GROUP BY merchant_id, DATE(occurred_at);

-- Used by:
--  * dashboard_api.merchant_summary_endpoint
--  * billing_worker.calculate_payouts (queries last 30 days)
--  * fraud_detection.daily_anomaly_check
