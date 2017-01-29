ALTER TABLE prices ADD COLUMN percentage DECIMAL(10, 2) DEFAULT 0 NOT NULL;
UPDATE prices INNER JOIN products ON prices.product=products.id SET prices.percentage=products.percentage;
ALTER TABLE products DROP COLUMN percentage;

