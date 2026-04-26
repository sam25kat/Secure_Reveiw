-- Payment processing schema (financial-grade consistency required)
CREATE TABLE accounts (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    currency CHAR(3) NOT NULL,
    balance_cents BIGINT NOT NULL DEFAULT 0,
    available_cents BIGINT NOT NULL DEFAULT 0,
    pending_cents BIGINT NOT NULL DEFAULT 0,
    last_settled_at TIMESTAMPTZ,
    version INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT positive_balance CHECK (balance_cents >= 0)
);
CREATE UNIQUE INDEX idx_accounts_customer_currency ON accounts(customer_id, currency);

CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES accounts(id),
    amount_cents BIGINT NOT NULL,
    direction CHAR(1) NOT NULL CHECK (direction IN ('D', 'C')),
    status VARCHAR(20) NOT NULL,
    external_ref VARCHAR(80),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_payments_account ON payments(account_id);

CREATE TABLE ledger_entries (
    id BIGSERIAL PRIMARY KEY,
    payment_id BIGINT NOT NULL REFERENCES payments(id),
    account_id BIGINT NOT NULL REFERENCES accounts(id),
    debit_cents BIGINT DEFAULT 0,
    credit_cents BIGINT DEFAULT 0,
    posted_at TIMESTAMPTZ DEFAULT NOW()
);

-- Other unrelated tables in the DB
CREATE TABLE notification_preferences (
    customer_id BIGINT PRIMARY KEY,
    email_optin BOOLEAN DEFAULT TRUE,
    sms_optin BOOLEAN DEFAULT FALSE
);
