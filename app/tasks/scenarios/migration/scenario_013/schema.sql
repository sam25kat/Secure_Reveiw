-- Activity / commenting system across multiple entity types
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120),
    avatar_url TEXT
);

CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    author_id BIGINT REFERENCES users(id),
    title VARCHAR(300),
    body TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE photos (
    id BIGSERIAL PRIMARY KEY,
    uploader_id BIGINT REFERENCES users(id),
    storage_url TEXT,
    width INTEGER,
    height INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE videos (
    id BIGSERIAL PRIMARY KEY,
    uploader_id BIGINT REFERENCES users(id),
    storage_url TEXT,
    duration_sec INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    author_id BIGINT NOT NULL REFERENCES users(id),
    target_type VARCHAR(20) NOT NULL,
    target_id BIGINT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_comments_target ON comments(target_type, target_id);
