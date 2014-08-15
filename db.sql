/*

Copyright (C) 2014 Bastien Orivel <b2orivel@enib.fr>
Copyright (C) 2014 Arnaud Levaufre <a2levauf@enib.fr>

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

INSERT INTO admins(login, password) VALUES("admin", "$2a$12$grLadAuopGdXxA7wEIehlO4BpMHTpJFweL3zJAHGaYFOIw1Gp.U5O");


CREATE TABLE IF NOT EXISTS notes(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	nickname VARCHAR(127) UNIQUE,
	surname VARCHAR(127),
	firstname VARCHAR(127),
	mail VARCHAR(255),
	tel VARCHAR(32),
	birthdate INTEGER UNSIGNED,
	promo ENUM('1A', '2A', '3A', '3S', '4A', '5A', 'Esiab', 'Externe', 'Ancien', 'Prof'),
	photo_path VARCHAR(255) DEFAULT NULL,
	note FLOAT DEFAULT 0,
	overdraft_time INTEGER UNSIGNED DEFAULT NULL,
	ecocups INTEGER UNSIGNED DEFAULT 0,
	hidden BOOLEAN DEFAULT 0
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS categories(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(127) UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(127),
	category INTEGER UNSIGNED,
	FOREIGN KEY (`category`) REFERENCES categories(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS price_description(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	label VARCHAR(127),
	category INTEGER UNSIGNED,
	FOREIGN KEY (category) REFERENCES categories (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS prices(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	price_description INTEGER UNSIGNED,
	product INTEGER UNSIGNED,
	value FLOAT UNSIGNED,
	FOREIGN KEY (price_description) REFERENCES price_description (id) ON DELETE CASCADE,
	FOREIGN KEY (product) REFERENCES products (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS transactions_history(
	id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	note_id INTEGER UNSIGNED,
	conso_id INTEGER UNSIGNED,
	quantity INTEGER UNSIGNED
) ENGINE=InnoDB;

