-- question: Calculate the 7-day moving average of sales for each product, some products may have 0 sales on some dates.
-- table: sales
-- schema: sale_id, product_id, sale_date (dd-mm-yyyy), amount

WITH allProductIds AS (
    SELECT DISTINCT product_id
    FROM sales
),
all_sale_dates AS (
    SELECT generate_series(
        (SELECT MIN(sale_date) FROM sales),
        (SELECT MAX(sale_date) FROM sales),
        INTERVAL '1 day'
    ) AS sale_date
),
sales_filled AS (
    SELECT
        p.product_id,
        d.sale_date,
        COALESCE(s.total_amount, 0) AS total_amount
    FROM
        allProductIds p
    CROSS JOIN
        all_sale_dates d
    LEFT JOIN (
        SELECT
            product_id,
            sale_date,
            SUM(amount) AS total_amount
        FROM
            sales
        GROUP BY
            product_id, sale_date
    ) s ON p.product_id = s.product_id AND d.sale_date = s.sale_date
),
final_res AS (
    SELECT
        product_id,
        sale_date,
        AVG(total_amount) OVER(
            PARTITION BY product_id
            ORDER BY sale_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS moving_avg_7d
    FROM
        sales_filled
)
SELECT * FROM final_res
;