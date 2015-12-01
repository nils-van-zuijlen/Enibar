ALTER TABLE prices ADD COLUMN percentage DECIMAL(10, 2) NOT NULL DEFAULT 0;
ALTER TABLE price_description ADD COLUMN quantity INTEGER NOT NULL DEFAULT 0;
ALTER TABLE transactions ADD percentage DECIMAL(10, 2);
ALTER TABLE transactions ADD liquid_quantity INTEGER;


