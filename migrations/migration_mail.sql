CREATE TABLE IF NOT EXISTS mail_models(
	name varchar(255) PRIMARY KEY,
	subject TEXT default "",
	message TEXT default "",
	filter INTEGER UNSIGNED,
	filter_value TEXT default ""
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS scheduled_mails(
	name VARCHAR(255) PRIMARY KEY,
	active BOOLEAN default FALSE,
	filter INTEGER UNSIGNED,
	filter_value TEXT default "",
	sender varchar(255) default "",
	subject TEXT default "",
	message TEXT default "",
	schedule_interval SMALLINT UNSIGNED default 1,
	schedule_unit enum('day', 'week', 'month') default "day",
	schedule_day TINYINT default 0,
	last_sent DATETIME
) ENGINE=InnoDB

