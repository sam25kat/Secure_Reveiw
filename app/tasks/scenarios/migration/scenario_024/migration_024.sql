-- Migration: enable Postgres RLS for defense-in-depth tenant isolation
-- Ticket: SECURITY-1102

ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE issue_comments ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_projects ON projects
    USING (tenant_id = current_setting('app.tenant_id')::BIGINT);

CREATE POLICY tenant_isolation_issues ON issues
    USING (tenant_id = current_setting('app.tenant_id')::BIGINT);

CREATE POLICY tenant_isolation_comments ON issue_comments
    USING (issue_id IN (SELECT id FROM issues WHERE tenant_id = current_setting('app.tenant_id')::BIGINT));
