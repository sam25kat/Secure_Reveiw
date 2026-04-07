-- Migration: Add foreign key constraints and improve order tracking
-- Ticket: ORDER-890

ALTER TABLE orders ADD COLUMN shipping_address_id BIGINT NOT NULL;

ALTER TABLE order_items
    ADD CONSTRAINT fk_order_items_order
    FOREIGN KEY (order_id) REFERENCES orders(id);

ALTER TABLE order_items
    ADD CONSTRAINT fk_order_items_product
    FOREIGN KEY (product_id) REFERENCES products(id);

CREATE INDEX idx_order_items_order ON order_items(order_id);

CREATE INDEX idx_order_items_product ON order_items(product_id);
