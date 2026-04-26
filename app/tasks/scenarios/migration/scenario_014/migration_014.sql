-- Migration: enforce referential integrity that was previously app-layer only
-- Ticket: DATA-2890

ALTER TABLE invoices ADD CONSTRAINT fk_invoices_tenant
    FOREIGN KEY (tenant_id) REFERENCES tenants(id);

ALTER TABLE invoices ADD CONSTRAINT fk_invoices_customer
    FOREIGN KEY (customer_id) REFERENCES customers(id);

ALTER TABLE invoice_lines ADD CONSTRAINT fk_invoice_lines_invoice
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE;

ALTER TABLE payment_methods ADD CONSTRAINT fk_payment_methods_customer
    FOREIGN KEY (customer_id) REFERENCES customers(id);
