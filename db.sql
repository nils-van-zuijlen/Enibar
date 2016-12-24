/*

Copyright (C) 2014-2016 Bastien Orivel <b2orivel@enib.fr>
Copyright (C) 2014-2016 Arnaud Levaufre <a2levauf@enib.fr>

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
	manage_notes BOOLEAN DEFAULT FALSE NOT NULL,
	manage_users BOOLEAN DEFAULT FALSE NOT NULL,
	manage_products BOOLEAN DEFAULT FALSE NOT NULL
) ENGINE=InnoDB;

INSERT INTO admins(login, password, manage_notes, manage_users, manage_products) VALUES("admin", "$2a$12$grLadAuopGdXxA7wEIehlO4BpMHTpJFweL3zJAHGaYFOIw1Gp.U5O", TRUE, TRUE, TRUE);

CREATE TABLE IF NOT EXISTS notes(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	nickname VARCHAR(127) UNIQUE NOT NULL,
	lastname VARCHAR(127) NOT NULL,
	firstname VARCHAR(127) NOT NULL,
	mail VARCHAR(255) NOT NULL,
	tel VARCHAR(32) NOT NULL,
	birthdate INTEGER UNSIGNED NOT NULL,
	promo ENUM('1A', '2A', '3A', '3S', '4A', '5A', 'Esiab', 'Externe', 'Ancien', 'Prof') NOT NULL,
	photo_path VARCHAR(255) DEFAULT NULL,
	note DECIMAL(10, 2) DEFAULT 0 NOT NULL,
	overdraft_date DATE DEFAULT NULL,
	last_agio DATE DEFAULT NULL,
	ecocups INTEGER UNSIGNED DEFAULT 0 NOT NULL,
	mails_inscription BOOLEAN DEFAULT TRUE NOT NULL,
	stats_inscription BOOLEAN DEFAULT TRUE NOT NULL,
	UNIQUE(lastname, firstname)
) ENGINE=InnoDB;
CREATE INDEX i_notes_nickname ON notes(nickname(10));
CREATE INDEX i_notes_stats_inscriptions ON notes(stats_inscription);
CREATE INDEX i_notes_firstname ON notes(firstname(10));
CREATE INDEX i_notes_lastname ON notes(lastname(10));

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
	color VARCHAR(32) DEFAULT "#FFFFFF" NOT NULL,
	alcoholic BOOLEAN DEFAULT FALSE NOT NULL
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
	label VARCHAR(127) NOT NULL,
	category INTEGER UNSIGNED,
    quantity INTEGER UNSIGNED NOT NULL,
	UNIQUE (label, category),
	FOREIGN KEY (category) REFERENCES categories (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS prices(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	price_description INTEGER UNSIGNED,
	product INTEGER UNSIGNED,
	value DECIMAL(10,2) NOT NULL,
    percentage DECIMAL(10, 2) DEFAULT 0 NOT NULL,
	FOREIGN KEY (price_description) REFERENCES price_description (id) ON DELETE CASCADE,
	FOREIGN KEY (product) REFERENCES products (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS transactions(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	date DATETIME NOT NULL,
	note VARCHAR(127) NOT NULL,
	lastname VARCHAR(127) NOT NULL,
	firstname VARCHAR(127) NOT NULL,
	category VARCHAR(127) NOT NULL,
	product VARCHAR(127) NOT NULL,
	price_name VARCHAR(127) NOT NULL,
	price DECIMAL(10, 2) NOT NULL,
	quantity INTEGER UNSIGNED NOT NULL,
    liquid_quantity INTEGER UNSIGNED NOT NULL,
    percentage DECIMAL(10, 2) NOT NULL,
	deletable BOOLEAN default TRUE NOT NULL
) ENGINE=InnoDB;
CREATE INDEX i_transactions_lastname ON transactions(lastname(10));
CREATE INDEX i_transactions_firstname ON transactions(firstname(10));
CREATE INDEX i_transactions_note ON transactions(note(10));

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
	subject TEXT default "" NOT NULL,
	message TEXT default "" NOT NULL,
	filter INTEGER UNSIGNED NOT NULL,
	filter_value TEXT default "" NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS scheduled_mails(
	name VARCHAR(255) PRIMARY KEY,
	active BOOLEAN default FALSE NOT NULL,
	filter INTEGER UNSIGNED NOT NULL,
	filter_value TEXT default "" NOT NULL,
	sender varchar(255) default "" NOT NULL,
	subject TEXT default "" NOT NULL,
	message TEXT default "" NOT NULL,
	schedule_interval SMALLINT UNSIGNED default 1 NOT NULL,
	schedule_unit enum('day', 'week', 'month') default "day" NOT NULL,
	schedule_day TINYINT default 0 NOT NULL,
	last_sent DATE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS note_categories(
    id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    hidden BOOLEAN DEFAULT FALSE NOT NULL,
    protected BOOLEAN DEFAULT FALSE NOT NULL
) ENGINE=InnoDB;

INSERT INTO `note_categories` (name, hidden, protected) VALUES ('Non Cotiz', 1, 1);

CREATE TABLE IF NOT EXISTS note_categories_assoc(
    id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    note INTEGER UNSIGNED NOT NULL,
    category INTEGER UNSIGNED NOT NULL,
    UNIQUE(note, category),
    FOREIGN KEY (note) REFERENCES notes (id) ON DELETE CASCADE,
    FOREIGN KEY (category) REFERENCES note_categories (id) ON DELETE CASCADE
) ENGINE=InnoDB;
