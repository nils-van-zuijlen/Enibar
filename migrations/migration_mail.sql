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
	schedule_interval INTEGER UNSIGNED default 86400,
	schedule_day TINYINT default 0,
	filter INTEGER UNSIGNED,
	filter_value TEXT default "",
	sender varchar(255) default "",
	subject TEXT default "",
	message TEXT default ""
) ENGINE=InnoDB
