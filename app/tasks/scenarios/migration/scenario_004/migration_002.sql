-- Migration 2: Clean up products table
-- Ticket: CATALOG-789

ALTER TABLE products RENAME COLUMN old_price TO legacy_price;

ALTER TABLE products ADD COLUMN sku VARCHAR(50) NOT NULL;

CREATE INDEX idx_products_sku ON products(sku);
