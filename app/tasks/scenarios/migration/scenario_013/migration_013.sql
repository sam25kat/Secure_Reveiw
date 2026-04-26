-- Migration: extend commenting to a new content type 'storymaps'
-- Ticket: SOCIAL-3712

CREATE TABLE storymaps (
    id BIGSERIAL PRIMARY KEY,
    creator_id BIGINT REFERENCES users(id),
    title VARCHAR(300),
    storyline JSONB,
    published BOOLEAN DEFAULT FALSE
);

UPDATE comments SET target_type = 'storymap' WHERE target_type = 'sm';
