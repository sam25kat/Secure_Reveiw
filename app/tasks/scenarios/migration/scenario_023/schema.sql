-- Document storage for collaborative editor
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL,
    title VARCHAR(300) NOT NULL,
    body TEXT NOT NULL,                          -- can be megabytes (collaborative doc)
    yjs_state BYTEA,                              -- CRDT state, 100KB - 5MB typical
    word_count INTEGER,
    char_count INTEGER,
    is_archived BOOLEAN DEFAULT FALSE,
    last_edited_at TIMESTAMPTZ DEFAULT NOW(),
    last_edited_by BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_docs_workspace ON documents(workspace_id);
CREATE INDEX idx_docs_archived ON documents(is_archived);

-- Hot query: SELECT id, title, last_edited_at FROM documents WHERE workspace_id=? ORDER BY last_edited_at DESC LIMIT 50
-- This query DOES NOT need body or yjs_state, but currently row-fetches all of them

CREATE TABLE document_links (
    source_doc_id BIGINT,
    target_doc_id BIGINT,
    PRIMARY KEY (source_doc_id, target_doc_id)
);
