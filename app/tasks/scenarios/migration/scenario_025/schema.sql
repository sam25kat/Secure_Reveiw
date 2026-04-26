-- Production setup: PG primary + 3 read replicas, 200 app servers
-- Each app: 50 worker threads, currently each opens its own connection (no pool)
-- Result: 200 servers × 50 threads = 10,000 potential connections

CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(120)
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT REFERENCES customers(id),
    total_cents BIGINT,
    placed_at TIMESTAMPTZ DEFAULT NOW()
);
