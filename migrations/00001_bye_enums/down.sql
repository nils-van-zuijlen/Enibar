CREATE TYPE promo AS ENUM('1A', '2A', '3A', '3S', '4A', '5A', 'Esiab', 'Externe', 'Ancien', 'Prof'); 
ALTER TABLE notes ALTER COLUMN promo SET DATA TYPE promo USING promo::promo;

CREATE TYPE schedule_unit AS ENUM('day', 'week', 'month');
ALTER TABLE scheduled_mails ALTER COLUMN schedule_unit DROP DEFAULT;
ALTER TABLE scheduled_mails ALTER COLUMN schedule_unit SET DATA TYPE schedule_unit USING schedule_unit::schedule_unit;
ALTER TABLE scheduled_mails ALTER COLUMN schedule_unit SET DEFAULT 'day';
