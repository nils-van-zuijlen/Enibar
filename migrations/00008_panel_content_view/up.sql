CREATE TYPE panel_product AS (id INT, name VARCHAR, description VARCHAR, price DECIMAL(10,2), percentage DECIMAL(10, 2));
CREATE VIEW panels_content AS
SELECT panels.name AS panel_name, array_agg((products.id, products.name, price_description.label, prices.value, products.percentage)::panel_product) AS panel_products, categories.id AS category_id, categories.name AS category_name, categories.alcoholic AS category_alcoholic, categories.color AS category_color FROM panels
INNER JOIN panel_content
    ON panel_content.panel_id = panels.id
INNER JOIN products
    ON products.id = panel_content.product_id
INNER JOIN price_description
    ON products.category = price_description.category
INNER JOIN categories
    ON categories.id = price_description.category
INNER JOIN prices
    ON prices.product = products.id AND price_description.id = prices.price_description
WHERE panels.hidden = FALSE AND prices.value != 0
GROUP BY panels.id, categories.id, products.id;
