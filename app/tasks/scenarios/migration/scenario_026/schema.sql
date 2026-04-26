-- Inventory reservation in e-commerce checkout
CREATE TABLE inventory (
    sku VARCHAR(80) PRIMARY KEY,
    on_hand INTEGER NOT NULL,
    reserved INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE reservations (
    id BIGSERIAL PRIMARY KEY,
    sku VARCHAR(80) NOT NULL,
    qty INTEGER NOT NULL,
    cart_id UUID NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    state VARCHAR(20) NOT NULL DEFAULT 'pending'
);
CREATE INDEX idx_reservations_cart ON reservations(cart_id);
CREATE INDEX idx_reservations_expires ON reservations(expires_at);

CREATE TABLE carts (
    id UUID PRIMARY KEY,
    customer_id BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
