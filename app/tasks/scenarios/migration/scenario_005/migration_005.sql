-- Migration: introduce centralized order numbering for cross-region uniqueness
-- Ticket: ORDER-2891
-- Author: platform@company.com

CREATE TABLE global_counters (
    name VARCHAR(40) PRIMARY KEY,
    value BIGINT NOT NULL DEFAULT 0
);

INSERT INTO global_counters(name, value) VALUES ('order_number', 0);

CREATE OR REPLACE FUNCTION next_order_number() RETURNS BIGINT AS $$
DECLARE
    new_val BIGINT;
BEGIN
    UPDATE global_counters SET value = value + 1 WHERE name = 'order_number'
        RETURNING value INTO new_val;
    RETURN new_val;
END;
$$ LANGUAGE plpgsql;

ALTER TABLE orders ALTER COLUMN order_number DROP DEFAULT;
ALTER TABLE orders ALTER COLUMN order_number SET DEFAULT 'ORD-' || next_order_number();

DROP SEQUENCE orders_id_seq CASCADE;
