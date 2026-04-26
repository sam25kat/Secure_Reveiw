-- Search index for marketplace listings
CREATE TABLE listings (
    id BIGSERIAL PRIMARY KEY,
    seller_id BIGINT NOT NULL,
    category_id INTEGER NOT NULL,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    price_cents BIGINT NOT NULL,
    state VARCHAR(20) NOT NULL DEFAULT 'draft',
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_listings_seller ON listings(seller_id);
CREATE INDEX idx_listings_category ON listings(category_id);
CREATE INDEX idx_listings_state ON listings(state);

-- Distribution: 95% of rows have state='active', 4% 'sold', 1% 'draft'/'flagged'
-- Distribution: 80% of writes from top-20 sellers (Pareto)

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(80),
    parent_id INTEGER
);

CREATE TABLE listing_views (
    listing_id BIGINT,
    viewed_at DATE,
    view_count BIGINT,
    PRIMARY KEY (listing_id, viewed_at)
);
