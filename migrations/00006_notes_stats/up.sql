ALTER TABLE notes ADD COLUMN tot_cons DECIMAL(10, 2) DEFAULT 0 NOT NULL;
ALTER TABLE notes ADD COLUMN tot_refill DECIMAL(10, 2) DEFAULT 0 NOT NULL;

CREATE FUNCTION update_notes_stats()
RETURNS trigger AS
$BODY$
DECLARE
	diff INT := 0;
BEGIN
	diff:=NEW.note - OLD.note;

	IF diff > 0 THEN
		NEW.tot_cons = OLD.tot_cons + diff;
	ELSE
		NEW.tot_refill = OLD.tot_refill + diff;
	END IF;

	RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;

CREATE TRIGGER update_notes_stats_trigger
BEFORE UPDATE
ON notes
FOR EACH ROW
EXECUTE PROCEDURE update_notes_stats();

UPDATE notes SET tot_refill=s.tot_refill, tot_cons=s.tot_cons
FROM (SELECT notes.nickname, notes.firstname, notes.lastname,
SUM(CASE WHEN price>0 THEN price ELSE 0 END) as tot_refill,
SUM(CASE WHEN price<0 THEN price ELSE 0 END) AS tot_cons
FROM transactions JOIN notes ON
notes.firstname=transactions.firstname AND
notes.lastname=transactions.lastname
GROUP BY notes.nickname, notes.firstname, notes.lastname) s
WHERE notes.nickname=s.nickname;
