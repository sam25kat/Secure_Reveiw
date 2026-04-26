-- Product catalog (started as MVP, now serves 50K req/sec read traffic)
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    sku VARCHAR(60) NOT NULL UNIQUE,
    title VARCHAR(300) NOT NULL,
    base_price_cents INTEGER NOT NULL,
    currency CHAR(3) DEFAULT 'USD',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- metadata typically includes: brand, category, color, size, weight_g, material, tags[]
    -- search uses metadata->>'brand', metadata->>'category', metadata @> '{"in_stock": true}'
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_products_published ON products(is_published);
CREATE INDEX idx_products_created ON products(created_at);

CREATE TABLE product_views (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT REFERENCES products(id),
    viewer_id BIGINT,
    viewed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE categories (
    slug VARCHAR(80) PRIMARY KEY,
    display_name VARCHAR(120),
    parent_slug VARCHAR(80) REFERENCES categories(slug)
);

-- Used by an admin-only legacy report
CREATE TABLE product_audit_legacy (
    id BIGSERIAL,
    sku VARCHAR(60),
    changed_field VARCHAR(40),
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMPTZ
);
