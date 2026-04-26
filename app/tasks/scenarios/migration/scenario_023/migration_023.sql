-- Migration: speed up dashboard load (workspace document list)
-- Ticket: PERF-4901

CREATE INDEX idx_docs_ws_edited ON documents(workspace_id, last_edited_at DESC);

ALTER TABLE documents ALTER COLUMN body SET STORAGE EXTERNAL;

ALTER TABLE documents ALTER COLUMN yjs_state SET STORAGE EXTERNAL;

ALTER TABLE documents ADD COLUMN preview_text VARCHAR(280);
