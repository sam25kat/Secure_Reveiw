-- Production OLTP schema - e-commerce order pipeline
CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(120),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    locale VARCHAR(10) DEFAULT 'en-US',
    marketing_consent BOOLEAN DEFAULT FALSE,
    legacy_customer_code VARCHAR(40)
);
CREATE INDEX idx_customers_email ON customers(email);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    sku VARCHAR(60) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    price_cents INTEGER NOT NULL,
    inventory_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    legacy_warehouse_code VARCHAR(20)
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(id),
    order_number VARCHAR(40) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_cents INTEGER NOT NULL,
    placed_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);

CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id),
    qty INTEGER NOT NULL,
    unit_price_cents INTEGER NOT NULL
);

-- Unused legacy table (kept for historical reporting)
CREATE TABLE archived_promo_codes (
    code VARCHAR(40) PRIMARY KEY,
    discount_pct SMALLINT,
    valid_until DATE
);
