/*

Copyright (C) 2014-2015 Bastien Orivel <b2orivel@enib.fr>
Copyright (C) 2014-2015 Arnaud Levaufre <a2levauf@enib.fr>

This file is part of Enibar.

Enibar is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Enibar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Enibar.  If not, see <http://www.gnu.org/licenses/>.

*/

DROP DATABASE IF EXISTS enibar;
CREATE DATABASE enibar;
USE enibar;

CREATE TABLE IF NOT EXISTS admins(
	login VARCHAR(127) PRIMARY KEY NOT NULL,
	password VARCHAR(127) NOT NULL,
	manage_notes BOOLEAN DEFAULT FALSE,
	manage_users BOOLEAN DEFAULT FALSE,
	manage_products BOOLEAN DEFAULT FALSE
) ENGINE=InnoDB;

INSERT INTO admins(login, password, manage_notes, manage_users, manage_products) VALUES("admin", "$2a$12$grLadAuopGdXxA7wEIehlO4BpMHTpJFweL3zJAHGaYFOIw1Gp.U5O", TRUE, TRUE, TRUE);

CREATE TABLE IF NOT EXISTS notes(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	nickname VARCHAR(127) UNIQUE NOT NULL,
	lastname VARCHAR(127),
	firstname VARCHAR(127),
	mail VARCHAR(255),
	tel VARCHAR(32),
	birthdate INTEGER UNSIGNED,
	promo ENUM('1A', '2A', '3A', '3S', '4A', '5A', 'Esiab', 'Externe', 'Ancien', 'Prof'),
	photo_path VARCHAR(255) DEFAULT NULL,
	note DECIMAL(10, 2) DEFAULT 0,
	overdraft_date DATE DEFAULT NULL,
	last_agio DATE DEFAULT NULL,
	ecocups INTEGER UNSIGNED DEFAULT 0,
	hidden BOOLEAN DEFAULT 0,
	mails_inscription BOOLEAN DEFAULT TRUE,
	stats_inscription BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

delimiter //
CREATE TRIGGER update_overdraft BEFORE UPDATE ON notes
FOR EACH ROW
BEGIN
	IF NEW.note < 0 AND NEW.overdraft_date IS NULL THEN
		SET NEW.overdraft_date = NOW();
		SET NEW.last_agio = NULL;
	ELSEIF NEW.note >= 0 AND NEW.overdraft_date IS NOT NULL THEN
		SET NEW.overdraft_date = NULL;
		SET NEW.last_agio = NULL;
	END IF;
END;//
delimiter ;



CREATE TABLE IF NOT EXISTS categories(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(127) UNIQUE NOT NULL,
	color VARCHAR(32) DEFAULT "#FFFFFF",
	alcoholic BOOLEAN DEFAULT FALSE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(127) NOT NULL,
	category INTEGER UNSIGNED,
	UNIQUE (name, category),
	FOREIGN KEY (`category`) REFERENCES categories(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS price_description(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	label VARCHAR(127),
	category INTEGER UNSIGNED,
    quantity INTEGER UNSIGNED,
	UNIQUE (label, category),
	FOREIGN KEY (category) REFERENCES categories (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS prices(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	price_description INTEGER UNSIGNED,
	product INTEGER UNSIGNED,
	value DECIMAL(10,2),
    percentage DECIMAL(10, 2) DEFAULT 0,
	FOREIGN KEY (price_description) REFERENCES price_description (id) ON DELETE CASCADE,
	FOREIGN KEY (product) REFERENCES products (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS barcodes(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	price_id INTEGER UNSIGNED,
	value VARCHAR(127) DEFAULT "" UNIQUE,
	FOREIGN KEY (price_id) REFERENCES prices(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS transactions(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	date DATETIME,
	note VARCHAR(127),
	lastname VARCHAR(127),
	firstname VARCHAR(127),
	category VARCHAR(127),
	product VARCHAR(127),
	price_name VARCHAR(127),
	price DECIMAL(10, 2),
	quantity INTEGER UNSIGNED,
    liquid_quantity INTEGER UNSIGNED,
    percentage DECIMAL(10, 2),
	deletable BOOLEAN default TRUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS panels(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(255) UNIQUE,
	hidden BOOLEAN DEFAULT FALSE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS panel_content(
	panel_id INTEGER UNSIGNED,
	product_id INTEGER UNSIGNED,
	PRIMARY KEY(panel_id, product_id),
	FOREIGN KEY (panel_id) REFERENCES panels(id) ON DELETE CASCADE,
	FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

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
	last_sent DATE
) ENGINE=InnoDB

