-- Migration: introduce async balance maintenance via trigger
-- Ticket: FIN-9914
-- Goal: simplify application code by computing balance from ledger asynchronously

CREATE OR REPLACE FUNCTION update_account_balance() RETURNS TRIGGER AS $$
BEGIN
    UPDATE accounts
       SET balance_cents = balance_cents + NEW.credit_cents - NEW.debit_cents,
           available_cents = available_cents + NEW.credit_cents - NEW.debit_cents
     WHERE id = NEW.account_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_ledger_balance
    AFTER INSERT ON ledger_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_account_balance();

ALTER TABLE accounts DROP CONSTRAINT positive_balance;
