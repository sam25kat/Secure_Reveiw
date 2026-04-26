-- Migration: speed up product search filtering
-- Ticket: SEARCH-1820

CREATE INDEX idx_products_metadata ON products USING gin(metadata);

ALTER TABLE products ADD COLUMN searchable_keywords JSONB DEFAULT '[]'::jsonb;

UPDATE products
   SET searchable_keywords = (
       SELECT jsonb_agg(value)
         FROM jsonb_each_text(metadata)
        WHERE key IN ('brand', 'category', 'color')
   )
 WHERE jsonb_typeof(metadata) = 'object';

CREATE INDEX idx_products_keywords ON products USING gin(searchable_keywords);
