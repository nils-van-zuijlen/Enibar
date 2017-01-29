ALTER TABLE products ADD COLUMN percentage DECIMAL(10, 2) DEFAULT 0 NOT NULL;
UPDATE products AS p INNER JOIN (SELECT product, MAX(percentage) mper FROM prices GROUP BY product) i ON p.id=i.product SET p.percentage=i.mper;
ALTER TABLE prices DROP COLUMN percentage;
