-- B2B SaaS: tenant-isolated data (single shared cluster, 5K tenants)
-- Plan tiers: free (~70% of tenants), pro (~25%), enterprise (~5%)
-- Top 50 enterprise tenants account for 80% of writes (Pareto-skewed)

CREATE TABLE tenants (
    id BIGSERIAL PRIMARY KEY,
    slug VARCHAR(80) UNIQUE NOT NULL,
    plan VARCHAR(40) NOT NULL,
    region VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id),
    title VARCHAR(300),
    body TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_documents_tenant ON documents(tenant_id);
CREATE INDEX idx_documents_created ON documents(created_at);

CREATE TABLE document_versions (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id),
    version_number INTEGER NOT NULL,
    body_snapshot TEXT,
    edited_by BIGINT,
    edited_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_dv_document ON document_versions(document_id);

CREATE TABLE document_collaborators (
    document_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role VARCHAR(20),
    PRIMARY KEY (document_id, user_id)
);
