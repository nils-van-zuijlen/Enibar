CREATE INDEX i_notes_firstname ON notes(firstname(10));
CREATE INDEX i_notes_lastname ON notes(lastname(10));
CREATE INDEX i_transactions_lastname ON transactions(lastname(10));
CREATE INDEX i_transactions_firstname ON transactions(firstname(10));

CREATE INDEX i_transactions_note ON transactions(note(10));
CREATE INDEX i_notes_nickname ON notes(nickname(10));
CREATE INDEX i_notes_stats_inscriptions ON notes(stats_inscription);


