CREATE TABLE IF NOT EXISTS mail_models(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	subject TEXT default "",
	message TEXT default "",
	filter INTEGER UNSIGNED,
	filter_value TEXT default ""
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS mail_scheduler(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	model INTEGER UNSIGNED,
	last INTEGER default NULL,
	send_interval INTEGER UNSIGNED,
	filter INTEGER UNSIGNED,
	filter_value TEXT default ""
) ENGINE=InnoDB;
