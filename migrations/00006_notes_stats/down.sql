ALTER TABLE notes DROP COLUMN tot_refill;
ALTER TABLE notes DROP COLUMN tot_cons;
DROP TRIGGER update_notes_stats_trigger ON notes;
DROP FUNCTION update_notes_stats;

