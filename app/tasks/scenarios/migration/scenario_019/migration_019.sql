-- Migration: add audit columns to inventory, orders, order_items, shipments
-- Ticket: COMPLIANCE-8821

BEGIN;

ALTER TABLE shipments ADD COLUMN updated_by BIGINT;
ALTER TABLE order_items ADD COLUMN updated_by BIGINT;
ALTER TABLE orders ADD COLUMN updated_by BIGINT;
ALTER TABLE inventory ADD COLUMN updated_by BIGINT;

CREATE INDEX idx_orders_updated_by ON orders(updated_by);
CREATE INDEX idx_inventory_updated_by ON inventory(updated_by);

COMMIT;
