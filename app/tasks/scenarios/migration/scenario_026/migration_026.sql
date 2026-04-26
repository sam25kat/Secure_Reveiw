-- Migration: introduce stored procedure for inventory reservation
-- Ticket: CHECKOUT-2200

CREATE OR REPLACE FUNCTION reserve_inventory(p_sku VARCHAR, p_qty INTEGER, p_cart_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    available INTEGER;
BEGIN
    SELECT on_hand - reserved INTO available FROM inventory WHERE sku = p_sku;

    IF available >= p_qty THEN
        UPDATE inventory SET reserved = reserved + p_qty WHERE sku = p_sku;
        INSERT INTO reservations(sku, qty, cart_id, expires_at)
            VALUES (p_sku, p_qty, p_cart_id, NOW() + INTERVAL '15 min');
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;
