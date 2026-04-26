-- User account schema (B2B SaaS, multi-tenant)
CREATE TABLE accounts (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(120),
    role VARCHAR(40) NOT NULL DEFAULT 'member',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    UNIQUE (workspace_id, email)
);
CREATE INDEX idx_accounts_workspace ON accounts(workspace_id);
CREATE INDEX idx_accounts_email ON accounts(email);

CREATE TABLE workspaces (
    id BIGSERIAL PRIMARY KEY,
    slug VARCHAR(80) UNIQUE,
    plan VARCHAR(40),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE invitations (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT REFERENCES workspaces(id),
    email VARCHAR(255),
    invited_by BIGINT,
    expires_at TIMESTAMPTZ
);

-- Audit table (rarely queried)
CREATE TABLE auth_audit (
    id BIGSERIAL,
    account_id BIGINT,
    action VARCHAR(40),
    ip INET,
    occurred_at TIMESTAMPTZ DEFAULT NOW()
);
