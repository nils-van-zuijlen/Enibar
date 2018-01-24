ALTER TABLE notes ADD COLUMN tot_cons DECIMAL(10, 2) DEFAULT 0 NOT NULL;
ALTER TABLE notes ADD COLUMN tot_refill DECIMAL(10, 2) DEFAULT 0 NOT NULL;

CREATE FUNCTION on_transaction()
RETURNS trigger AS
$BODY$
BEGIN
    UPDATE notes SET
        note=note+NEW.price,
        tot_cons=(CASE WHEN NEW.price < 0 THEN tot_cons + NEW.price ELSE tot_cons END),
        tot_refill=(CASE WHEN NEW.price > 0 THEN tot_refill + NEW.price ELSE tot_refill END)
    WHERE notes.firstname=NEW.firstname AND notes.lastname=NEW.lastname;

    RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;

CREATE FUNCTION on_transaction_deletion()
RETURNS trigger AS
$BODY$
BEGIN
    UPDATE notes SET
        note=note-OLD.price,
        tot_cons=(CASE WHEN OLD.price < 0 THEN tot_cons - OLD.price ELSE tot_cons END),
        tot_refill=(CASE WHEN OLD.price > 0 THEN tot_refill - OLD.price ELSE tot_refill END)
    WHERE notes.firstname=OLD.firstname AND notes.lastname=OLD.lastname;
    RETURN OLD;
END;
$BODY$ LANGUAGE plpgsql;

CREATE FUNCTION on_transaction_update()
RETURNS trigger AS
$BODY$
DECLARE
    diff DECIMAL(10, 2) := 0;
BEGIN
    diff = OLD.price - NEW.price;
    UPDATE notes SET
        note=note-diff,
        tot_cons=(CASE WHEN diff < 0 THEN tot_cons - diff ELSE tot_cons END),
        tot_refill=(CASE WHEN diff > 0 THEN tot_refill - diff ELSE tot_refill END)
    WHERE notes.firstname=NEW.firstname AND notes.lastname=NEW.lastname;

    RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;

UPDATE notes SET tot_refill=s.tot_refill, tot_cons=s.tot_cons
FROM (SELECT notes.nickname, notes.firstname, notes.lastname,
SUM(CASE WHEN price>0 THEN price ELSE 0 END) as tot_refill,
SUM(CASE WHEN price<0 THEN price ELSE 0 END) AS tot_cons
FROM transactions JOIN notes ON
notes.firstname=transactions.firstname AND
notes.lastname=transactions.lastname
GROUP BY notes.nickname, notes.firstname, notes.lastname) s
WHERE notes.firstname=s.firstname AND notes.lastname=s.lastname;

CREATE TRIGGER on_transaction_trigger
BEFORE INSERT ON transactions
FOR EACH ROW EXECUTE PROCEDURE on_transaction();

CREATE TRIGGER on_transaction_deletion_trigger
BEFORE DELETE ON transactions
FOR EACH ROW EXECUTE PROCEDURE on_transaction_deletion();

CREATE TRIGGER on_transaction_update_trigger
BEFORE UPDATE ON transactions
FOR EACH ROW EXECUTE PROCEDURE on_transaction_update();

