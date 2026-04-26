-- Migration: change idx_imp_campaign_served to include cost for budget tracking
-- Ticket: ADS-5512

DROP INDEX idx_imp_campaign_served;

CREATE INDEX idx_imp_campaign_served_cost ON ad_impressions(campaign_id, served_at) INCLUDE (cost_micros);
