-- Migration: enable logical replication for analytics warehouse sync
-- Ticket: DATA-7700

CREATE PUBLICATION analytics_pub FOR ALL TABLES;

ALTER TABLE customers REPLICA IDENTITY FULL;

CREATE INDEX idx_customers_updated ON customers(updated_at);

ALTER TABLE orders ADD COLUMN region_code VARCHAR(8) DEFAULT 'US-EAST';

UPDATE orders SET region_code = 'US-EAST' WHERE region_code IS NULL;
