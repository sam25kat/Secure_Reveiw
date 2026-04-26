CREATE TABLE feature_users (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    feature_key VARCHAR(80) NOT NULL,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    UNIQUE(user_id, feature_key)
);
CREATE INDEX idx_fu_user ON feature_users(user_id);

CREATE TABLE feature_definitions (
    key VARCHAR(80) PRIMARY KEY,
    name VARCHAR(120),
    is_paid BOOLEAN DEFAULT FALSE,
    rollout_strategy VARCHAR(40)
);

CREATE TABLE billing_events (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_type VARCHAR(40),
    amount_cents BIGINT,
    occurred_at TIMESTAMPTZ DEFAULT NOW()
);
