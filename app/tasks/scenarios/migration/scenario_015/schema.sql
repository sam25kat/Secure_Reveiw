-- Activity feed for social product (built 6 years ago when 'no way we'll hit 2B rows')
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,            -- INTEGER, max 2,147,483,647
    actor_id BIGINT NOT NULL,
    verb VARCHAR(40) NOT NULL,
    object_type VARCHAR(40) NOT NULL,
    object_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    visibility VARCHAR(20) DEFAULT 'public'
);
CREATE INDEX idx_activities_actor ON activities(actor_id);
CREATE INDEX idx_activities_object ON activities(object_type, object_id);

CREATE TABLE activity_reactions (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER NOT NULL REFERENCES activities(id),
    user_id BIGINT NOT NULL,
    reaction CHAR(1),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE follows (
    follower_id BIGINT NOT NULL,
    followee_id BIGINT NOT NULL,
    PRIMARY KEY (follower_id, followee_id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Currently at id ~1.83B / 2.14B max — 14% headroom
