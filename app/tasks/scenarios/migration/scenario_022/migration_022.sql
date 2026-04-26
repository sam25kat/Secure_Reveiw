-- Migration: speed up the 'recent listings in category' page
-- Ticket: SEARCH-2299
-- Common query: SELECT * FROM listings
--               WHERE category_id = ? AND state = 'active'
--               ORDER BY created_at DESC LIMIT 100;

CREATE INDEX idx_listings_cat_state_created ON listings(category_id, state, created_at DESC);

ALTER TABLE listings ALTER COLUMN state SET STATISTICS 1000;

VACUUM ANALYZE listings;
