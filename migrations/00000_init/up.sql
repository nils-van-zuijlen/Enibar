CREATE TABLE admins(
    login VARCHAR PRIMARY KEY NOT NULL,
    password VARCHAR NOT NULL,
    manage_notes BOOLEAN DEFAULT FALSE NOT NULL,
    manage_users BOOLEAN DEFAULT FALSE NOT NULL,
    manage_products BOOLEAN DEFAULT FALSE NOT NULL
);

INSERT INTO admins(login, password, manage_notes, manage_users, manage_products) VALUES('admin', '$2a$04$vRE564ijZKQIm9RHiflh1u38ONpZNDc6UcFs9bJpVOV3xzUCqUvEa', TRUE, TRUE, TRUE);
CREATE TYPE promo AS ENUM('1A', '2A', '3A', '3S', '4A', '5A', 'Esiab', 'Externe', 'Ancien', 'Prof');

CREATE TABLE notes(
    id BIGSERIAL PRIMARY KEY ,
    nickname VARCHAR UNIQUE NOT NULL,
    lastname VARCHAR NOT NULL,
    firstname VARCHAR NOT NULL,
    mail VARCHAR NOT NULL,
    tel VARCHAR NOT NULL,
    birthdate INTEGER NOT NULL,
    promo promo NOT NULL,
    photo_path VARCHAR DEFAULT NULL,
    note DECIMAL(10, 2) DEFAULT 0 NOT NULL,
    overdraft_date DATE DEFAULT NULL,
    ecocups INTEGER DEFAULT 0 NOT NULL,
    last_agio DATE DEFAULT NULL,
    mails_inscription BOOLEAN DEFAULT TRUE NOT NULL,
    stats_inscription BOOLEAN DEFAULT TRUE NOT NULL,
    agios_inscription BOOLEAN DEFAULT TRUE NOT NULL,
    UNIQUE(lastname, firstname)
);
CREATE INDEX i_notes_nickname ON notes(nickname);
CREATE INDEX i_notes_stats_inscriptions ON notes(stats_inscription);
CREATE INDEX i_notes_firstname ON notes(firstname);
CREATE INDEX i_notes_lastname ON notes(lastname);

CREATE FUNCTION check_overdraft()
RETURNS trigger AS
$BODY$
BEGIN
    IF NEW.note < 0 AND NEW.overdraft_date IS NULL THEN
        NEW.overdraft_date = NOW();
        NEW.last_agio = NULL;
    ELSEIF NEW.note >= 0 AND NEW.overdraft_date IS NOT NULL THEN
        NEW.overdraft_date = NULL;
        NEW.last_agio = NULL;
    END IF;

    RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;

CREATE TRIGGER update_overdraft
BEFORE UPDATE
ON notes
FOR EACH ROW
EXECUTE PROCEDURE check_overdraft();

CREATE TABLE categories(
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    color VARCHAR DEFAULT '#FFFFFF' NOT NULL,
    alcoholic BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE TABLE products(
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    category INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    percentage DECIMAL(10, 2) DEFAULT 0 NOT NULL,
    UNIQUE (name, category)
);

CREATE TABLE price_description(
    id SERIAL PRIMARY KEY,
    label VARCHAR NOT NULL,
    category INTEGER,
    quantity INTEGER NOT NULL,
    UNIQUE (label, category),
    FOREIGN KEY (category) REFERENCES categories (id) ON DELETE CASCADE
);

CREATE TABLE prices(
    id SERIAL PRIMARY KEY,
    price_description INTEGER NOT NULL,
    product INTEGER NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (price_description) REFERENCES price_description (id) ON DELETE CASCADE,
    FOREIGN KEY (product) REFERENCES products (id) ON DELETE CASCADE
);

CREATE TABLE transactions(
    id SERIAL PRIMARY KEY,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    note VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    product VARCHAR NOT NULL,
    price_name VARCHAR NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    lastname VARCHAR NOT NULL,
    firstname VARCHAR NOT NULL,
    deletable BOOLEAN default TRUE NOT NULL,
    percentage DECIMAL(10, 2) NOT NULL,
    liquid_quantity INTEGER NOT NULL,
    note_id INTEGER DEFAULT NULL
);
CREATE INDEX i_transactions_lastname ON transactions(lastname);
CREATE INDEX i_transactions_firstname ON transactions(firstname);
CREATE INDEX i_transactions_note ON transactions(note);

CREATE TABLE panels(
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE,
    hidden BOOLEAN DEFAULT FALSE
);

CREATE TABLE panel_content(
    panel_id INTEGER,
    product_id INTEGER,
    PRIMARY KEY(panel_id, product_id),
    FOREIGN KEY (panel_id) REFERENCES panels(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE mail_models(
    name varchar(255) PRIMARY KEY,
    subject TEXT default '' NOT NULL,
    message TEXT default '' NOT NULL,
    filter INTEGER NOT NULL,
    filter_value TEXT default '' NOT NULL
);

CREATE TYPE schedule_unit AS ENUM('day', 'week', 'month');

CREATE TABLE scheduled_mails(
    name VARCHAR PRIMARY KEY,
    active BOOLEAN default FALSE NOT NULL,
    filter INTEGER NOT NULL,
    filter_value TEXT default '' NOT NULL,
    sender varchar(255) default '' NOT NULL,
    subject TEXT default '' NOT NULL,
    message TEXT default '' NOT NULL,
    schedule_interval SMALLINT default 1 NOT NULL,
    schedule_unit schedule_unit default 'day' NOT NULL,
    schedule_day SMALLINT default 0 NOT NULL,
    last_sent DATE
);

CREATE TABLE note_categories(
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    hidden BOOLEAN DEFAULT FALSE NOT NULL,
    protected BOOLEAN DEFAULT FALSE NOT NULL
);

INSERT INTO note_categories(name, hidden, protected) VALUES ('Non Cotiz', TRUE, TRUE);

CREATE TABLE note_categories_assoc(
    id SERIAL PRIMARY KEY,
    note INTEGER NOT NULL,
    category INTEGER NOT NULL,
    UNIQUE(note, category),
    FOREIGN KEY (note) REFERENCES notes (id) ON DELETE CASCADE,
    FOREIGN KEY (category) REFERENCES note_categories (id) ON DELETE CASCADE
);
