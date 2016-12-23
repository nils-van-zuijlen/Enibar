CREATE INDEX i_notes_firstname ON notes(firstname(10));
CREATE INDEX i_notes_lastname ON notes(lastname(10));
CREATE INDEX i_transactions_lastname ON transactions(lastname(10));
CREATE INDEX i_transactions_firstname ON transactions(firstname(10));
