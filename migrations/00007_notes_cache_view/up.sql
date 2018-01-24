CREATE VIEW notes_cache AS
    SELECT notes.*, array_remove(array_agg(note_categories.*), NULL) AS categories, bool_or(note_categories.hidden) AS hidden FROM notes
    LEFT JOIN note_categories_assoc
    ON notes.id = note_categories_assoc.note
    LEFT JOIN note_categories
    ON note_categories.id = note_categories_assoc.category
    GROUP BY notes.id;
