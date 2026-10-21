
-- Overall sales summary
SELECT
    COUNT(*) AS total_orders,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(total_amount), 2) AS total_sales
FROM orders;

-- Sales by category
SELECT
    category,
    COUNT(*) AS order_count,
    ROUND(SUM(total_amount), 2) AS category_sales
FROM orders
GROUP BY category
ORDER BY category_sales DESC;

-- Top 10 products by sales
SELECT
    product,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(total_amount), 2) AS total_sales
FROM orders
GROUP BY product
ORDER BY total_sales DESC
LIMIT 10;
