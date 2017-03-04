ALTER TABLE notes ALTER COLUMN promo SET DATA TYPE VARCHAR;
ALTER TABLE notes ADD CONSTRAINT promochk CHECK(promo in ('1A', '2A', '3A', '3S', '4A', '5A', 'Externe', 'Esiab', 'Ancien'));
DROP TYPE promo;

ALTER TABLE scheduled_mails ALTER COLUMN schedule_unit SET DATA TYPE VARCHAR;
ALTER TABLE scheduled_mails ALTER COLUMN schedule_unit SET DEFAULT 'day';
ALTER TABLE scheduled_mails ADD CONSTRAINT schedule_unitchk CHECK(schedule_unit in ('day', 'week', 'month'));
DROP TYPE schedule_unit;

