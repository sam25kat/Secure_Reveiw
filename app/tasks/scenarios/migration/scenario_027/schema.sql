-- Subscription billing with state-machine status
CREATE TYPE subscription_status AS ENUM (
    'active',
    'past_due',
    'canceled',
    'trialing',
    'incomplete'
);

CREATE TABLE subscriptions (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    status subscription_status NOT NULL DEFAULT 'incomplete',
    plan_id INTEGER,
    started_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_subs_customer ON subscriptions(customer_id);
CREATE INDEX idx_subs_status ON subscriptions(status);

CREATE TABLE subscription_events (
    id BIGSERIAL PRIMARY KEY,
    subscription_id BIGINT,
    from_status subscription_status,
    to_status subscription_status,
    occurred_at TIMESTAMPTZ DEFAULT NOW()
);
