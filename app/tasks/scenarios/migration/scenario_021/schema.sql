-- Source database for logical replication to analytics warehouse
CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(120),
    pii_ssn VARCHAR(20),
    pii_dob DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(id),
    status VARCHAR(20),
    total_cents BIGINT,
    placed_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_orders_customer ON orders(customer_id);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    sku VARCHAR(80) UNIQUE,
    title VARCHAR(300),
    price_cents INTEGER
);

-- Currently NO replica identity set on most tables — defaults to PRIMARY KEY which is fine for INSERT-only
-- but UPDATE/DELETE replication needs FULL replica identity if PK changes are infrequent
