-- Multi-tenant invoicing system
CREATE TABLE tenants (
    id BIGSERIAL PRIMARY KEY,
    slug VARCHAR(80) UNIQUE NOT NULL,
    plan VARCHAR(40),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL REFERENCES tenants(id),
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);
CREATE INDEX idx_customers_tenant ON customers(tenant_id);

CREATE TABLE invoices (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    invoice_number VARCHAR(40) NOT NULL,
    amount_cents BIGINT NOT NULL,
    issued_at TIMESTAMPTZ DEFAULT NOW(),
    paid_at TIMESTAMPTZ,
    UNIQUE(tenant_id, invoice_number)
);
CREATE INDEX idx_invoices_customer ON invoices(customer_id);

CREATE TABLE invoice_lines (
    id BIGSERIAL PRIMARY KEY,
    invoice_id BIGINT NOT NULL,
    description TEXT,
    amount_cents BIGINT
);

CREATE TABLE payment_methods (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT,
    type VARCHAR(40),
    last4 CHAR(4),
    is_default BOOLEAN DEFAULT FALSE
);
