-- Realtime ad serving (microsecond-sensitive)
CREATE TABLE ad_impressions (
    id BIGSERIAL PRIMARY KEY,
    campaign_id BIGINT NOT NULL,
    creative_id BIGINT NOT NULL,
    user_id BIGINT,
    placement_id INTEGER NOT NULL,
    served_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    cost_micros BIGINT
);
CREATE INDEX idx_imp_campaign_served ON ad_impressions(campaign_id, served_at);
CREATE INDEX idx_imp_creative ON ad_impressions(creative_id);
CREATE INDEX idx_imp_placement_served ON ad_impressions(placement_id, served_at);
CREATE INDEX idx_imp_user ON ad_impressions(user_id) WHERE user_id IS NOT NULL;

-- Hot path: ad-serving query takes p99 < 5ms with these indexes

CREATE TABLE campaigns (
    id BIGSERIAL PRIMARY KEY,
    advertiser_id BIGINT,
    daily_budget_cents BIGINT,
    is_active BOOLEAN
);
