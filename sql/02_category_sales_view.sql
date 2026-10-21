
-- Create a reusable category sales reporting view
CREATE OR REPLACE VIEW category_sales_summary AS
SELECT
    category,
    COUNT(*) AS order_count,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(total_amount), 2) AS total_sales
FROM orders
GROUP BY category;

-- Query the reporting view
SELECT *
FROM category_sales_summary
ORDER BY total_sales DESC;
