ALTER TABLE notes DROP COLUMN tot_refill;
ALTER TABLE notes DROP COLUMN tot_cons;
DROP TRIGGER on_transaction_trigger ON transactions;
DROP FUNCTION on_transaction;
DROP TRIGGER on_transaction_deletion_trigger ON transactions;
DROP FUNCTION on_transaction_deletion;
DROP TRIGGER on_transaction_update_trigger ON transactions;
DROP FUNCTION on_transaction_update;

